from functools import reduce
from typing import Optional

from spire.models import Course, CourseDetail, Section, SectionDetail
from spire.scraper.shared import assert_dict_keys_subset

from .shared import RawField, RawObject, key_override_factory, to_camel_case

DETAILS = [
    RawField(k="Status"),
    RawField(k="Class Number", re=r"\d{3,10}"),
    RawField(k="Session"),
    RawField(k="Units"),
    RawField(k="Class Components"),
    RawField(k="Career"),
    RawField(k="Grading"),
    RawField(k="Gened"),
    RawField(k="RAP/TAP/HLC"),
]


class RawSectionDetail(RawObject):
    def __init__(self, section_id: str, table: dict[str, str]) -> None:
        self.section_id = section_id
        assert_dict_keys_subset(table, map(lambda d: d.k, DETAILS))

        for d in DETAILS:
            s_k = to_camel_case(d.k.replace("/", " "))

            if d.k in table:
                setattr(self, s_k, table[d.k])

        super().__init__(SectionDetail, *DETAILS, pk="section_id")

    def push(self, section: Section):
        detail, created = SectionDetail.objects.update_or_create(
            section=section, defaults=super().get_model_defaults()
        )
