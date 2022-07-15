import logging
from typing import Optional

from django.db import transaction
from django.utils import timezone

from spire.models import MeetingInformation, Section
from spire.patterns import COURSE_ID_REGEXP, COURSE_TITLE_REGEXP, SECTION_ID_REGEXP, TERM_REGEXP
from spire.scraper.classes.normalizers import REPLACE_DOUBLE_SPACE, STRIP_STR
from spire.scraper.classes.raw_meeting_information import RawMeetingInformation
from spire.scraper.classes.raw_section_availability import RawSectionAvailability
from spire.scraper.classes.raw_section_detail import RawSectionDetail
from spire.scraper.classes.raw_section_restriction import RawSectionRestriction
from spire.scraper.shared import assert_match

from .shared import RawField, RawObject

log = logging.getLogger(__name__)


def COMBINED_SECTION_ASSERTION(x):
    if "combined_sections" in x:
        for s_id in x["combined_sections"]:
            assert_match(r"\d{3,15}", s_id)

    return True


class RawSection(RawObject):
    def __init__(
        self,
        id: str,
        course_id: str,
        course_title: str,
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
        self.course_title = course_title
        self.term = term

        self.details = RawSectionDetail(self.id, details)
        log.info("Scraped section detail:\n%s", self.details)

        self.meeting_information = [RawMeetingInformation(self.id, x) for x in meeting_information]
        log.info(
            "Scraped section meeting information: [\n%s]",
            "\n".join([str(x) for x in self.meeting_information]),
        )

        if restrictions:
            self.restrictions = RawSectionRestriction(self.id, restrictions)
            log.info("Scraped section restrictions:\n%s", self.restrictions)

        self.availability = RawSectionAvailability(self.id, availability)
        log.info("Scraped section availability:\n%s", self.availability)

        self.description = description
        self.overview = overview

        super().__init__(
            Section,
            fields=[
                RawField("id", re=SECTION_ID_REGEXP),
                RawField("course_id", re=COURSE_ID_REGEXP),
                RawField("course_title", re=COURSE_TITLE_REGEXP, normalizers=[REPLACE_DOUBLE_SPACE]),
                RawField("term", re=TERM_REGEXP),
                RawField("description", normalizers=[STRIP_STR], min_len=5),
                RawField("overview", min_len=5),
            ],
        )

    def push(self, subject):
        with transaction.atomic():
            section = super().push(
                defaults={
                    "subject": subject,
                    "course_id": self.course_id,
                    "course_title": self.course_title,
                    "term": self.term,
                    "description": self.description,
                    "overview": self.overview,
                    "_updated_at": timezone.now(),
                }
            )

            self.details.push(section)
            if hasattr(self, "restrictions"):
                self.restrictions.push(section)
            self.availability.push(section)

            dropped, _ = MeetingInformation.objects.filter(section_id=section.id).delete()

            log.debug(
                "Dropped %s MeetingInformation records in preparation to push %s new ones.",
                dropped,
                len(self.meeting_information),
            )

            for r_mi in self.meeting_information:
                r_mi.push(section)

        return section
