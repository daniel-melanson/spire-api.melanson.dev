import logging
from typing import Optional

from django.db import transaction
from django.utils import timezone

from spire.models import Section, SectionMeetingInformation
from spire.patterns import SECTION_ID_REGEXP
from spire.scraper.classes.normalizers import (
    DESCRIPTION_NOT_AVAILABLE_TO_NONE,
    NONE_STRING_TO_NONE_NORMALIZER,
    STRIP_STR,
)
from spire.scraper.classes.sections.raw_section_availability import RawSectionAvailability
from spire.scraper.classes.sections.raw_section_detail import RawSectionDetail
from spire.scraper.classes.sections.raw_section_meeting_information import RawSectionMeetingInformation
from spire.scraper.classes.sections.raw_section_restriction import RawSectionRestriction
from spire.scraper.classes.shared import RawField, RawObject
from spire.scraper.shared import assert_match

log = logging.getLogger(__name__)


def COMBINED_SECTION_ASSERTION(x):
    if "combined_sections" in x:
        for s_id in x["combined_sections"]:
            assert_match(r"\d{3,15}", s_id)

    return True


class RawSection(RawObject):
    def __init__(
        self,
        spire_id: str,
        details: dict[str, str],
        meeting_information: list,
        restrictions: Optional[dict[str, str]],
        availability: dict[str, str],
        description: Optional[str],
        overview: Optional[str],
    ):
        self.spire_id = spire_id

        self.details = RawSectionDetail(self.spire_id, details)
        log.info("Scraped section detail:\n%s", self.details)

        self.meeting_information = [
            RawSectionMeetingInformation(self.spire_id, x) for x in meeting_information
        ]
        log.info(
            "Scraped section meeting information: [\n%s]",
            "\n".join([str(x) for x in self.meeting_information]),
        )

        if restrictions:
            self.restrictions = RawSectionRestriction(self.spire_id, restrictions)
            log.info("Scraped section restrictions:\n%s", self.restrictions)

        self.availability = RawSectionAvailability(self.spire_id, availability)
        log.info("Scraped section availability:\n%s", self.availability)

        self.description = description
        self.overview = overview

        super().__init__(
            Section,
            spire_id,
            fields=[
                RawField("spire_id", re=SECTION_ID_REGEXP),
                RawField(
                    "description",
                    normalizers=[STRIP_STR, DESCRIPTION_NOT_AVAILABLE_TO_NONE],
                    min_len=5,
                ),
                RawField("overview", min_len=5, normalizers=[NONE_STRING_TO_NONE_NORMALIZER]),
            ],
        )

    def push(self, offering):
        with transaction.atomic():
            section, _ = Section.objects.update_or_create(
                spire_id=self.spire_id,
                offering=offering,
                defaults={
                    "spire_id": self.spire_id,
                    "description": self.description,
                    "overview": self.overview,
                    "_updated_at": timezone.now(),
                },
            )

            self.details.push(section=section)
            if hasattr(self, "restrictions"):
                self.restrictions.push(section=section)
            self.availability.push(section=section)

            dropped, _ = SectionMeetingInformation.objects.filter(section_id=section.id).delete()

            log.debug(
                "Dropped %s MeetingInformation records in preparation to push %s new ones.",
                dropped,
                len(self.meeting_information),
            )

            for r_mi in self.meeting_information:
                r_mi.push(section=section)

        return section
