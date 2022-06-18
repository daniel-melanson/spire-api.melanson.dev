from typing import Optional

from spire.models import Course, Subject
from spire.regexp import COURSE_ID_NUM_REGEXP, COURSE_ID_REGEXP, COURSE_TITLE_REGEXP
from spire.scraper.classes import RawCourseDetail, RawCourseEnrollmentInformation
from spire.scraper.classes.shared import RawField, RawObject, clean_id


class RawCourse(RawObject):
    id: str
    subject: Subject
    number: str
    title: str
    details: RawCourseDetail
    description: Optional[str]
    enrollment_information: Optional[RawCourseEnrollmentInformation]

    def __init__(
        self,
        subject: Subject,
        number: str,
        title: str,
        details: dict[str, str],
        description: Optional[str],
        enrollment_information: Optional[dict[str, str]],
    ):
        number = clean_id(number)

        self.id = f"{subject.id} {number}"
        self.subject = subject
        self.number = number
        self.title = title
        self.description = description

        self.details = raw_course_detail(self.id, details)

        if enrollment_information:
            self.enrollment_information = raw_course_enrollment_information(self.id, enrollment_information)

        super().__init__(
            Course,
            RawField(k="id", re=COURSE_ID_REGEXP),
            RawField(k="number", re=COURSE_ID_NUM_REGEXP),
            RawField(k="title", re=COURSE_TITLE_REGEXP),
            RawField(k="description", len=(5, 4096)),
        )

    def push(self):
        course_model = Course.objects.update_or_create(id=self.id, defaults=self.get_model_defaults(True))

        course_model.details = self.details.push(course_model)

        if self.enrollment_information:
            course_model.enrollment_information = self.enrollment_information.push(course_model)

        self.subject.courses.add(course_model)
