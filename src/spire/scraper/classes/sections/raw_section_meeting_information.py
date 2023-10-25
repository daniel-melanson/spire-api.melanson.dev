import logging
import re
from datetime import date, time
from typing import Any, Optional

from spire.models import (
    Instructor,
    Section,
    SectionMeetingDates,
    SectionMeetingInformation,
    SectionMeetingSchedule,
)
from spire.scraper.classes.buildings.raw_building import get_raw_building_room
from spire.scraper.classes.shared import RawField, RawObject
from spire.scraper.shared import assert_match

log = logging.getLogger(__name__)


class RawInstructor(RawObject):
    name: str
    email: Optional[str]

    def __init__(self, name: str, email=None) -> None:
        self.name = name
        self.email = email

        super().__init__(
            Instructor,
            fields=[
                RawField(
                    "name",
                    min_len=4,
                    normalizers=[lambda x: "Staff" if x in ("staff", "TBD") else x],
                ),
                RawField("email"),
            ],
        )

    def push(self):
        if self.email:
            try:
                staff = Instructor.objects.get(name=self.name)

                if staff.email is None:
                    staff.email = self.email
                    staff.save()

                created = False
            except Instructor.DoesNotExist:
                staff, created = Instructor.objects.get_or_create(
                    email=self.email, defaults={"name": self.name}
                )
        else:
            staff, created = Instructor.objects.get_or_create(name=self.name)

        log.info(
            "%s instructor %s from %s", "Created" if created else "Updated", staff, self
        )

        return staff


def as_time(time_str, meridiem):
    [hour, minute] = time_str.split(":")

    hour = int(hour)
    minute = int(minute)

    if hour == 12 and meridiem == "AM":
        hour = 0
    elif hour != 12 and meridiem == "PM":
        hour += 12

    return time(hour=hour, minute=minute)


class RawSectionMeetingDates(RawObject):
    def __init__(self, dates: str) -> None:
        match = assert_match(r"^(?P<start>\S+) - (?P<end>\S+)$", dates.strip())

        date_pattern = r"^(\d{2})/(\d{2})/(\d{4})$"

        start_match = assert_match(date_pattern, match.group("start"))
        end_match = assert_match(date_pattern, match.group("end"))

        start_kwargs = {}
        end_kwargs = {}
        for i, unit in enumerate(["month", "day", "year"]):
            start_kwargs[unit] = int(start_match.group(i + 1))
            end_kwargs[unit] = int(end_match.group(i + 1))

        self.start = date(**start_kwargs)
        self.end = date(**end_kwargs)

        super().__init__(
            SectionMeetingDates, None, [RawField("start"), RawField("end")]
        )


class RawSectionMeetingSchedule(RawObject):
    def __init__(self, days_and_times) -> None:
        m = assert_match(
            r"(?P<days>(Mo|Tu|We|Th|Fr|Sa|Su){1,6}) (?P<start_time>\d\d?:\d\d)(?P<start_m>AM|PM) - (?P<end_time>\d\d?:\d\d)(?P<end_m>AM|PM)",
            days_and_times,
        )

        self.days = []

        days = m.group("days")

        for day in (
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ):
            if day[:2] in days:
                self.days.append(day)

        self.start_time = as_time(m.group("start_time"), m.group("start_m"))
        self.end_time = as_time(m.group("end_time"), m.group("end_m"))

        super().__init__(
            SectionMeetingSchedule,
            fields=[
                RawField("days", min_len=1),
                RawField("start_time"),
                RawField("end_time"),
            ],
        )


class RawSectionMeetingInformation(RawObject):
    def __init__(self, spire_id: str, table: dict[str, Any]) -> None:
        self.room = get_raw_building_room(table["room"])
        log.debug("Scraped building room:\n%s", self.room)

        self.room_raw = table["room"]

        self.instructors: list[RawInstructor] = table["instructors"]
        assert len(self.instructors) > 0

        days_and_times = table["days_and_times"]
        log.debug("Processing date and time: %s", days_and_times)
        if days_and_times.lower() not in ("tba", "tba 1:00am - 1:00am", "n/a"):
            self.schedule = RawSectionMeetingSchedule(days_and_times)
            log.debug("Scraped meeting schedule:\n%s", self.schedule)

        if days_and_times.lower() not in ("tba", "n/a"):
            self.meeting_dates = RawSectionMeetingDates(table["meeting_dates"])
            log.debug("Scraped meeting_dates:\n%s", self.meeting_dates)

        super().__init__(
            SectionMeetingInformation,
            spire_id,
            [RawField("room"), RawField("room_raw"), RawField("instructors")],
        )

    def push(self, section: Section):
        mi = SectionMeetingInformation.objects.create(
            section=section, room=self.room.push(), room_raw=self.room_raw
        )
        log.info("Created SectionMeetingInformation: %s", mi)

        if hasattr(self, "schedule"):
            self.schedule.push(meeting_information=mi)

        if hasattr(self, "meeting_dates"):
            self.meeting_dates.push(meeting_information=mi)

        new_instructors: list[RawInstructor] = []
        for r_staff in self.instructors:
            new_instructors.append(r_staff.push())

        mi.instructors.set(new_instructors)

        return mi
