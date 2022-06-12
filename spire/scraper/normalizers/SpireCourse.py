from typing import Optional

from spire.regexp import COURSE_ID_NUM_REGEXP, COURSE_ID_REGEXP, COURSE_TITLE_REGEXP, SUBJECT_ID_REGEXP
from spire.scraper.normalizers.shared import DETAIL_OVERRIDES, SUBJECT_OVERRIDES
from spire.scraper.shared import assert_dict_keys_subset, assert_match

DETAIL_KEYS = [
    "Career",
    "Units",
    "Grading Basis",
    "Course Components",
    "Academic Group",
    "Academic Organization",
    "Campus",
]


class SpireCourse:
    course_id: str
    subject: str
    number: str
    title: str
    details: dict[str, str]
    enrollment_information: Optional[dict[str, str]]
    description: Optional[str]

    def __init__(
        self,
        course_id: str,
        subject: str,
        number: str,
        title: str,
        details: dict[str, str],
        enrollment_information: Optional[dict[str, str]],
        description: Optional[str],
    ):
        if (override := SUBJECT_OVERRIDES(subject)) != subject:
            subject = override[0]
            course_id = f"{subject} {number}"

        assert_match(COURSE_ID_REGEXP, course_id)
        self.course_id = course_id

        assert_match(SUBJECT_ID_REGEXP, subject)
        self.subject = subject

        assert_match(COURSE_ID_NUM_REGEXP, number)
        self.number = number

        assert_match(COURSE_TITLE_REGEXP, title)
        self.title = title

        assert_dict_keys_subset(
            details,
            DETAIL_KEYS,
        )

        for key in DETAIL_KEYS:
            if key not in details:
                continue

            if key in DETAIL_OVERRIDES:
                x = DETAIL_OVERRIDES[key](details[key])
            else:
                x = details[key]

            details[key] = x

        self.details = details

        self.enrollment_information = enrollment_information

        if description:
            description = (
                description.replace("\\n", " ")
                .replace("\n", " ")
                .replace("\\\\\\n", " ")
                .replace("  ", " ")
                .replace("\n\n", "\n")
            )

        self.description = description

    def __str__(self):
        details = {
            "course_id": self.course_id,
            "subject": self.subject,
            "number": self.number,
            "title": self.title,
            "details": str(self.details),
        }

        if self.enrollment_information:
            details["enrollment_information"] = self.enrollment_information
        if self.description:
            details["description"] = self.description

        return "SpireCourse(" + str(details) + ")"
