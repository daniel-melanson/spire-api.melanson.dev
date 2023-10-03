# Generated by Django 4.1.1 on 2022-09-16 23:03

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AcademicGroup",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=64, unique=True)),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="Building",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=64, unique=True)),
                ("address", models.CharField(max_length=64, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="BuildingRoom",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("number", models.CharField(max_length=8, null=True)),
                ("alt", models.CharField(max_length=64, unique=True)),
                (
                    "building",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rooms",
                        to="spire.building",
                    ),
                ),
            ],
            options={
                "ordering": ["building", "number"],
                "unique_together": {("building", "number")},
            },
        ),
        migrations.CreateModel(
            name="Course",
            fields=[
                (
                    "id",
                    models.CharField(
                        max_length=32,
                        primary_key=True,
                        serialize=False,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="must be a course ID (match course ID RegExp)",
                                regex="^(?P<subject_id>[A-Z\\-@]{2,9}[A-Z]) (?P<course_number>[\\x00-\\x7F]{0,9}[A-Za-z0-9])$",
                            )
                        ],
                    ),
                ),
                (
                    "number",
                    models.CharField(
                        max_length=16,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="must be a course ID number (match course title number RegExp)",
                                regex="^(?P<course_number>[\\x00-\\x7F]{0,9}[A-Za-z0-9])$",
                            )
                        ],
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        max_length=256,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="must be a course title (match course title RegExp)",
                                regex="^(?P<course_title>[\\x00-\\x7F]{3,256})$",
                            )
                        ],
                    ),
                ),
                ("description", models.CharField(max_length=4096, null=True)),
                ("_updated_at", models.DateTimeField()),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="CourseOffering",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("alternative_title", models.CharField(max_length=256, null=True)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="offerings",
                        to="spire.course",
                    ),
                ),
            ],
            options={
                "ordering": ["term", "course"],
            },
        ),
        migrations.CreateModel(
            name="CourseUnits",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("base", models.FloatField(null=True)),
                ("min", models.FloatField(null=True)),
                ("max", models.FloatField(null=True)),
            ],
            options={
                "ordering": ["base"],
            },
        ),
        migrations.CreateModel(
            name="Instructor",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=64, unique=True)),
                ("email", models.EmailField(max_length=254, null=True)),
            ],
            options={
                "ordering": ["name", "email"],
            },
        ),
        migrations.CreateModel(
            name="Section",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "spire_id",
                    models.CharField(
                        max_length=32,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="must be a section id (match the id RegExp",
                                regex="^(?P<section_id>([A-Z0-9]{1,6})-[A-Z]{1,4}\\(\\d{3,10}\\))$",
                            )
                        ],
                    ),
                ),
                ("description", models.CharField(max_length=4096, null=True)),
                ("overview", models.CharField(max_length=32768, null=True)),
                ("_updated_at", models.DateTimeField()),
                (
                    "offering",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sections",
                        to="spire.courseoffering",
                    ),
                ),
            ],
            options={
                "ordering": ["offering", "spire_id"],
            },
        ),
        migrations.CreateModel(
            name="SectionMeetingInformation",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("room_raw", models.CharField(max_length=64)),
                (
                    "instructors",
                    models.ManyToManyField(related_name="+", to="spire.instructor"),
                ),
                (
                    "room",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="spire.buildingroom",
                    ),
                ),
                (
                    "section",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="meeting_information",
                        to="spire.section",
                    ),
                ),
            ],
            options={
                "ordering": ["section"],
            },
        ),
        migrations.CreateModel(
            name="Term",
            fields=[
                (
                    "id",
                    models.CharField(
                        max_length=32,
                        primary_key=True,
                        serialize=False,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="must be a term (match the term RegExp)",
                                regex="^(Spring|Summer|Winter|Fall) (20\\d{2})$",
                            )
                        ],
                    ),
                ),
                ("season", models.CharField(max_length=16)),
                ("year", models.IntegerField()),
                ("ordinal", models.IntegerField()),
                ("start_date", models.DateField(default=None, null=True)),
                ("end_date", models.DateField(default=None, null=True)),
            ],
            options={
                "ordering": ["ordinal"],
                "unique_together": {("year", "season")},
            },
        ),
        migrations.CreateModel(
            name="CourseEnrollmentInformation",
            fields=[
                (
                    "course",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="enrollment_information",
                        serialize=False,
                        to="spire.course",
                    ),
                ),
                ("add_consent", models.CharField(max_length=512, null=True)),
                ("enrollment_requirement", models.CharField(max_length=512, null=True)),
                ("course_attribute", models.JSONField(default=list, null=True)),
            ],
            options={
                "ordering": ["course"],
            },
        ),
        migrations.CreateModel(
            name="SectionAvailability",
            fields=[
                (
                    "section",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="availability",
                        serialize=False,
                        to="spire.section",
                    ),
                ),
                ("capacity", models.IntegerField()),
                ("enrollment_total", models.IntegerField()),
                ("available_seats", models.IntegerField()),
                ("wait_list_capacity", models.IntegerField()),
                ("wait_list_total", models.IntegerField()),
                (
                    "nso_enrollment_capacity",
                    models.IntegerField(default=None, null=True),
                ),
            ],
            options={
                "ordering": ["section"],
            },
        ),
        migrations.CreateModel(
            name="SectionCoverage",
            fields=[
                (
                    "term",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to="spire.term",
                    ),
                ),
                ("completed", models.BooleanField(default=False)),
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField(null=True)),
            ],
            options={
                "ordering": ["term"],
            },
        ),
        migrations.CreateModel(
            name="SectionMeetingSchedule",
            fields=[
                (
                    "meeting_information",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="schedule",
                        serialize=False,
                        to="spire.sectionmeetinginformation",
                    ),
                ),
                ("days", models.JSONField()),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
            ],
            options={
                "ordering": ["meeting_information", "start_time"],
            },
        ),
        migrations.CreateModel(
            name="SectionRestriction",
            fields=[
                (
                    "section",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="restrictions",
                        serialize=False,
                        to="spire.section",
                    ),
                ),
                ("drop_consent", models.CharField(max_length=4096, null=True)),
                (
                    "enrollment_requirements",
                    models.CharField(max_length=4096, null=True),
                ),
                ("add_consent", models.CharField(max_length=4096, null=True)),
            ],
            options={
                "ordering": ["section"],
            },
        ),
        migrations.CreateModel(
            name="TermEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("description", models.CharField(max_length=256)),
                (
                    "term",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        to="spire.term",
                    ),
                ),
            ],
            options={
                "ordering": ["term", "date"],
            },
        ),
        migrations.CreateModel(
            name="Subject",
            fields=[
                (
                    "id",
                    models.CharField(
                        max_length=8,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="must be a  title (match subject id RegExp)",
                                regex="^(?P<subject_id>[A-Z\\-@]{2,9}[A-Z])$",
                            )
                        ],
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        max_length=64,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="must be a title (match subject title RegExp)",
                                regex="^(?P<subject_title>[\\x00-\\x7F]{3,99})$",
                            )
                        ],
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        related_name="subjects", to="spire.academicgroup"
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="SectionMeetingDates",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start", models.DateField()),
                ("end", models.DateField()),
                (
                    "meeting_information",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="meeting_dates",
                        to="spire.sectionmeetinginformation",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="courseoffering",
            name="subject",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="offerings",
                to="spire.subject",
            ),
        ),
        migrations.AddField(
            model_name="courseoffering",
            name="term",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="spire.term",
            ),
        ),
        migrations.AddField(
            model_name="course",
            name="subject",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="courses",
                to="spire.subject",
            ),
        ),
        migrations.CreateModel(
            name="SectionCombinedAvailability",
            fields=[
                (
                    "individual_availability",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="combined_availability",
                        serialize=False,
                        to="spire.sectionavailability",
                    ),
                ),
                ("sections", models.JSONField()),
                ("capacity", models.IntegerField()),
                ("enrollment_total", models.IntegerField()),
                ("available_seats", models.IntegerField()),
                ("wait_list_capacity", models.IntegerField()),
                ("wait_list_total", models.IntegerField()),
                (
                    "nso_enrollment_capacity",
                    models.IntegerField(default=None, null=True),
                ),
            ],
            options={
                "ordering": ["individual_availability"],
            },
        ),
        migrations.CreateModel(
            name="SectionDetail",
            fields=[
                (
                    "section",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="details",
                        serialize=False,
                        to="spire.section",
                    ),
                ),
                ("status", models.CharField(max_length=64, null=True)),
                ("class_number", models.IntegerField()),
                ("session", models.CharField(max_length=64, null=True)),
                ("class_components", models.JSONField(null=True)),
                ("career", models.CharField(max_length=64, null=True)),
                ("topic", models.CharField(max_length=64, null=True)),
                ("grading", models.CharField(max_length=64, null=True)),
                ("gened", models.JSONField(null=True)),
                ("rap_tap_hlc", models.CharField(max_length=64, null=True)),
                (
                    "units",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="spire.courseunits",
                    ),
                ),
            ],
            options={
                "ordering": ["section"],
            },
        ),
        migrations.AlterUniqueTogether(
            name="courseoffering",
            unique_together={("course", "term")},
        ),
        migrations.CreateModel(
            name="CourseDetail",
            fields=[
                (
                    "course",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="details",
                        serialize=False,
                        to="spire.course",
                    ),
                ),
                ("career", models.CharField(max_length=32, null=True)),
                ("grading_basis", models.CharField(max_length=64, null=True)),
                ("course_components", models.JSONField(default=list, null=True)),
                ("academic_group", models.CharField(max_length=128, null=True)),
                ("academic_organization", models.CharField(max_length=128, null=True)),
                ("campus", models.CharField(max_length=64, null=True)),
                (
                    "units",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="spire.courseunits",
                    ),
                ),
            ],
            options={
                "ordering": ["course"],
            },
        ),
        migrations.AlterUniqueTogether(
            name="course",
            unique_together={("subject", "number")},
        ),
    ]
