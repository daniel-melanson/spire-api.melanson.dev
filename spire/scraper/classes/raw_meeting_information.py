from typing import Any, Optional

from spire.models import Instructor, MeetingInformation, Section

from .shared import RawDictionary, RawField, RawObject


class RawInstructor(RawObject):
    name: str
    email: Optional[str]

    def __init__(self, name: str, email=None) -> None:
        self.name = name
        self.email = email

        super().__init__(
            Instructor,
            RawField("name", len=(1, 64), normalizers=[lambda x: "Staff" if x in ("staff", "TBD") else x]),
            RawField("email"),
        )

    def push(self):
        if self.email:
            staff = super().push(email=self.email)
        else:
            staff, _ = Instructor.objects.get_or_create(name=self.name)

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
            RawField("days_and_times", len=(1, 64)),
            RawField("instructors", len=(1, 10)),
            RawField("room", len=(1, 64)),
            RawField("meeting_dates", len=(1, 64)),
            pk="section_id",
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
