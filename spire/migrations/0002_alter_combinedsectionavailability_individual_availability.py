# Generated by Django 4.0.5 on 2022-06-29 14:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('spire', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='combinedsectionavailability',
            name='individual_availability',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='combined_availability', serialize=False, to='spire.sectionavailability'),
        ),
    ]
