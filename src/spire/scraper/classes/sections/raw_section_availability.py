import logging
import re
from typing import Any

from spire.models import Section, SectionAvailability, SectionCombinedCapacity
from spire.scraper.classes.shared import RawDictionary, RawField, RawObject
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


def _get_combined_capacity(sections, term, defaults):
    log.debug("Searching for a combined capacity with %s during %s", sections, term.id)
    for sprie_id in sections:
        try:
            section = Section.objects.get(offering__term=term, spire_id=sprie_id)

            availability = section.availability
            if availability and availability.combined_capacity:
                log.debug("Found combined capacity")
                combined_capacity = availability.combined_capacity

                combined_capacity.capacity = defaults["capacity"]
                combined_capacity.wait_list_capacity = defaults["wait_list_capacity"]
                combined_capacity.nso_enrollment_capacity = defaults[
                    "nso_enrollment_capacity"
                ]
                combined_capacity.save()

                return combined_capacity, False
        except Section.DoesNotExist:  # type: ignore
            continue

    log.debug("No combined capacity found, returning")
    return SectionCombinedCapacity.objects.create(**defaults), True


class RawSectionCombinedCapacity:
    def __init__(self, table: dict[str, str]) -> None:
        self.sections = table["Sections"]
        self.capacity = table["Capacity"]
        self.wait_list_capacity = table["Wait List Capacity"]
        self.nso_enrollment_capacity = table.get("NSO Enrollment Capacity", None)

    def push(self, individual_availability: SectionAvailability):
        if individual_availability.combined_capacity:
            combined_capacity = individual_availability.combined_capacity

            combined_capacity.capacity = self.capacity
            combined_capacity.wait_list_capacity = self.wait_list_capacity
            combined_capacity.nso_enrollment_capacity = self.nso_enrollment_capacity

            combined_capacity.save()
        else:
            section = individual_availability.section

            individual_availability.combined_capacity = _get_combined_capacity(
                term=section.offering.term,
                sections=self.sections,
                defaults={
                    "capacity": self.capacity,
                    "wait_list_capacity": self.wait_list_capacity,
                    "nso_enrollment_capacity": self.nso_enrollment_capacity,
                },
            )

            log.debug("Updated %s", individual_availability.combined_capacity)

            individual_availability.save()


class RawSectionAvailability(RawDictionary):
    def __init__(self, spire_id: str, table: dict[str, Any]) -> None:
        self._is_combined = "Individual Availability" in table

        if self._is_combined:
            self.combined_capacity = RawSectionCombinedCapacity(
                table["Combined Availability"]
            )
            log.debug("Scraped combined capacity:\n%s", self.combined_capacity)
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
        availability, created = super().push(section=section)

        if self._is_combined:
            self.combined_capacity.push(individual_availability=availability)

        return availability, created
