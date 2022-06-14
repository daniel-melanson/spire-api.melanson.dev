from typing import Optional

from spire.models import Subject
from spire.regexp import COURSE_ID_NUM_REGEXP, COURSE_ID_REGEXP, COURSE_TITLE_REGEXP, SUBJECT_ID_REGEXP
from spire.scraper.normalizers.shared import (
    SUBJECT_OVERRIDES,
    SpireField,
    SpireObject,
    clean_id,
    detail_override_normalizer,
)
from spire.scraper.shared import assert_dict_keys_subset

DETAIL_KEYS = [
    "Career",
    "Units",
    "Grading Basis",
    "Course Components",
    "Academic Group",
    "Academic Organization",
    "Campus",
]


class SpireCourse(SpireObject):
    course_id: str
    subject: str
    number: str
    title: str
    details: dict[str, str]
    enrollment_information: Optional[dict[str, str]]
    description: Optional[str]

    def get_course_id(subject: str, number: str) -> tuple[str, str, str]:
        [subject, number] = clean_id(subject, number)

        if (override := SUBJECT_OVERRIDES(subject)) != subject:
            subject = override[0]

        return (f"{subject} {number}", subject, number)

    def __init__(
        self,
        subject: str,
        number: str,
        title: str,
        details: dict[str, str],
        enrollment_information: Optional[dict[str, str]],
        description: Optional[str],
    ):
        (course_id, subject, number) = SpireCourse.get_course_id(subject, number)

        self.subject = subject
        self.number = number
        self.course_id = course_id
        self.title = title
        self.details = details
        self.enrollment_information = enrollment_information
        self.description = description

        super().__init__(
            "SpireCourse",
            "course_id",
            SpireField(k="subject", re=SUBJECT_ID_REGEXP),
            SpireField(k="number", re=COURSE_ID_NUM_REGEXP),
            SpireField(k="course_id", re=COURSE_ID_REGEXP),
            SpireField(k="title", re=COURSE_TITLE_REGEXP),
            SpireField(
                k="details",
                normalizers=[detail_override_normalizer],
                assertions=[lambda x: assert_dict_keys_subset(x, DETAIL_KEYS)],
            ),
            SpireField(k="enrollment_information"),
            SpireField(k="description"),
        )

        self.subject = Subject.objects.get(pk=self.subject)
