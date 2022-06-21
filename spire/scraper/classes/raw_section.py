from typing import NamedTuple, Optional

from django.utils import timezone

from spire.models import Section, Staff
from spire.patterns import COURSE_ID_REGEXP, SECTION_ID_REGEXP, TERM_REGEXP
from spire.scraper.classes.raw_section_detail import RawSectionDetail

from .raw_course_enrollment_information import RawCourseEnrollmentInformation
from .shared import RawField, RawObject, clean_id


class RawStaff(NamedTuple):
    name: str
    email: Optional[str]


class RawMeetingInformation(NamedTuple):
    days_and_times: str
    instructors: list[RawStaff]
    room: str
    meeting_dates: str


class RawSection(RawObject):
    def __init__(
        self,
        id: str,
        course_id: str,
        term: str,
        details: dict[str, str],
        meeting_information: list[RawMeetingInformation],
        restrictions: Optional[dict[str, str]],
        availability: dict[str, str],
        description: Optional[str],
        overview: Optional[str],
    ):
        self.id = id
        self.course_id = course_id
        self.term = term

        self.details = RawSectionDetail(self.id, details)

        self.meeting_information = meeting_information

        self.restrictions = restrictions
        self.availability = availability
        self.description = description
        self.overview = overview

        super().__init__(
            Section,
            RawField("id", re=SECTION_ID_REGEXP),
            RawField("course_id", re=COURSE_ID_REGEXP),
            RawField("term", re=TERM_REGEXP),
            RawField("details"),
            RawField("meeting_information"),
            RawField("restrictions"),
            RawField("availability"),
            RawField("description"),
            RawField("overview"),
        )

    def push(self):
        section, created = Section.objects.update_or_create(
            id=self.id,
            defaults={
                "course_id": self.course_id,
                "term": self.term,
                "meeting_information": list(
                    map(lambda x: {k: getattr(x, k) for k in x._fields if k != "instructors"})
                ),
                "restrictions": self.restrictions,
                "availability": self.availability,
                "description": self.description,
                "overview": self.overview,
                "_updated_at": timezone.now(),
            },
        )

        section.details = self.details.push(section)

        new_instructors = []
        for raw_instructor in self.meeting_information.instructors:
            if raw_instructor.email:
                instructor, _ = Staff.objects.get_or_create(
                    email=raw_instructor.email, defaults={"name": raw_instructor.name}
                )
            elif raw_instructor.name.lower() == "Staff":
                instructor = Staff.objects.get_or_create(name="Staff")
            else:
                possible_instructors = Staff.objects.filter(name=raw_instructor.name)

                if len(possible_instructors) == 0:
                    instructor = Staff.objects.create(name=raw_instructor.name)

            new_instructors.append(instructor)

        section.instructors.set(new_instructors)

        return section
