# Generated by Django 4.1.1 on 2022-09-16 22:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("spire", "0002_alter_buildingroom_building"),
    ]

    operations = [
        migrations.AlterField(
            model_name="buildingroom",
            name="alt",
            field=models.CharField(max_length=64, unique=True),
        ),
    ]