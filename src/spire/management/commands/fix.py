from django.core.management.base import BaseCommand

from spire.models import Subject
from spire.scraper.classes.groups.raw_subject import SUBJECT_OVERRIDES


class Command(BaseCommand):
    help = "Random scripts to fix data."

    def handle(self, *args, **options):
        for s in Subject.objects.all():
            if s.id not in SUBJECT_OVERRIDES:
                continue

            id = s.id
            print(id, s.title, SUBJECT_OVERRIDES[id][1])
            _, s.title = SUBJECT_OVERRIDES[id]
            s.save()
