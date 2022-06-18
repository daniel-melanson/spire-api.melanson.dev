from typing import Optional

from spire.scraper.classes.shared import RawField, RawObject, to_camel_case
from spire.scraper.shared import assert_dict_keys_subset

EI = [
    RawField(k="Enrollment Requirement", len=(1, 256)),
    RawField(k="Add Consent", len=(1, 256)),
    RawField(k="Course Attribute", len=(1, 256)),
]


class RawCourseEnrollmentInformation(RawObject):
    add_consent: Optional[str]
    enrollment_requirement: Optional[str]
    course_attribute: Optional[str]

    def __init__(self, table: dict[str, str]) -> None:
        assert_dict_keys_subset(table, map(lambda d: d.k, EI))

        for d in EI:
            s_k = to_camel_case(d.k)

            if d.k in table:
                setattr(self, s_k, table[d.k])

        super().__init__(RawCourseEnrollmentInformation, EI)
