

from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from spire.regexp import (
    COURSE_ID_NUM_REGEXP,
    COURSE_ID_REGEXP,
    COURSE_TITLE_REGEXP,
    SECTION_ID_REGEXP,
    SECTION_TERM_REGEXP,
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
    SUBJECT_TITLE_REGEXP, "must be a title (match subject title RegExp)"
)

_section_id_validator = re_validator_factory(SECTION_ID_REGEXP, "must be a section id (match the id RegExp")

_section_term_validator = re_validator_factory(SECTION_TERM_REGEXP, "must be a term (match the term RegExp)")


class Subject(models.Model):
    title = models.CharField(max_length=64, unique=True, validators=[_subject_title_validator])
    id = models.CharField(
        max_length=8,
        unique=True,
        primary_key=True,
        validators=[_subject_id_validator],
    )
    courses = models.ManyToManyField("Course", related_name="+")

    class Meta:
        ordering = ["id"]


class Course(models.Model):
    id = models.CharField(max_length=32, primary_key=True, validators=[_course_id_validator])
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    number = models.CharField(max_length=16, validators=[_course_id_number_validator])
    title = models.CharField(max_length=256, validators=[_course_title_validator])
    description = models.CharField(max_length=4096, null=True)
    details = models.JSONField(default=dict)
    enrollment_information = models.JSONField(null=True)
    sections = models.ManyToManyField("Section", related_name="+")
    _updated_at = models.DateTimeField()

    class Meta:
        unique_together = [["subject", "number"]]
        ordering = ["id"]


class Staff(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    email = models.EmailField(null=True)

    class Meta:
        ordering = ["email"]


class Section(models.Model):
    id = models.CharField(max_length=10, primary_key=True, validators=[_section_id_validator])
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    term = models.CharField(max_length=16, validators=[_section_term_validator])
    details = models.JSONField()
    restrictions = models.JSONField(null=True)
    availability = models.JSONField()
    description = models.CharField(max_length=1024, null=True)
    overview = models.CharField(max_length=1024, null=True)
    meeting_info = models.JSONField()
    instructors = models.ManyToManyField(Staff)
    _updated_at = models.DateTimeField()

    class Meta:
        ordering = ["term", "course", "id"]


class SectionCoverage(models.Model):
    term = models.CharField(max_length=32, primary_key=True, validators=[_section_term_validator])
    completed = models.BooleanField(default=False)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)

    class Meta:
        ordering = ["term"]
