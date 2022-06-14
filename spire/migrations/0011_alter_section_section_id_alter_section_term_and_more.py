# Generated by Django 4.0.5 on 2022-06-14 18:09

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spire', '0010_alter_course_number_alter_subject_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='section_id',
            field=models.CharField(max_length=10, primary_key=True, serialize=False, validators=[django.core.validators.RegexValidator(message='must be a section id (match the id RegExp', regex='^(?P<section_id>.{3,10})$')]),
        ),
        migrations.AlterField(
            model_name='section',
            name='term',
            field=models.CharField(max_length=16, validators=[django.core.validators.RegexValidator(message='must be a term (match the term RegExp)', regex='^(Spring|Summer|Winter|Fall) (20\\d{2})$')]),
        ),
        migrations.AlterField(
            model_name='subject',
            name='title',
            field=models.CharField(max_length=64, unique=True, validators=[django.core.validators.RegexValidator(message='must be a title (match subject title RegExp)', regex='^(?P<subject_title>[\\x00-\\x7F]{3,99})$')]),
        ),
        migrations.DeleteModel(
            name='Term',
        ),
    ]
