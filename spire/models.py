from datetime import datetime

from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from spire.regexp import (
    COURSE_ID_NUM_REGEXP,
    COURSE_ID_REGEXP,
    COURSE_TITLE_REGEXP,
    SUBJECT_ID_REGEXP,
    SUBJECT_TITLE_REGEXP,
)


def re_validator_factory(r: str, msg: str):
    assert r.startswith("^") == r.endswith("$")

    if not r.startswith("^"):
        r = "^" + r + "$"

    return RegexValidator(regex=r, message=msg)


_course_id_validator = re_validator_factory(COURSE_ID_REGEXP, "must be a course ID (match course ID RegExp)")

_course_id_number_validator = re_validator_factory(
    COURSE_ID_NUM_REGEXP,
    "must be a course ID number (match course title number RegExp)",
)

_course_title_validator = re_validator_factory(
    COURSE_TITLE_REGEXP, "must be a course title (match course title RegExp)"
)

_subject_id_validator = re_validator_factory(SUBJECT_ID_REGEXP, "must be a  title (match subject id RegExp)")

_subject_title_validator = re_validator_factory(
    SUBJECT_TITLE_REGEXP, "must be a  title (match subject title RegExp)"
)


class Term(models.Model):
    term_id = models.AutoField(primary_key=True)
    year = models.SmallIntegerField(validators=[MinValueValidator(2010), MaxValueValidator(2050)])
    season = models.CharField(
        max_length=2,
        choices=[("S", "Spring"), ("SU", "Summer"), ("F", "Fall"), ("W", "Winter")],
    )

    class Meta:
        unique_together = [["year", "season"]]


class Subject(models.Model):
    name = models.CharField(max_length=30, unique=True, validators=[_subject_title_validator])
    subject_id = models.CharField(
        max_length=8,
        unique=True,
        primary_key=True,
        validators=[_subject_id_validator],
    )


class Course(models.Model):
    course_id = models.CharField(max_length=32, primary_key=True, validators=[_course_id_validator])
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    number = models.CharField(max_length=8, validators=[_course_id_number_validator])
    title = models.CharField(max_length=128, validators=[_course_title_validator])
    description = models.CharField(max_length=1024, null=True)
    _updated_at = models.DateTimeField(default=datetime.fromisoformat("2022-05-01T00:00:00.000+00:00"))

    class Meta:
        unique_together = [["subject", "number"]]


class Staff(models.Model):
    staff_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    email = models.EmailField(null=True)


class Section(models.Model):
    section_id = models.CharField(max_length=10, primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    details = models.JSONField()
    restrictions = models.JSONField(null=True)
    availability = models.JSONField()
    description = models.CharField(max_length=1024, null=True)
    overview = models.CharField(max_length=1024, null=True)
    meeting_info = models.JSONField()
    instructors = models.ManyToManyField(Staff)
    _updated_at = models.DateTimeField(default=datetime.fromisoformat("2022-05-01T00:00:00.000+00:00"))


class SectionCoverage(models.Model):
    term = models.CharField(max_length=32, primary_key=True)
    completed = models.BooleanField(default=False)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
