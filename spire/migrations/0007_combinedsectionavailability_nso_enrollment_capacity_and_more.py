# Generated by Django 4.0.6 on 2022-07-14 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spire', '0006_sectionavailability_nso_enrollment_capacity'),
    ]

    operations = [
        migrations.AddField(
            model_name='combinedsectionavailability',
            name='nso_enrollment_capacity',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='sectionavailability',
            name='nso_enrollment_capacity',
            field=models.IntegerField(default=None, null=True),
        ),
    ]
