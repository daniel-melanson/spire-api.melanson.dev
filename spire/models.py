from django.core.validators import RegexValidator
from django.db.models import (
    CASCADE,
    AutoField,
    BooleanField,
    CharField,
    DateTimeField,
    EmailField,
    ForeignKey,
    IntegerField,
    JSONField,
    ManyToManyField,
    Model,
    OneToOneField,
)

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


class Subject(Model):
    title = CharField(max_length=2**6, unique=True, validators=[_subject_title_validator])
    id = CharField(
        max_length=2**3,
        unique=True,
        primary_key=True,
        validators=[_subject_id_validator],
    )

    def __str__(self):
        return f"Subject[{self.id}](title='{self.title}')"

    class Meta:
        ordering = ["id"]


class Course(Model):
    id = CharField(max_length=2**5, primary_key=True, validators=[_course_id_validator])
    subject = ForeignKey(Subject, on_delete=CASCADE, related_name="courses")
    number = CharField(max_length=2**4, validators=[_course_id_number_validator])
    title = CharField(max_length=2**8, validators=[_course_title_validator])
    description = CharField(max_length=2**12, null=True)
    sections = ManyToManyField("Section", related_name="+")
    _updated_at = DateTimeField()

    def __str__(self) -> str:
        return f"Course[{self.id}](subject={self.subject}, title='{self.title}')"

    class Meta:
        unique_together = ["subject", "number"]
        ordering = ["id"]


class CourseDetail(Model):
    course = OneToOneField(Course, on_delete=CASCADE, primary_key=True, related_name="details")
    career = CharField(null=True, max_length=2**5)
    units = CharField(null=True, max_length=2**4)
    grading_basis = CharField(null=True, max_length=2**5)
    course_components = JSONField(null=True, default=list)
    academic_group = CharField(null=True, max_length=2**7)
    academic_organization = CharField(null=True, max_length=2**7)
    campus = CharField(null=True, max_length=2**6)

    def __str__(self) -> str:
        return f"CourseDetail[{self.course}]"

    class Meta:
        ordering = ["course"]


class CourseEnrollmentInformation(Model):
    course = OneToOneField(
        "Course",
        on_delete=CASCADE,
        primary_key=True,
        related_name="enrollment_information",
    )
    add_consent = CharField(null=True, max_length=2**9)
    enrollment_requirement = CharField(null=True, max_length=2**9)
    course_attribute = JSONField(null=True, default=list)

    class Meta:
        ordering = ["course"]


class Instructor(Model):
    id = AutoField(primary_key=True)
    name = CharField(max_length=2**6, unique=True)
    email = EmailField(null=True)

    def __str__(self):
        return f"Instructor(name='{self.name}', email='{self.email}')"

    class Meta:
        ordering = ["name", "email"]


class Section(Model):
    id = CharField(max_length=2**5, primary_key=True, validators=[_section_id_validator])
    subject = ForeignKey(Subject, on_delete=CASCADE, related_name="sections")
    course_id = CharField(max_length=2**5, validators=[_course_id_validator])
    course_title = CharField(max_length=2**8, null=True)
    term = CharField(max_length=2**4, validators=[_section_term_validator])
    description = CharField(max_length=2**12, null=True)
    overview = CharField(max_length=2**15, null=True)
    _updated_at = DateTimeField()

    def __str__(self):
        return f"Section[{self.id}](term={self.term}, course_id={self.course_id})"

    class Meta:
        ordering = ["term", "course_id", "id"]


class CourseOffering(Model):
    id = AutoField(primary_key=True)
    subject = ForeignKey(Subject, on_delete=CASCADE)
    course = ForeignKey(Course, on_delete=CASCADE)
    alternative_title = CharField(max_length=2**8, null=True)
    term = CharField(max_length=2**5)

    def __str__(self):
        return (
            f"CourseOffering[{self.id}](term={self.term}, subject={self.subject.id}, course={self.course.id})"
        )

    class Meta:
        ordering = ["term", "course"]
        unique_together = [["course", "term"]]


class SectionV2(Model):
    id = CharField(max_length=2**5, primary_key=True, validators=[_section_id_validator])
    offering = ForeignKey(CourseOffering, on_delete=CASCADE, related_name="sections")
    description = CharField(max_length=2**12, null=True)
    overview = CharField(max_length=2**15, null=True)
    _updated_at = DateTimeField()

    def __str__(self):
        return f"Section[{self.id}](term={self.term}, course_id={self.course_id})"

    class Meta:
        ordering = ["id"]


class SectionDetail(Model):
    section = OneToOneField(Section, on_delete=CASCADE, primary_key=True, related_name="details")
    status = CharField(null=True, max_length=2**6)
    class_number = IntegerField()
    session = CharField(null=True, max_length=2**6)
    units = CharField(null=True, max_length=2**6)
    class_components = JSONField(null=True)
    career = CharField(null=True, max_length=2**6)
    topic = CharField(null=True, max_length=2**6)
    grading = CharField(null=True, max_length=2**6)
    gened = JSONField(null=True)
    rap_tap_hlc = CharField(null=True, max_length=2**6)

    class Meta:
        ordering = ["section"]


class SectionAvailability(Model):
    section = OneToOneField(Section, on_delete=CASCADE, primary_key=True, related_name="availability")
    capacity = IntegerField()
    enrollment_total = IntegerField()
    available_seats = IntegerField()
    wait_list_capacity = IntegerField()
    wait_list_total = IntegerField()
    nso_enrollment_capacity = IntegerField(null=True, default=None)


class CombinedSectionAvailability(Model):
    individual_availability = OneToOneField(
        SectionAvailability, on_delete=CASCADE, primary_key=True, related_name="combined_availability"
    )
    sections = JSONField()
    capacity = IntegerField()
    enrollment_total = IntegerField()
    available_seats = IntegerField()
    wait_list_capacity = IntegerField()
    wait_list_total = IntegerField()
    nso_enrollment_capacity = IntegerField(null=True, default=None)


class SectionRestriction(Model):
    section = OneToOneField(Section, on_delete=CASCADE, primary_key=True, related_name="restrictions")
    drop_consent = CharField(null=True, max_length=2**12)
    enrollment_requirements = CharField(null=True, max_length=2**12)
    add_consent = CharField(null=True, max_length=2**12)


class SectionRestriction(Model):
    section = OneToOneField(Section, on_delete=CASCADE, primary_key=True, related_name="restrictions")
    drop_consent = CharField(null=True, max_length=2**12)
    enrollment_requirements = CharField(null=True, max_length=2**12)
    add_consent = CharField(null=True, max_length=2**12)


class MeetingInformation(Model):
    id = AutoField(primary_key=True)
    section = ForeignKey(Section, on_delete=CASCADE, related_name="meeting_information")
    days_and_times = CharField(max_length=2**6)
    room = CharField(max_length=2**6)
    instructors = ManyToManyField(Instructor, "+")
    meeting_dates = CharField(max_length=2**6)

    class Meta:
        ordering = ["section", "days_and_times"]


class SectionCoverage(Model):
    term = CharField(max_length=2**5, primary_key=True, validators=[_section_term_validator])
    completed = BooleanField(default=False)
    start_time = DateTimeField()
    end_time = DateTimeField(null=True)

    class Meta:
        ordering = ["term"]
