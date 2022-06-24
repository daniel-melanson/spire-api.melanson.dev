from django.core.validators import RegexValidator
from django.db import models

from spire.patterns import (
    COURSE_ID_NUM_REGEXP,
    COURSE_ID_REGEXP,
    COURSE_TITLE_REGEXP,
    SECTION_ID_REGEXP,
    SUBJECT_ID_REGEXP,
    SUBJECT_TITLE_REGEXP,
    TERM_REGEXP,
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

_section_term_validator = re_validator_factory(TERM_REGEXP, "must be a term (match the term RegExp)")


class Subject(models.Model):
    title = models.CharField(max_length=64, unique=True, validators=[_subject_title_validator])
    id = models.CharField(
        max_length=8,
        unique=True,
        primary_key=True,
        validators=[_subject_id_validator],
    )

    class Meta:
        ordering = ["id"]


class Course(models.Model):
    id = models.CharField(max_length=32, primary_key=True, validators=[_course_id_validator])
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="courses")
    number = models.CharField(max_length=16, validators=[_course_id_number_validator])
    title = models.CharField(max_length=256, validators=[_course_title_validator])
    description = models.CharField(max_length=4096, null=True)
    sections = models.ManyToManyField("Section", related_name="+")
    _updated_at = models.DateTimeField()

    class Meta:
        unique_together = ["subject", "number"]
        ordering = ["id"]


class CourseDetail(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, primary_key=True, related_name="details")
    career = models.CharField(null=True, max_length=32)
    units = models.CharField(null=True, max_length=16)
    grading_basis = models.CharField(null=True, max_length=32)
    course_components = models.JSONField(null=True, default=list)
    academic_group = models.CharField(null=True, max_length=128)
    academic_organization = models.CharField(null=True, max_length=128)
    campus = models.CharField(null=True, max_length=64)

    class Meta:
        ordering = ["course"]


class CourseEnrollmentInformation(models.Model):
    course = models.OneToOneField(
        "Course",
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="enrollment_information",
    )
    add_consent = models.CharField(null=True, max_length=512)
    enrollment_requirement = models.CharField(null=True, max_length=512)
    course_attribute = models.JSONField(null=True, default=list)

    class Meta:
        ordering = ["course"]


class Instructor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True)
    email = models.EmailField(null=True)

    class Meta:
        ordering = ["name", "email"]


class Section(models.Model):
    id = models.CharField(max_length=32, primary_key=True, validators=[_section_id_validator])
    course_id = models.CharField(max_length=32, validators=[_course_id_validator])
    term = models.CharField(max_length=16, validators=[_section_term_validator])
    restrictions = models.JSONField(null=True)
    availability = models.JSONField()
    description = models.CharField(max_length=4096, null=True)
    overview = models.CharField(max_length=2048, null=True)
    _updated_at = models.DateTimeField()

    class Meta:
        ordering = ["term", "course_id", "id"]


class MeetingInformation(models.Model):
    id = models.AutoField(primary_key=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="meeting_information")
    days_and_times = models.CharField(max_length=64)
    room = models.CharField(max_length=64)
    instructors = models.ManyToManyField(Instructor, "+")
    meeting_dates = models.CharField(max_length=64)

    class Meta:
        unique_together = [["section", "room", "days_and_times"]]
        ordering = ["section", "days_and_times"]


class SectionDetail(models.Model):
    section = models.OneToOneField(
        Section, on_delete=models.CASCADE, primary_key=True, related_name="details"
    )
    status = models.CharField(null=True, max_length=64)
    class_number = models.IntegerField()
    session = models.CharField(null=True, max_length=64)
    units = models.CharField(null=True, max_length=64)
    class_components = models.JSONField(null=True)
    career = models.CharField(null=True, max_length=64)
    topic = models.CharField(null=True, max_length=64)
    grading = models.CharField(null=True, max_length=64)
    gened = models.JSONField(null=True)
    rap_tap_hlc = models.CharField(null=True, max_length=64)

    class Meta:
        ordering = ["section"]


class SectionCoverage(models.Model):
    term = models.CharField(max_length=32, primary_key=True, validators=[_section_term_validator])
    completed = models.BooleanField(default=False)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)

    class Meta:
        ordering = ["term"]
