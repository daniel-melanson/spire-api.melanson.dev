from django.core.management.base import BaseCommand

from spire.models import CourseDetail


class Command(BaseCommand):
    help = "Random scripts to fix data."

    def handle(self, *args, **options):
        for x in CourseDetail.objects.filter(grading_basis="Grad Ltr Grading, with options"):
            x.grading_basis = "Graduate Letter Grading, with options"
            x.save()
