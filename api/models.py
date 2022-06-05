import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

COURSE_ID_REGEXP = r"^[A-Z]{3,10} $"
COURSE_ID_NUMBER_REGEXP = r"^$"
COURSE_TITLE_REGEXP = r"^$"


def validation_generator(f, msg):
    def validator(value: str):
        if not f(value):
            raise ValidationError(
                _("%(value)s %(msg)s"), params={"value": value, "msg": msg}
            )

    return validator


validate_alphabetic = validation_generator(lambda x: x.isalpha(), "must be alphabetic")

validate_upper = validation_generator(lambda x: x.isupper(), "must be uppercase")

validate_course_id = validation_generator(
    lambda x: re.match(COURSE_ID_REGEXP, x), "must be a course ID"
)

validate_course_id_number = validation_generator(
    lambda x: re.match(COURSE_ID_NUMBER_REGEXP, x), "must be a course ID number"
)

validate_term_year = validation_generator(
    lambda x: 2010 < x < 2050, "must be a valid term year"
)

validate_course_title = validation_generator(
    lambda x: re.match(COURSE_TITLE_REGEXP, x), "must be a course title"
)


class Term(models.Model):
    term_id = models.AutoField(primary_key=True)
    year = models.SmallIntegerField(validators=[validate_term_year])
    season = models.CharField(
        max_length=2,
        choices=[("S", "Spring"), ("SU", "Summer"), ("F", "Fall"), ("W", "Winter")],
    )

    class Meta:
        unique_together = [["year", "season"]]


class Subject(models.Model):
    name = models.CharField(max_length=30, unique=True)
    subject_id = models.CharField(
        max_length=8,
        unique=True,
        primary_key=True,
        validators=[],
    )


class Course(models.Model):
    course_id = models.CharField(
        max_length=32, primary_key=True, validators=[validate_course_id]
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    number = models.CharField(max_length=8, validators=[validate_course_id_number])
    title = models.CharField(max_length=128, validators=[validate_course_title])
    description = models.CharField(max_length=1024, null=True)

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
    restriction = models.JSONField(null=True)
    availability = models.JSONField()
    description = models.CharField(max_length=1024, null=True)
    overview = models.CharField(max_length=1024, null=True)
    meeting_days_and_time = models.CharField(max_length=32)
    meeting_room = models.CharField(max_length=32)
    meeting_instructors = models.ManyToManyField(Staff)
    meeting_dates = models.CharField(max_length=32)


class SectionCoverage(models.Model):
    term = models.CharField(max_length=32, primary_key=True)
    completed = models.CharField(default=False)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
