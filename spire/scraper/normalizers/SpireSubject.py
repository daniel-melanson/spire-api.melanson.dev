from spire.regexp import SUBJECT_ID_REGEXP, SUBJECT_TITLE_REGEXP
from spire.scraper.normalizers.shared import SUBJECT_OVERRIDES, SpireField, SpireObject, clean_id
from spire.scraper.shared import assert_match


class SpireSubject(SpireObject):
    id: str
    title: str

    def __init__(self, id: str, title: str) -> None:
        id = clean_id(id)

        if (override := SUBJECT_OVERRIDES(id)) != id:
            self.id = override[0]
            self.title = override[1]
        else:
            self.id = id
            self.title = title

        super().__init__(
            "SpireSubject",
            SpireField(k="id", re=SUBJECT_ID_REGEXP),
            SpireField(k="title", re=SUBJECT_TITLE_REGEXP),
        )
