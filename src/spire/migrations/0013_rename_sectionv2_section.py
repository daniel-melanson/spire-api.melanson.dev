# Generated by Django 4.0.6 on 2022-07-23 04:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spire', '0012_delete_section'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SectionV2',
            new_name='Section',
        ),
    ]