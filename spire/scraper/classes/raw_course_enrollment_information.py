from typing import Optional

from spire.models import Course, CourseEnrollmentInformation
from spire.scraper.shared import assert_dict_keys_subset

from .shared import RawField, RawObject, to_camel_case

EI = [
    RawField(k="Enrollment Requirement", len=(1, 256)),
    RawField(k="Add Consent", len=(1, 256)),
    RawField(k="Course Attribute", len=(1, 256)),
]


class RawCourseEnrollmentInformation(RawObject):
    add_consent: Optional[str]
    enrollment_requirement: Optional[str]
    course_attribute: Optional[str]

    def __init__(self, course_id: str, table: dict[str, str]) -> None:
        self.course_id = course_id
        assert_dict_keys_subset(table, map(lambda d: d.k, EI))

        for d in EI:
            s_k = to_camel_case(d.k)

            if d.k in table:
                setattr(self, s_k, table[d.k])

        super().__init__(RawCourseEnrollmentInformation, *EI, pk="course_id")

    def push(self, course: Course):
        return CourseEnrollmentInformation.objects.update_or_create(
            course=course, defaults=self.get_model_default()
        )
