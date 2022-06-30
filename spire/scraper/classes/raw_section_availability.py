import logging

from spire.models import CombinedSectionAvailability, Section, SectionAvailability

from .shared import RawDictionary, RawField

log = logging.getLogger(__name__)

AVAILABILITY_FIELDS = [
    RawField(k="Capacity"),
    RawField(k="Enrollment Total"),
    RawField(k="Available Seats"),
    RawField(k="Wait List Capacity"),
    RawField(k="Wait List Total"),
]


class RawCombinedSectionAvailability(RawDictionary):
    def __init__(self, section_id: str, table: dict[str, str]) -> None:
        self.section_id = section_id

        super().__init__(
            CombinedSectionAvailability,
            table,
            fields=[RawField(k="combined_sections"), *AVAILABILITY_FIELDS],
        )

    def push(self, individual_availability: SectionAvailability):
        return super().push(individual_availability=individual_availability)


class RawSectionAvailability(RawDictionary):
    def __init__(self, section_id: str, table: dict[str, str]) -> None:
        self.section_id = section_id
        self._is_combined = "Individual Availability" in table

        table["Capacity"] = table["Total Enrollment Capacity"]
        del table["Total Enrollment Capacity"]

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
