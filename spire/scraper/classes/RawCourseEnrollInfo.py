from spire.scraper.classes.shared import RawObject


class RawCourseEnrollInfo(RawObject):
    def __init__(self, table: dict[str, str]) -> None:
        super().__init__("SpireCourseEnrollInfo")
