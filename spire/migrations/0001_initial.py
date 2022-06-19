# Generated by Django 4.0.5 on 2022-06-19 09:24

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.CharField(max_length=32, primary_key=True, serialize=False, validators=[django.core.validators.RegexValidator(message='must be a course ID (match course ID RegExp)', regex='^(?P<subject_id>[A-Z\\-]{2,9}[A-Z]) (?P<course_number>[\\x00-\\x7F]{1,9}[A-Za-z0-9])$')])),
                ('number', models.CharField(max_length=16, validators=[django.core.validators.RegexValidator(message='must be a course ID number (match course title number RegExp)', regex='^(?P<course_number>[\\x00-\\x7F]{1,9}[A-Za-z0-9])$')])),
                ('title', models.CharField(max_length=256, validators=[django.core.validators.RegexValidator(message='must be a course title (match course title RegExp)', regex='^(?P<course_title>[\\x00-\\x7F]{3,256})$')])),
                ('description', models.CharField(max_length=4096, null=True)),
                ('_updated_at', models.DateTimeField()),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.CharField(max_length=32, primary_key=True, serialize=False, validators=[django.core.validators.RegexValidator(message='must be a section id (match the id RegExp', regex='^(?P<section_id>\\d{2,4}([A-Z]{1,4})?-[A-Z]{1,4}\\(\\d{3,10}\\))$')])),
                ('course_id', models.CharField(max_length=32, validators=[django.core.validators.RegexValidator(message='must be a course ID (match course ID RegExp)', regex='^(?P<subject_id>[A-Z\\-]{2,9}[A-Z]) (?P<course_number>[\\x00-\\x7F]{1,9}[A-Za-z0-9])$')])),
                ('term', models.CharField(max_length=16, validators=[django.core.validators.RegexValidator(message='must be a term (match the term RegExp)', regex='^(Spring|Summer|Winter|Fall) (20\\d{2})$')])),
                ('meeting_information', models.JSONField()),
                ('restrictions', models.JSONField(null=True)),
                ('availability', models.JSONField()),
                ('description', models.CharField(max_length=1024, null=True)),
                ('overview', models.CharField(max_length=1024, null=True)),
                ('_updated_at', models.DateTimeField()),
            ],
            options={
                'ordering': ['term', 'course_id', 'id'],
            },
        ),
        migrations.CreateModel(
            name='SectionCoverage',
            fields=[
                ('term', models.CharField(max_length=32, primary_key=True, serialize=False, validators=[django.core.validators.RegexValidator(message='must be a term (match the term RegExp)', regex='^(Spring|Summer|Winter|Fall) (20\\d{2})$')])),
                ('completed', models.BooleanField(default=False)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField(null=True)),
            ],
            options={
                'ordering': ['term'],
            },
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('email', models.EmailField(max_length=254, null=True)),
            ],
            options={
                'ordering': ['name', 'email'],
            },
        ),
        migrations.CreateModel(
            name='CourseDetail',
            fields=[
                ('course', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='details', serialize=False, to='spire.course')),
                ('career', models.CharField(max_length=32, null=True)),
                ('units', models.CharField(max_length=16, null=True)),
                ('grading_basis', models.CharField(max_length=32, null=True)),
                ('course_components', models.JSONField(default=list, null=True)),
                ('academic_group', models.CharField(max_length=128, null=True)),
                ('academic_organization', models.CharField(max_length=128, null=True)),
                ('campus', models.CharField(max_length=64, null=True)),
            ],
            options={
                'ordering': ['course'],
            },
        ),
        migrations.CreateModel(
            name='CourseEnrollmentInformation',
            fields=[
                ('course', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='enrollment_information', serialize=False, to='spire.course')),
                ('add_consent', models.CharField(max_length=512, null=True)),
                ('enrollment_requirement', models.CharField(max_length=512, null=True)),
                ('course_attribute', models.JSONField(default=list, null=True)),
            ],
            options={
                'ordering': ['course'],
            },
        ),
        migrations.CreateModel(
            name='SectionDetail',
            fields=[
                ('section', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='details', serialize=False, to='spire.section')),
                ('status', models.CharField(max_length=32)),
                ('class_number', models.IntegerField()),
                ('units', models.CharField(max_length=32)),
                ('class_components', models.JSONField()),
                ('career', models.CharField(max_length=32)),
                ('grading', models.CharField(max_length=32)),
                ('gened', models.CharField(max_length=32)),
                ('rap_tap_hcl', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('title', models.CharField(max_length=64, unique=True, validators=[django.core.validators.RegexValidator(message='must be a title (match subject title RegExp)', regex='^(?P<subject_title>[\\x00-\\x7F]{3,99})$')])),
                ('id', models.CharField(max_length=8, primary_key=True, serialize=False, unique=True, validators=[django.core.validators.RegexValidator(message='must be a  title (match subject id RegExp)', regex='^(?P<subject_id>[A-Z\\-]{2,9}[A-Z])$')])),
                ('courses', models.ManyToManyField(related_name='subject', to='spire.course')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='section',
            name='instructors',
            field=models.ManyToManyField(to='spire.staff'),
        ),
        migrations.AddField(
            model_name='course',
            name='sections',
            field=models.ManyToManyField(related_name='+', to='spire.section'),
        ),
    ]
