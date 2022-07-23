from django.core.management.base import BaseCommand

from spire.models import Course, Section, SectionV2
from spire.scraper.classes.normalizers import DESCRIPTION_NOT_AVAILABLE_TO_NONE, REPLACE_DOUBLE_SPACE


def fix_description_not_available(qs):
    for x in qs:
        old = x.description
        x.description = DESCRIPTION_NOT_AVAILABLE_TO_NONE(x.description)
        print(f"{old} -> {x.description}")
        x.save()


class Command(BaseCommand):
    help = "Random scripts to fix data."

    def handle(self, *args, **options):
        # for x in Section.objects.raw("select * from spire_section where position('  ' in course_title) > 0"):
        #     old = x.course_title
        #     x.course_title = REPLACE_DOUBLE_SPACE(x.course_title)

        #     print(f"{old} -> {x.course_title}")
        #     x.save()

        # for x in Course.objects.raw("select * from spire_course where position('  ' in title) > 0"):
        #     old = x.title
        #     x.title = REPLACE_DOUBLE_SPACE(x.title)
        #     print(f"{old} -> {x.course_title}")
        #     x.save()

        # fix_description_not_available(Section.objects.filter(description__icontains=("not available")))
        # fix_description_not_available(Course.objects.filter(description__icontains=("not available")))

        for old_section in Section.objects.filter(overview__isnull=False):
            new_section = SectionV2.objects.get(id=old_section.id)

            new_section.overview = old_section.overview
            new_section.save()
