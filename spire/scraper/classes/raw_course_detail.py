from typing import Optional

from spire.models import Course, CourseDetail

from .assertions import NO_EMPTY_STRS_ASSERTION
from .normalizers import COURSE_CREDIT_NORMALIZER, SPLIT_NEWLINE
from .shared import RawDictionary, RawField, key_override_factory

DETAILS = [
    RawField(k="Career", len=(1, 16)),
    RawField(k="Units", len=(1, 16), normalizers=[COURSE_CREDIT_NORMALIZER]),
    RawField(k="Grading Basis", len=(1, 32)),
    RawField(
        k="Course Components",
        len=(1, 4),
        normalizers=[SPLIT_NEWLINE],
        assertions=[NO_EMPTY_STRS_ASSERTION],
    ),
    RawField(k="Campus", len=(1, 128)),
    RawField(
        k="Academic Group",
        len=(1, 128),
        normalizers=[
            key_override_factory(
                {
                    "College of Humanities&Fine Art": "College of Humanities & Fine Art",
                    "Stockbridge School": "Stockbridge School of Agriculture",
                    "College of Social & Behav. Sci": "College of Social & Behavioral Sciences",
                    "College of Info & Computer Sci": "Manning College of Information & Computer Sciences",
                }
            )
        ],
    ),
    RawField(
        k="Academic Organization",
        len=(1, 128),
        normalizers=[
            key_override_factory(
                {
                    "Bldg &Construction Technology": "Building & Construction Technology",
                    "Civil & Environmental Engin.": "Civil & Environmental Engineering",
                    "College of Info & Computer Sci": "Manning College of Information & Computer Sciences",
                }
            )
        ],
    ),
]


class RawCourseDetail(RawDictionary):
    career: Optional[str]
    units: Optional[str]
    grading_basis: Optional[str]
    course_components: Optional[list[str]]
    academic_group: Optional[str]
    campus: Optional[str]

    def __init__(self, course_id: str, table: dict[str, str]) -> None:
        self.course_id = course_id

        super().__init__(CourseDetail, table, *DETAILS, pk="course_id")

    def push(self, course: Course):
        return super().push(course=course)
