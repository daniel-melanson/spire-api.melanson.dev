from spire.models import Section, SectionDetail
from spire.patterns import UNITS_REGEXP

from .assertions import NO_EMPTY_STRS_ASSERTION
from .normalizers import COURSE_CREDIT_NORMALIZER, NONE_STRING_TO_NONE_NORMALIZER
from .shared import RawDictionary, RawField, key_override_factory


def class_component_norm(x: str) -> list[str]:
    l = []
    for s in x.split("\n"):
        if s == "Required":
            l[-1] = l[-1] + " (Required)"
        else:
            l.append(s)

    return l


DETAILS = [
    RawField(k="Status", choices=("Open", "Closed")),
    RawField(k="Class Number", re=r"^\d{3,15}$"),
    RawField(
        k="Session",
        normalizers=[key_override_factory({"*University": "University", "UWW": "University Without Walls"})],
        len=(1, 64),
    ),
    RawField(
        k="Units",
        normalizers=[COURSE_CREDIT_NORMALIZER],
        re=UNITS_REGEXP,
    ),
    RawField(
        k="Class Components",
        normalizers=[class_component_norm],
        assertions=[NO_EMPTY_STRS_ASSERTION],
    ),
    RawField(k="Career", choices=("Undergraduate", "Graduate")),
    RawField(k="Grading", len=(1, 64)),
    RawField(k="Topic", len=(1, 64)),
    RawField(
        k="Gened",
        normalizers=[
            NONE_STRING_TO_NONE_NORMALIZER,
        ],
    ),
    RawField(k="RAP/TAP/HLC", normalizers=[NONE_STRING_TO_NONE_NORMALIZER]),
]


class RawSectionDetail(RawDictionary):
    def __init__(self, section_id: str, table: dict[str, str]) -> None:
        self.section_id = section_id

        super().__init__(SectionDetail, table, *DETAILS, pk="section_id")

    def push(self, section: Section):
        return super().push(section=section)
