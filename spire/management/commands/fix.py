from django.core.management.base import BaseCommand

from spire.models import Course, Section


def REPLACE_DOUBLE_SPACE(s):
    while "  " in s:
        s = s.replace("  ", " ")

    return s


class Command(BaseCommand):
    help = "Random scripts to fix data."

    def handle(self, *args, **options):
        for x in Section.objects.raw("select * from spire_section where position('  ' in course_title) > 0"):
            x.course_title = REPLACE_DOUBLE_SPACE(x.course_title)
            x.save()

        for x in Course.objects.raw("select * from spire_course where position('  ' in title) > 0"):
            x.title = REPLACE_DOUBLE_SPACE(x.title)
            x.save()

        for x in Section.objects.filter(description="Not available at this time"):
            x.description = None
            x.save()
