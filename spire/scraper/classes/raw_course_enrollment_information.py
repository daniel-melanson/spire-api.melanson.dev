from typing import Optional

from spire.models import Course, CourseEnrollmentInformation
from spire.scraper.classes.assertions import NO_EMPTY_STRS_ASSERTION
from spire.scraper.classes.normalizers import SPLIT_NEWLINE

from .shared import RawDictionary, RawField


class RawCourseEnrollmentInformation(RawDictionary):
    add_consent: Optional[str]
    enrollment_requirement: Optional[str]
    course_attribute: Optional[str]

    def __init__(self, course_id: str, table: dict[str, str]) -> None:
        self.course_id = course_id

        super().__init__(
            CourseEnrollmentInformation,
            table,
            pk="course_id",
            fields=[
                RawField(k="Enrollment Requirement", min_len=1),
                RawField(k="Add Consent", min_len=1),
                RawField(
                    k="Course Attribute",
                    min_len=1,
                    normalizers=[SPLIT_NEWLINE],
                    assertions=[NO_EMPTY_STRS_ASSERTION],
                ),
            ],
        )

    def push(self, course: Course):
        return super().push(course=course)
