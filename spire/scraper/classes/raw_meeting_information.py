from typing import NamedTuple, Optional

from spire.models import MeetingInformation, Staff

from .shared import RawDictionary, RawField, RawObject


class RawStaff(RawObject):
    name: str
    email: Optional[str]

    def __init__(self, name: str, email: Optional[str]) -> None:
        super().__init__(Staff, RawField("name"), RawField("email"))

    def push():
        pass



class RawMeetingInformation(RawDictionary):
    days_and_times: str
    instructors: list[RawStaff]
    room: str
    meeting_dates: str

    def __init__(self, table: dict[str, str]) -> None:
        super().__init__(
            MeetingInformation,
            table,
            RawField("days_and_times"),
            RawField("instructors"),
            RawField("room"),
            RawField("meeting_dates"),
            pk="section",
        )
