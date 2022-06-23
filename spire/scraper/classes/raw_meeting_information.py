from typing import Any, NamedTuple, Optional

from spire.models import MeetingInformation, Section, Staff

from .shared import RawDictionary, RawField, RawObject


class RawStaff(RawObject):
    name: str
    email: Optional[str]

    def __init__(self, name: str, email: Optional[str]) -> None:
        self.name = name
        self.email = email

        super().__init__(Staff, RawField("name"), RawField("email"))

    def push(self):
        if self.email:
            staff = super().push(email=self.email)
        elif self.name.lower() == "staff":
            staff = Staff.objects.get_or_create(name="Staff")
        else:
            possible_instructors = Staff.objects.filter(name=self.name)

            if len(possible_instructors) == 0:
                staff = Staff.objects.create(name=self.name)
            else:
                assert False # TODO

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
            RawField("days_and_times"),
            RawField("instructors"),
            RawField("room"),
            RawField("meeting_dates"),
            pk="section_id",
        )

    def push(self, section: Section):
        mi = MeetingInformation.objects.create(section=section, defaults=super().get_model_defaults())

        new_instructors = []
        for r_staff in self.instructors:
            new_instructors.append(r_staff.push())

        self.instructors.set(new_instructors)

        return mi
