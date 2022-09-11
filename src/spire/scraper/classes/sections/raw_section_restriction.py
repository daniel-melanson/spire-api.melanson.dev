from spire.models import SectionRestriction
from spire.scraper.classes.normalizers import STRIP_STR
from spire.scraper.classes.shared import RawDictionary, RawField


class RawSectionRestriction(RawDictionary):
    def __init__(self, section_id: str, table: dict[str, str]) -> None:
        self.section_id = section_id

        super().__init__(
            SectionRestriction,
            table,
            pk="section_id",
            fields=[
                RawField(k="Add Consent", min_len=1, normalizers=[STRIP_STR]),
                RawField(k="Enrollment Requirements", min_len=1, normalizers=[STRIP_STR]),
                RawField(k="Drop Consent", min_len=1, normalizers=[STRIP_STR]),
            ],
        )
