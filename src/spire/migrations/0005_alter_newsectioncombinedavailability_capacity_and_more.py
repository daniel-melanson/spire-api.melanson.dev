# Generated by Django 4.2.6 on 2023-10-26 17:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("spire", "0004_newsectioncombinedavailability_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="newsectioncombinedavailability",
            name="capacity",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="newsectioncombinedavailability",
            name="nso_enrollment_capacity",
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name="newsectioncombinedavailability",
            name="wait_list_capacity",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="sectionavailability",
            name="available_seats",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="sectionavailability",
            name="capacity",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="sectionavailability",
            name="enrollment_total",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="sectionavailability",
            name="nso_enrollment_capacity",
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name="sectionavailability",
            name="wait_list_capacity",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="sectionavailability",
            name="wait_list_total",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="term",
            name="ordinal",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="term",
            name="year",
            field=models.PositiveIntegerField(),
        ),
    ]
