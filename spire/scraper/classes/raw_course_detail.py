from typing import Optional

from spire.models import Course, CourseDetail

from .assertions import NO_EMPTY_STRS_ASSERTION
from .normalizers import COURSE_CREDIT_NORMALIZER, SPLIT_NEWLINE
from .shared import RawDictionary, RawField, key_override_factory


class RawCourseDetail(RawDictionary):
    career: Optional[str]
    units: Optional[str]
    grading_basis: Optional[str]
    course_components: Optional[list[str]]
    academic_group: Optional[str]
    campus: Optional[str]

    def __init__(self, course_id: str, table: dict[str, str]) -> None:
        self.course_id = course_id

        super().__init__(
            CourseDetail,
            table,
            fields=[
                RawField(k="Career", min_len=1),
                RawField(k="Units", min_len=1, normalizers=[COURSE_CREDIT_NORMALIZER]),
                RawField(k="Grading Basis", min_len=1),
                RawField(
                    k="Course Components",
                    len=(1, 4),
                    normalizers=[SPLIT_NEWLINE],
                    assertions=[NO_EMPTY_STRS_ASSERTION],
                ),
                RawField(k="Campus", min_len=3),
                RawField(
                    k="Academic Group",
                    min_len=1,
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
                    min_len=1,
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
            ],
            pk="course_id",
        )

    def push(self, course: Course):
        return super().push(course=course)
