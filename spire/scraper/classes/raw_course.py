from typing import Optional

from spire.models import Course, Subject
from spire.patterns import COURSE_ID_NUM_REGEXP, COURSE_ID_REGEXP, COURSE_TITLE_REGEXP
from spire.scraper.classes.raw_subject import SUBJECT_OVERRIDES

from .raw_course_detail import RawCourseDetail
from .raw_course_enrollment_information import RawCourseEnrollmentInformation
from .shared import RawField, RawObject, clean_id


class RawCourse(RawObject):
    def get_course_id(subject: str, number: str):
        [subject, number] = clean_id(subject, number)

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

        if enrollment_information:
            self.enrollment_information = RawCourseEnrollmentInformation(self.id, enrollment_information)
        else:
            self.enrollment_information = None

        super().__init__(
            Course,
            RawField(k="id", re=COURSE_ID_REGEXP),
            RawField(k="subject"),
            RawField(k="number", re=COURSE_ID_NUM_REGEXP),
            RawField(k="title", re=COURSE_TITLE_REGEXP),
            RawField(k="description", len=(5, 4096)),
            update_time=True,
        )

    def push(self):
        course = super().push()

        self.details.push(course)

        if self.enrollment_information:
            self.enrollment_information.push(course)
