import logging
import re
from typing import Any

from spire.models import Section, SectionAvailability, SectionCombinedAvailability
from spire.scraper.classes.shared import RawDictionary, RawField
from spire.scraper.shared import assert_match

log = logging.getLogger(__name__)

AVAILABILITY_FIELDS = [
    RawField(k="Capacity"),
    RawField(k="Enrollment Total"),
    RawField(k="Available Seats"),
    RawField(k="Wait List Capacity"),
    RawField(k="Wait List Total"),
    RawField(k="NSO Enrollment Capacity"),
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
            spire_id = SECTION_ID_OVERRIDES[f"-({m.group(1)})"]
        else:
            # COMP-LIT 391SF-01AC DIS (50749): S-International SciFi Cinema
            m = assert_match(
                r"\S+\s+\S+-(?P<id>\S+)\s+(?P<type>\S+)\s+\((?P<number>\d+)\).+",
                section,
            )

            spire_id = f"{m.group('id')}-{m.group('type')}({m.group('number')})"

        sections.append(spire_id)

    return sections


class RawCombinedSectionAvailability(RawDictionary):
    def __init__(self, spire_id: str, table: dict[str, str]) -> None:
        super().__init__(
            SectionCombinedAvailability,
            spire_id,
            table,
            [
                RawField(k="Sections", normalizers=[section_list_normalizer]),
                *AVAILABILITY_FIELDS,
            ],
        )


class RawSectionAvailability(RawDictionary):
    def __init__(self, spire_id: str, table: dict[str, Any]) -> None:
        self._is_combined = "Individual Availability" in table

        if self._is_combined:
            self.combined_availability = RawCombinedSectionAvailability(
                spire_id, table["Combined Availability"]
            )
            log.info("Scraped combined availability:\n%s", self.combined_availability)
            super().__init__(
                SectionAvailability,
                spire_id,
                table["Individual Availability"],
                AVAILABILITY_FIELDS,
            )
        else:
            table["Capacity"] = table["Total Enrollment Capacity"]
            del table["Total Enrollment Capacity"]

            if "NSO Enroll Cap" in table:
                table["NSO Enrollment Capacity"] = table["NSO Enroll Cap"]
                del table["NSO Enroll Cap"]

            super().__init__(
                SectionAvailability,
                spire_id,
                table,
                AVAILABILITY_FIELDS,
            )

    def push(self, section: Section):
        availability = super().push(section=section)

        if self._is_combined:
            self.combined_availability.push(individual_availability=availability)
