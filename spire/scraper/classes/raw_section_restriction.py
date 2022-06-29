from spire.models import Section, SectionDetail

from .normalizers import STRIP_STR
from .shared import RawDictionary, RawField

DETAILS = [
    RawField(k="Add Consent", min_len=1, normalizers=[STRIP_STR]),
    RawField(k="Enrollment Requirement", min_len=1, normalizers=[STRIP_STR]),
    RawField(k="Drop Consent", min_len=1, normalizers=[STRIP_STR]),
]


class RawSectionRestriction(RawDictionary):
    def __init__(self, section_id: str, table: dict[str, str]) -> None:
        self.section_id = section_id

        super().__init__(SectionDetail, table, *DETAILS, pk="section_id")

    def push(self, section: Section):
        return super().push(section=section)
