import json

from django.core.management.base import BaseCommand

from spire.models import Course, CourseDetail


def get_or_set_default(table, key, default):
    if key in table:
        return table[key]
    else:
        table[key] = default
        return default


class Command(BaseCommand):
    help = "Testing for queries."

    def handle(self, *args, **options):

        group = {}
        organization = {}

        for course_detail in CourseDetail.objects.all():
            subject = course_detail.course.subject

            subject_groups = get_or_set_default(group, subject.id, set())
            subject_organizations = get_or_set_default(organization, subject.id, set())

            subject_groups.add(course_detail.academic_group)
            subject_organizations.add(course_detail.academic_organization)

        print(json.dumps({k: list(v) for k, v in group.items()}, indent=4))
        print(json.dumps({k: list(v) for k, v in organization.items()}, indent=4))
