import logging
from typing import Optional

from spire.models import Course, Subject
from spire.patterns import COURSE_ID_NUM_REGEXP, COURSE_ID_REGEXP, COURSE_TITLE_REGEXP
from spire.scraper.classes.courses.raw_course_detail import RawCourseDetail
from spire.scraper.classes.courses.raw_course_enrollment_information import (
    RawCourseEnrollmentInformation,
)
from spire.scraper.classes.groups.raw_academic_group import RawAcademicGroup
from spire.scraper.classes.groups.raw_subject import SUBJECT_OVERRIDES
from spire.scraper.classes.normalizers import (
    DESCRIPTION_NOT_AVAILABLE_TO_NONE,
    EMPTY_TO_NONE,
    REPLACE_DOUBLE_SPACE,
    STRIP_STR,
)
from spire.scraper.classes.shared import RawField, RawObject, clean_id

log = logging.getLogger(__name__)


class RawCourse(RawObject):
    @staticmethod
    def get_course_id(subject: str, number: str):
        subject = clean_id(subject)
        number = clean_id(number)

        if subject in SUBJECT_OVERRIDES:
            subject = SUBJECT_OVERRIDES[subject][0]

        return f"{subject} {number}", subject, number

    def __init__(
        self,
        subject: Subject,
        number: str,
        title: str,
        details: dict[str, str],
        description: Optional[str],
        enrollment_information: Optional[dict[str, str]],
    ):
        (id, _, number) = RawCourse.get_course_id(subject.id, number)

        self.id = id
        self.subject = subject
        self.number = number
        self.title = title
        self.description = description

        self.details = RawCourseDetail(self.id, details)
        log.debug("Scraped course detail:\n%s", self.details)

        if self.details.academic_group is not None:
            self._raw_group = RawAcademicGroup(self.details.academic_group)
            log.debug("Scraped academic group:\n%s", self._raw_group)

        if enrollment_information:
            self.enrollment_information = RawCourseEnrollmentInformation(
                self.id, enrollment_information
            )
            log.info(
                "Scraped course enrollment information:\n%s",
                self.enrollment_information,
            )

        super().__init__(
            Course,
            self.id,
            fields=[
                RawField(k="id", re=COURSE_ID_REGEXP),
                RawField(k="subject"),
                RawField(k="number", re=COURSE_ID_NUM_REGEXP),
                RawField(
                    k="title",
                    re=COURSE_TITLE_REGEXP,
                    normalizers=[REPLACE_DOUBLE_SPACE],
                ),
                RawField(
                    k="description",
                    normalizers=[
                        STRIP_STR,
                        EMPTY_TO_NONE,
                        DESCRIPTION_NOT_AVAILABLE_TO_NONE,
                    ],
                    min_len=5,
                ),
            ],
            update_time=True,
        )

    def push(self):
        course, created = super().push()

        if hasattr(self, "_raw_group"):
            self.subject.groups.add(self._raw_group.push())

        self.details.push(course=course)

        if hasattr(self, "enrollment_information"):
            self.enrollment_information.push(course=course)

        return course, created
