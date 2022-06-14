from spire.regexp import SUBJECT_ID_REGEXP, SUBJECT_TITLE_REGEXP
from spire.scraper.normalizers.shared import SUBJECT_OVERRIDES, SpireField, SpireObject, clean_id
from spire.scraper.shared import assert_match


class SpireSubject(SpireObject):
    subject_id: str
    title: str

    def __init__(self, subject_id: str, title: str) -> None:
        subject_id = clean_id(subject_id)

        if (override := SUBJECT_OVERRIDES(subject_id)) != subject_id:
            self.subject_id = override[0]
            self.title = override[1]
        else:
            self.subject_id = subject_id
            self.title = title

        super().__init__(
            "SpireSubject"
            "subject_id",
            SpireField(k="subject_id", re=SUBJECT_ID_REGEXP),
            SpireField(k="title", re=SUBJECT_TITLE_REGEXP),
        )
