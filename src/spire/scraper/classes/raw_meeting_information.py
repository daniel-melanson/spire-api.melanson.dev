import logging
import re
from datetime import time
from typing import Optional

from spire.models import Instructor, MeetingInformation, MeetingSchedule, Section
from spire.scraper.classes.shared import RawDictionary, RawField, RawObject

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
                RawField("name", min_len=4, normalizers=[lambda x: "Staff" if x in ("staff", "TBD") else x]),
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

        log.info("%s instructor %s from %s", "Created" if created else "Updated", staff, self)

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


class RawMeetingSchedule(RawObject):
    def __init__(self, days_and_times) -> None:
        m = re.fullmatch(
            r"(?P<days>(Mo|Tu|We|Th|Fr|Sa|Su){1,6}) (?P<start_time>\d\d?:\d\d)(?P<start_m>AM|PM) - (?P<end_time>\d\d?:\d\d)(?P<end_m>AM|PM)",
            days_and_times,
        )
        assert m

        self.days = []

        days = m.group("days")

        for day in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"):
            if day[:2] in days:
                self.days.append(day)

        self.start_time = as_time(m.group("start_time"), m.group("start_m"))
        self.end_time = as_time(m.group("end_time"), m.group("end_m"))

        super().__init__(
            MeetingSchedule,
            [
                RawField("days", min_len=1),
                RawField("start_time"),
                RawField("end_time"),
            ],
            "meeting_information_id",
        )


class RawMeetingInformation(RawDictionary):
    def __init__(self, section_id: str, table: dict[str, str]) -> None:
        self.section_id = section_id

        days_and_times = table["days_and_times"]
        del table["days_and_times"]
        if days_and_times not in ("TBA", "TBA 1:00AM - 1:00AM"):
            self.schedule = RawMeetingSchedule(days_and_times)
            log.info("Scraped meeting schedule:\n%s", self.schedule)

        super().__init__(
            MeetingInformation,
            table,
            pk="section_id",
            fields=[
                RawField("instructors", min_len=1),
                RawField("room", min_len=1),
                RawField("meeting_dates", min_len=1),
            ],
        )

    def push(self, section: Section):
        mi = MeetingInformation.objects.create(
            section=section,
            room=self.room,
            meeting_dates=self.meeting_dates,
        )

        if hasattr(self, "schedule"):
            self.schedule.push(meeting_information=mi)

        new_instructors = []
        for r_staff in self.instructors:
            new_instructors.append(r_staff.push())

        mi.instructors.set(new_instructors)

        return mi
