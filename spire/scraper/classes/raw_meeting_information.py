import logging
from typing import Any, Optional

from spire.models import Instructor, MeetingInformation, Section

from .shared import RawDictionary, RawField, RawObject

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
                RawField("name", min_len=1, normalizers=[lambda x: "Staff" if x in ("staff", "TBD") else x]),
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


class RawMeetingInformation(RawDictionary):
    days_and_times: str
    instructors: Any
    room: str
    meeting_dates: str

    def __init__(self, section_id: str, table: dict[str, str]) -> None:
        self.section_id = section_id

        super().__init__(
            MeetingInformation,
            table,
            pk="section_id",
            fields=[
                RawField("days_and_times", min_len=1),
                RawField("instructors", min_len=1),
                RawField("room", min_len=1),
                RawField("meeting_dates", min_len=1),
            ],
        )

    def push(self, section: Section):
        mi = MeetingInformation.objects.create(
            section=section,
            days_and_times=self.days_and_times,
            room=self.room,
            meeting_dates=self.meeting_dates,
        )

        new_instructors = []
        for r_staff in self.instructors:
            new_instructors.append(r_staff.push())

        mi.instructors.set(new_instructors)

        return mi
