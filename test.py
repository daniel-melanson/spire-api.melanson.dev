import os

import django

os.environ["DJANGO_SETTINGS_MODULE"] = "root.settings"
django.setup()

from spire.models import Section, SectionDetail

for x in SectionDetail.objects.filter(units__isnull=True):
    print(x.section.term + " " + x.section_id)

