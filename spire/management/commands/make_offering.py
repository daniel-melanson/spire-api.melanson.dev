from django.core.management.base import BaseCommand

from spire.models import Course, CourseOffering, Section, SectionV2


class Command(BaseCommand):
    help = "Makes course offerings from section."

    def handle(self, *args, **options):
        for old_section in Section.objects.all():
            if SectionV2.objects.filter(id=old_section.id).first():
                print(f"Section {old_section} is already a SectionV2")
                continue

            course_id = old_section.course_id

            [_, course_id_number] = course_id.split(" ")

            course, created = Course.objects.get_or_create(
                id=course_id,
                defaults={
                    "subject": old_section.subject,
                    "number": course_id_number,
                    "title": old_section.course_title,
                    "description": None,
                    "_updated_at": old_section._updated_at,
                },
            )

            print(f"{'Created' if created else 'Got'} course {course}")

            offering, created = CourseOffering.objects.get_or_create(
                course=course,
                term=old_section.term,
                defaults={
                    "alternative_title": old_section.course_title
                    if old_section.course_title != course.title
                    else None,
                    "subject": course.subject,
                },
            )

            print(f"{'Created' if created else 'Got'} offering {offering}")

            new_section = SectionV2.objects.create(
                id=old_section.id,
                offering=offering,
                description=old_section.description,
                _updated_at=old_section._updated_at,
            )

            print(f"Created new section {new_section}")
