import logging
from typing import Optional

from django.db import transaction
from django.utils import timezone

from spire.models import MeetingInformation, Section
from spire.patterns import SECTION_ID_REGEXP, TERM_REGEXP
from spire.scraper.classes.normalizers import REPLACE_DOUBLE_SPACE
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
        term: str,
        alternative_title: str,
        details: dict[str, str],
        meeting_information: list,
        restrictions: Optional[dict[str, str]],
        availability: dict[str, str],
        description: Optional[str],
        overview: Optional[str],
    ):
        self.id = id
        self.term = term
        self.alternative_title = alternative_title

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
                RawField("term", re=TERM_REGEXP),
                RawField("alternative_title", normalizers=[REPLACE_DOUBLE_SPACE])
                RawField(
                    "description",
                    normalizers=[STRIP_STR, key_override_factory({"Not available at this time": None})],
                    min_len=5,
                ),
                RawField("overview", min_len=5),
            ],
        )

    def push(self, subject, course):
        with transaction.atomic():
            section = super().push(
                defaults={
                    "subject": subject,
                    "course": course,
                    "term": self.term,
                    "alternative_title": self.alternative_title,
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
