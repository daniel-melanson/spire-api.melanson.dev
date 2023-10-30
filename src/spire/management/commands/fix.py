from django.core.management.base import BaseCommand

from spire.models import (
    CourseDetail,
    Section,
    SectionAvailability,
    SectionCombinedAvailability,
    SectionCombinedCapacity,
)


def _get_combined_capacity(sections, term, defaults):
    for sprie_id in sections:
        try:
            section = Section.objects.get(offering__term=term, spire_id=sprie_id)

            availability = section.availability
            if availability and availability.combined_capacity:
                return availability.combined_capacity
        except Section.DoesNotExist:  # type: ignore
            continue

    return SectionCombinedCapacity.objects.create(**defaults)


class Command(BaseCommand):
    help = "Random scripts to fix data."

    def handle(self, *args, **options):
        SectionCombinedCapacity.objects.all().delete()

        for combined_availability in SectionCombinedAvailability.objects.all():
            individual_availability = combined_availability.individual_availability
            section = individual_availability.section
            term = section.offering.term

            section_ids = set(combined_availability.sections)
            section_ids.add(section.spire_id)

            combined_capacity = _get_combined_capacity(
                sections=section_ids,
                term=term,
                defaults={
                    "capacity": combined_availability.capacity,
                    "wait_list_capacity": combined_availability.wait_list_capacity,
                    "nso_enrollment_capacity": combined_availability.nso_enrollment_capacity,
                },
            )

            individual_availability.combined_capacity = combined_capacity
            individual_availability.save()
