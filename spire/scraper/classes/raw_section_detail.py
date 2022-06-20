from functools import reduce
from typing import Optional

from spire.models import Course, CourseDetail, Section, SectionDetail
from spire.patterns import UNITS_REGEXP
from spire.scraper.shared import assert_dict_keys_subset

from .shared import RawField, RawObject, key_override_factory, re_override_factory, to_camel_case

DETAILS = [
    RawField(k="Status", re=r"^(Open|Closed)$"),
    RawField(k="Class Number", re=r"^\d{3,10}$"),
    RawField(k="Session", normalizers=[key_override_factory({"*University": "University", "UWW": "University Without Walls" })]),
    RawField(k="Units", normalizers=[re_override_factory((r"^\d$", "$0.00"), (r"^(\d+) - (\d+)$", "$1.00 - $2.00"))], re=UNITS_REGEXP),
    RawField(k="Class Components"),
    RawField(k="Career"),
    RawField(k="Grading"),
    RawField(k="Topic"),
    RawField(k="Gened", normalizers=[key_override_factory({"None": None})]),
    RawField(k="RAP/TAP/HLC", normalizers=[key_override_factory({"(None)": None})]),
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
