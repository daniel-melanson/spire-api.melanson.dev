from typing import Optional

from spire.regexp import COURSE_ID_REGEXP, SECTION_ID_REGEXP, TERM_REGEXP
from spire.scraper.normalizers.shared import SpireField, SpireObject
from spire.scraper.normalizers.SpireMeetingInformation import SpireMeetingInformation


class SpireSection(SpireObject):
    course_id: str
    term: str
    id: str
    details: dict[str, str]
    meeting_information: SpireMeetingInformation
    restrictions: Optional[dict[str, str]]
    availability: dict[str, str]
    description: Optional[str]
    overview: Optional[str]

    def __init__(
        self,
        course_id: str,
        term: str,
        id: str,
        details: dict[str, str],
        meeting_information: SpireMeetingInformation,
        restrictions: Optional[dict[str, str]],
        availability: dict[str, str],
        description: Optional[str],
        overview: Optional[str],
    ):
        self.course_id = course_id
        self.term = term
        self.id = id
        self.details = details
        self.meeting_information = meeting_information
        self.restrictions = restrictions
        self.availability = availability
        self.description = description
        self.overview = overview

        super().__init__(
            "SpireSection",
            (
                SpireField("course_id", re=COURSE_ID_REGEXP),
                SpireField("term", re=TERM_REGEXP),
                SpireField("id", re=SECTION_ID_REGEXP),
                SpireField("details"),
                SpireField("meeting_information"),
                SpireField("availability"),
                SpireField("description"),
                SpireField("overview"),
            ),
        )
