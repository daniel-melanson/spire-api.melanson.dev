from spire.scraper.normalizers.shared import SpireObject
from spire.scraper.normalizers.SpireStaff import SpireStaff


class SpireMeetingInformation:
    days_and_times: str
    room: str
    instructors: list[SpireStaff]
    meeting_dates: str

    def __init__(self, days_and_times: str, room: str, instructors: list[SpireStaff]):
        pass
