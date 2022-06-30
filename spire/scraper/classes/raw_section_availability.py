import logging
import re

from spire.models import CombinedSectionAvailability, Section, SectionAvailability
from spire.scraper.shared import assert_match

from .shared import RawDictionary, RawField

log = logging.getLogger(__name__)

AVAILABILITY_FIELDS = [
    RawField(k="Capacity"),
    RawField(k="Enrollment Total"),
    RawField(k="Available Seats"),
    RawField(k="Wait List Capacity"),
    RawField(k="Wait List Total"),
]

SECTION_ID_OVERRIDES = {
    "-(62798)": "01-DIS(62798)",
    "-(62799)": "01AA-DIS(62799)",
    "-(62800)": "01AB-DIS(62800)",
    "-(62801)": "01AC-DIS(62801)",
}


def section_list_normalizer(lst):
    sections = []
    for section in lst:
        if m := re.fullmatch(r"- \((\d+)\): S-International SciFi Cinema", section):
            section_id = SECTION_ID_OVERRIDES[f"-({m.group(1)})"]
        else:
            # COMP-LIT 391SF-01AC DIS (50749): S-International SciFi Cinema
            m = assert_match(r"\S+\s+\S+-(?P<id>\S+)\s+(?P<type>\S+)\s+\((?P<number>\d+)\).+", section)

            section_id = f"{m.group('id')}-{m.group('type')}({m.group('number')})"

        sections.append(section_id)

    return sections


class RawCombinedSectionAvailability(RawDictionary):
    def __init__(self, section_id: str, table: dict[str, str]) -> None:
        self.section_id = section_id

        super().__init__(
            CombinedSectionAvailability,
            table,
            fields=[RawField(k="Sections", normalizers=[section_list_normalizer]), *AVAILABILITY_FIELDS],
        )

    def push(self, individual_availability: SectionAvailability):
        return super().push(individual_availability=individual_availability)


class RawSectionAvailability(RawDictionary):
    def __init__(self, section_id: str, table: dict[str, str]) -> None:
        self.section_id = section_id
        self._is_combined = "Individual Availability" in table

        if self._is_combined:
            self.combined_availability = RawCombinedSectionAvailability(
                section_id, table["Combined Availability"]
            )
            log.info("Scraped combined availability: %s", self.combined_availability)
            super().__init__(
                SectionAvailability,
                table["Individual Availability"],
                pk="section_id",
                fields=AVAILABILITY_FIELDS,
            )
        else:
            table["Capacity"] = table["Total Enrollment Capacity"]
            del table["Total Enrollment Capacity"]

            super().__init__(
                SectionAvailability,
                table,
                pk="section_id",
                fields=AVAILABILITY_FIELDS,
            )

    def push(self, section: Section):
        availability = super().push(section=section)

        if self._is_combined:
            self.combined_availability.push(availability)
