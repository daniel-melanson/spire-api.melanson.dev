from typing import Optional

from spire.models import Course, Subject
from spire.regexp import COURSE_ID_NUM_REGEXP, COURSE_ID_REGEXP, COURSE_TITLE_REGEXP
from spire.scraper.classes.shared import RawField, RawObject, clean_id


class RawCourse(RawObject):
    id: str
    subject: Subject
    number: str
    title: str
    description: Optional[str]

    def __init__(
        self,
        subject: Subject,
        number: str,
        title: str,
        description: Optional[str],
    ):
        number = clean_id(number)

        self.id = f"{subject.id} {number}"
        self.subject = subject
        self.number = number
        self.title = title
        self.description = description

        super().__init__(
            Course,
            RawField(k="id", re=COURSE_ID_REGEXP),
            RawField(k="number", re=COURSE_ID_NUM_REGEXP),
            RawField(k="title", re=COURSE_TITLE_REGEXP),
            RawField(k="description"),
            time_aware=True,
        )

    def push(self):
        pass
