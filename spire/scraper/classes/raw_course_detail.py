from typing import Optional

from spire.models import Course, CourseDetail
from spire.regexp import COURSE_DETAIL_COMPONENT_REGEXP
from spire.scraper.shared import assert_dict_keys_subset

from .shared import RawField, RawObject, key_override_factory, to_camel_case

DETAILS = [
    RawField(k="Career", len=(1, 16)),
    RawField(k="Units", len=(1, 16)),
    RawField(k="Grading Basis", len=(1, 32)),
    RawField(
        k="Course Components",
        len=(1, 4),
        normalizers=[lambda x: x.strip().replace("\n", ", ")],
        re=COURSE_DETAIL_COMPONENT_REGEXP,
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


class RawCourseDetail(RawObject):
    career: Optional[str]
    units: Optional[str]
    grading_basis: Optional[str]
    course_components: Optional[list[str]]
    academic_group: Optional[str]
    campus: Optional[str]

    def __init__(self, course_id: str, table: dict[str, str]) -> None:
        course_id = course_id
        assert_dict_keys_subset(table, map(lambda d: d.k, DETAILS))

        for d in DETAILS:
            s_k = to_camel_case(d.k)

            if d.k in table:
                setattr(self, s_k, table[d.k])

        super().__init__(RawCourseDetail, *DETAILS, pk="course_id")

    def push(self, course: Course):
        return CourseDetail.objects.update_or_create(course=course, defaults=self.get_model_default())
