# Generated by Django 4.1.1 on 2022-09-25 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("spire", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sectionmeetinginformation",
            name="instructors",
            field=models.ManyToManyField(
                related_name="sections", to="spire.instructor"
            ),
        ),
    ]