from spire.regexp import SUBJECT_ID_REGEXP, SUBJECT_TITLE_REGEXP
from spire.scraper.normalizers.shared import SUBJECT_OVERRIDES
from spire.scraper.shared import assert_match


class SpireSubject:
    subject_id: str
    title: str

    def __init__(self, subject_id: str, title: str) -> None:
        if (override := SUBJECT_OVERRIDES(subject_id)) != subject_id:
            self.subject_id = override[0]
            self.title = override[1]
        else:
            self.subject_id = subject_id
            self.title = title

        assert_match(SUBJECT_ID_REGEXP, self.subject_id)
        assert_match(SUBJECT_TITLE_REGEXP, self.title)
