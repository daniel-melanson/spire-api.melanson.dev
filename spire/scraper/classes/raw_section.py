import logging
from typing import Optional

from django.db import DatabaseError, transaction
from django.utils import timezone

from spire.models import MeetingInformation, Section
from spire.patterns import COURSE_ID_REGEXP, SECTION_ID_REGEXP, TERM_REGEXP
from spire.scraper.classes.raw_course import RawCourse
from spire.scraper.classes.raw_meeting_information import RawMeetingInformation
from spire.scraper.classes.raw_section_detail import RawSectionDetail
from spire.scraper.shared import assert_match

from .shared import RawField, RawObject

log = logging.getLogger(__name__)

def COMBINED_SECTION_NORM(x):
    if "combined_sections" in x:
        for obj in x["combined_sections"]:
            [subject, number] = obj["course_id"].split(" ")
            course_id, _, _ = RawCourse.get_course_id(subject, number)
            obj["course_id"] = course_id

    return x


def COMBINED_SECTION_ASSERTION(x):
    if "combined_sections" in x:
        for obj in x["combined_sections"]:
            assert "course_id" in obj
            assert_match(COURSE_ID_REGEXP, obj["course_id"])
            assert "section_id" in obj
            assert_match(SECTION_ID_REGEXP, obj["section_id"])

    return True


class RawSection(RawObject):
    def __init__(
        self,
        id: str,
        course_id: str,
        term: str,
        details: dict[str, str],
        meeting_information: list,
        restrictions: Optional[dict[str, str]],
        availability: dict[str, str],
        description: Optional[str],
        overview: Optional[str],
    ):
        self.id = id
        self.course_id = course_id
        self.term = term

        self.details = RawSectionDetail(self.id, details)
        log.info("Scraped section detail: %s", self.details)

        self.meeting_information = [RawMeetingInformation(self.id, x) for x in meeting_information]
        log.info(
            "Scraped section meeting information: [\n%s]",
            "\n".join([str(x) for x in self.meeting_information]),
        )

        self.restrictions = restrictions
        self.availability = availability
        self.description = description
        self.overview = overview

        super().__init__(
            Section,
            RawField("id", re=SECTION_ID_REGEXP),
            RawField("course_id", re=COURSE_ID_REGEXP),
            RawField("term", re=TERM_REGEXP),
            RawField("restrictions"),
            RawField("availability", assertions=[COMBINED_SECTION_ASSERTION]),
            RawField("description"),
            RawField("overview"),
        )

    def push(self):
        with transaction.atomic():
            section = super().push(
                defaults={
                    "course_id": self.course_id,
                    "term": self.term,
                    "restrictions": self.restrictions,
                    "availability": self.availability,
                    "description": self.description,
                    "overview": self.overview,
                    "_updated_at": timezone.now(),
                }
            )

            self.details.push(section)

            MeetingInformation.objects.filter(section=section).delete()

            for r_mi in self.meeting_information:
                r_mi.push(section)

        return section
