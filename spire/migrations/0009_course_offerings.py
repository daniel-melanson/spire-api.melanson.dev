# Generated by Django 4.0.6 on 2022-07-23 03:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spire', '0008_courseoffering_sectionv2'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='offerings',
            field=models.ManyToManyField(related_name='+', to='spire.courseoffering'),
        ),
    ]
