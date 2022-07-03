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
    title = models.CharField(max_length=2**6, unique=True, validators=[_subject_title_validator])
    id = models.CharField(
        max_length=2**3,
        unique=True,
        primary_key=True,
        validators=[_subject_id_validator],
    )

    def __str__(self):
        return f"Subject[{self.id}](title=`{self.title}`)"

    class Meta:
        ordering = ["id"]


class Course(models.Model):
    id = models.CharField(max_length=2**5, primary_key=True, validators=[_course_id_validator])
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="courses")
    number = models.CharField(max_length=2**4, validators=[_course_id_number_validator])
    title = models.CharField(max_length=2**8, validators=[_course_title_validator])
    description = models.CharField(max_length=2**12, null=True)
    sections = models.ManyToManyField("Section", related_name="+")
    _updated_at = models.DateTimeField()

    def __str__(self) -> str:
        return f"Course[{self.id}](subject={self.subject}, title=`{self.title}`)"

    class Meta:
        unique_together = ["subject", "number"]
        ordering = ["id"]


class CourseDetail(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, primary_key=True, related_name="details")
    career = models.CharField(null=True, max_length=2**5)
    units = models.CharField(null=True, max_length=2**4)
    grading_basis = models.CharField(null=True, max_length=2**5)
    course_components = models.JSONField(null=True, default=list)
    academic_group = models.CharField(null=True, max_length=2**7)
    academic_organization = models.CharField(null=True, max_length=2**7)
    campus = models.CharField(null=True, max_length=2**6)

    def __str__(self) -> str:
        return f"CourseDetail[{self.course}]"

    class Meta:
        ordering = ["course"]


class CourseEnrollmentInformation(models.Model):
    course = models.OneToOneField(
        "Course",
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="enrollment_information",
    )
    add_consent = models.CharField(null=True, max_length=2**9)
    enrollment_requirement = models.CharField(null=True, max_length=2**9)
    course_attribute = models.JSONField(null=True, default=list)

    class Meta:
        ordering = ["course"]


class Instructor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=2**6, unique=True)
    email = models.EmailField(null=True)

    def __str__(self):
        return f"Instructor(name={self.name}, email={self.email})"

    class Meta:
        ordering = ["name", "email"]


class Section(models.Model):
    id = models.CharField(max_length=2**5, primary_key=True, validators=[_section_id_validator])
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="sections")
    course_id = models.CharField(max_length=2**5, validators=[_course_id_validator])
    course_title = models.CharField(max_length=2**8, null=True)
    term = models.CharField(max_length=2**4, validators=[_section_term_validator])
    description = models.CharField(max_length=2**12, null=True)
    overview = models.CharField(max_length=2**15, null=True)
    _updated_at = models.DateTimeField()

    def __str__(self):
        return f"Section[{self.id}](term={self.term}, course_id={self.course_id})"

    class Meta:
        ordering = ["term", "course_id", "id"]


class SectionAvailability(models.Model):
    section = models.OneToOneField(
        Section, on_delete=models.CASCADE, primary_key=True, related_name="availability"
    )
    capacity = models.IntegerField()
    enrollment_total = models.IntegerField()
    available_seats = models.IntegerField()
    wait_list_capacity = models.IntegerField()
    wait_list_total = models.IntegerField()


class CombinedSectionAvailability(models.Model):
    individual_availability = models.OneToOneField(
        SectionAvailability, on_delete=models.CASCADE, primary_key=True, related_name="combined_availability"
    )
    sections = models.JSONField()
    capacity = models.IntegerField()
    enrollment_total = models.IntegerField()
    available_seats = models.IntegerField()
    wait_list_capacity = models.IntegerField()
    wait_list_total = models.IntegerField()


class SectionRestriction(models.Model):
    section = models.OneToOneField(
        Section, on_delete=models.CASCADE, primary_key=True, related_name="restrictions"
    )
    drop_consent = models.CharField(null=True, max_length=2**12)
    enrollment_requirements = models.CharField(null=True, max_length=2**12)
    add_consent = models.CharField(null=True, max_length=2**12)


class MeetingInformation(models.Model):
    id = models.AutoField(primary_key=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="meeting_information")
    days_and_times = models.CharField(max_length=2**6)
    room = models.CharField(max_length=2**6)
    instructors = models.ManyToManyField(Instructor, "+")
    meeting_dates = models.CharField(max_length=2**6)

    class Meta:
        ordering = ["section", "days_and_times"]


class SectionDetail(models.Model):
    section = models.OneToOneField(
        Section, on_delete=models.CASCADE, primary_key=True, related_name="details"
    )
    status = models.CharField(null=True, max_length=2**6)
    class_number = models.IntegerField(unique=True)
    session = models.CharField(null=True, max_length=2**6)
    units = models.CharField(null=True, max_length=2**6)
    class_components = models.JSONField(null=True)
    career = models.CharField(null=True, max_length=2**6)
    topic = models.CharField(null=True, max_length=2**6)
    grading = models.CharField(null=True, max_length=2**6)
    gened = models.JSONField(null=True)
    rap_tap_hlc = models.CharField(null=True, max_length=2**6)

    class Meta:
        ordering = ["section"]


class SectionCoverage(models.Model):
    term = models.CharField(max_length=2**5, primary_key=True, validators=[_section_term_validator])
    completed = models.BooleanField(default=False)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)

    class Meta:
        ordering = ["term"]
