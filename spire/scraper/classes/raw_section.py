from typing import Optional

from django.db import DatabaseError, transaction
from django.utils import timezone

from spire.models import MeetingInformation, Section
from spire.patterns import COURSE_ID_REGEXP, SECTION_ID_REGEXP, TERM_REGEXP
from spire.scraper.classes.raw_meeting_information import RawMeetingInformation
from spire.scraper.classes.raw_section_detail import RawSectionDetail

from .shared import RawField, RawObject


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

        self.meeting_information = [RawMeetingInformation(x) for x in meeting_information]

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
            RawField("availability"),
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

            mi_ids = []
            for r_mi in self.meeting_information:
                mi = r_mi.push(section)

                mi_ids.append(mi.id)

            MeetingInformation.objects.filter(section=section).exclude(id__in=mi_ids).delete()

        return section
