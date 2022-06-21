from spire.models import Section, SectionDetail
from spire.patterns import UNITS_REGEXP
from spire.scraper.shared import assert_dict_keys_subset

from .assertions import NO_EMPTY_STRS_ASSERTION
from .shared import (
    COURSE_CREDIT_NORMALIZER,
    NONE_STRING_TO_NONE_NORMALIZER,
    RawField,
    RawObject,
    key_override_factory,
    to_camel_case,
)


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
    RawField(k="Class Components", normalizers=[class_component_norm], assertions=[NO_EMPTY_STRS_ASSERTION]),
    RawField(k="Career", choices=("Undergraduate")),
    RawField(k="Grading"),
    RawField(k="Topic"),
    RawField(
        k="Gened",
        normalizers=[
            NONE_STRING_TO_NONE_NORMALIZER,
        ],
    ),
    RawField(k="RAP/TAP/HLC", normalizers=[NONE_STRING_TO_NONE_NORMALIZER]),
]


class RawSectionDetail(RawObject):
    def __init__(self, section_id: str, table: dict[str, str]) -> None:
        self.section_id = section_id
        assert_dict_keys_subset(table, map(lambda d: d.k, DETAILS))

        for d in DETAILS:
            s_k = to_camel_case(d.k)

            if d.k in table:
                setattr(self, s_k, table[d.k])
            else:
                setattr(self, s_k, None)

        super().__init__(SectionDetail, *DETAILS, pk="section_id")

    def push(self, section: Section):
        detail, created = SectionDetail.objects.update_or_create(
            section=section, defaults=super().get_model_defaults()
        )
