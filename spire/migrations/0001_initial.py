# Generated by Django 4.0.5 on 2022-06-06 17:22

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
                ('course_id', models.CharField(max_length=32, primary_key=True, serialize=False, validators=[django.core.validators.RegexValidator(message='must be a course ID (match course ID RegExp)', regex='^.+$')])),
                ('number', models.CharField(max_length=8, validators=[django.core.validators.RegexValidator(message='must be a course ID number (match course title number RegExp)', regex='^.+$')])),
                ('title', models.CharField(max_length=128, validators=[django.core.validators.RegexValidator(message='must be a course title (match course title RegExp)', regex='^.+$')])),
                ('description', models.CharField(max_length=1024, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SectionCoverage',
            fields=[
                ('term', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('completed', models.BooleanField(default=False)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('staff_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('email', models.EmailField(max_length=254, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('name', models.CharField(max_length=30, unique=True, validators=[django.core.validators.RegexValidator(message='must be a  title (match subject title RegExp)', regex='^.+$')])),
                ('subject_id', models.CharField(max_length=8, primary_key=True, serialize=False, unique=True, validators=[django.core.validators.RegexValidator(message='must be a  title (match subject id RegExp)', regex='^.+$')])),
            ],
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('term_id', models.AutoField(primary_key=True, serialize=False)),
                ('year', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(2010), django.core.validators.MaxValueValidator(2050)])),
                ('season', models.CharField(choices=[('S', 'Spring'), ('SU', 'Summer'), ('F', 'Fall'), ('W', 'Winter')], max_length=2)),
            ],
            options={
                'unique_together': {('year', 'season')},
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('section_id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('details', models.JSONField()),
                ('restrictions', models.JSONField(null=True)),
                ('availability', models.JSONField()),
                ('description', models.CharField(max_length=1024, null=True)),
                ('overview', models.CharField(max_length=1024, null=True)),
                ('meeting_info', models.JSONField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spire.course')),
                ('instructors', models.ManyToManyField(to='spire.staff')),
                ('term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spire.term')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spire.subject'),
        ),
        migrations.AlterUniqueTogether(
            name='course',
            unique_together={('subject', 'number')},
        ),
    ]
