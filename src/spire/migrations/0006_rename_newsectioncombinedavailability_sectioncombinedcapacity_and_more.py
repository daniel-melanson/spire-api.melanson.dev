# Generated by Django 4.2.6 on 2023-10-26 17:22

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("spire", "0005_alter_newsectioncombinedavailability_capacity_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="NewSectionCombinedAvailability",
            new_name="SectionCombinedCapacity",
        ),
        migrations.RenameField(
            model_name="sectionavailability",
            old_name="new_combined_availability",
            new_name="combined_capacity",
        ),
    ]