from django.core.validators import RegexValidator
from django.db.models import (
    CASCADE,
    SET_NULL,
    AutoField,
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    EmailField,
    FloatField,
    ForeignKey,
    IntegerField,
    JSONField,
    ManyToManyField,
    Model,
    OneToOneField,
    TimeField,
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

_term_validator = re_validator_factory(TERM_REGEXP, "must be a term (match the term RegExp)")


class Building(Model):
    id = AutoField(primary_key=True)
    name = CharField(max_length=2**6, unique=True)
    address = CharField(max_length=2**6, null=True)

    def __str__(self) -> str:
        return f"Building[{self.id}](name={self.name}, address={self.address})"

    class Meta:
        ordering = ["name"]


class BuildingRoom(Model):
    id = AutoField(primary_key=True)
    building = ForeignKey(Building, on_delete=CASCADE, related_name="rooms", null=True)
    number = CharField(max_length=2**3, null=True)
    alt = CharField(max_length=2**6, unique=True)

    def __str__(self) -> str:
        return f"BuildingRoom[{self.id}](building={self.building}, number={self.number}, alt={self.alt})"

    class Meta:
        ordering = ["building", "number"]
        unique_together = [["building", "number"]]


class Term(Model):
    id = CharField(primary_key=True, validators=[_term_validator], max_length=2**5)
    season = CharField(max_length=2**4)
    year = IntegerField()
    ordinal = IntegerField()
    start_date = DateField(default=None, null=True)
    end_date = DateField(default=None, null=True)

    def __str__(self) -> str:
        return f"Term[{self.id}]"

    class Meta:
        ordering = ["-ordinal"]
        unique_together = [["year", "season"]]


class TermEvent(Model):
    term = ForeignKey(Term, related_name="events", on_delete=CASCADE)
    date = DateField()
    description = CharField(max_length=2**8)

    def __str__(self) -> str:
        return f"TermEvent[None](term={self.term}, date={self.date})"

    class Meta:
        ordering = ["term", "date"]


class AcademicGroup(Model):
    id = AutoField(primary_key=True)
    title = CharField(max_length=2**6, unique=True)

    def __str__(self) -> str:
        return f"AcademicGroup[{self.id}](title={self.title})"

    class Meta:
        ordering = ["title"]


class Subject(Model):
    id = CharField(
        max_length=2**3,
        unique=True,
        primary_key=True,
        validators=[_subject_id_validator],
    )
    title = CharField(max_length=2**6, unique=True, validators=[_subject_title_validator])
    groups = ManyToManyField(AcademicGroup, related_name="subjects")

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
    _updated_at = DateTimeField()

    def __str__(self) -> str:
        return f"Course[{self.id}](subject={self.subject}, title='{self.title}')"

    class Meta:
        unique_together = ["subject", "number"]
        ordering = ["id"]


class CourseUnits(Model):
    base = FloatField(null=True)
    min = FloatField(null=True)
    max = FloatField(null=True)

    class Meta:
        ordering = ["base"]


class CourseDetail(Model):
    course = OneToOneField(Course, on_delete=CASCADE, primary_key=True, related_name="details")
    career = CharField(null=True, max_length=2**5)
    units = ForeignKey(CourseUnits, on_delete=SET_NULL, related_name="+", null=True)
    grading_basis = CharField(null=True, max_length=2**6)
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
        Course,
        on_delete=CASCADE,
        primary_key=True,
        related_name="enrollment_information",
    )
    add_consent = CharField(null=True, max_length=2**9)
    enrollment_requirement = CharField(null=True, max_length=2**9)
    course_attribute = JSONField(null=True, default=list)

    def __str__(self) -> str:
        return f"CourseEnrollmentInformation[{self.course.id}]"

    class Meta:
        ordering = ["course"]


class CourseOffering(Model):
    id = AutoField(primary_key=True)
    subject = ForeignKey(Subject, on_delete=CASCADE, related_name="offerings")
    course = ForeignKey(Course, on_delete=CASCADE, related_name="offerings")
    alternative_title = CharField(max_length=2**8, null=True)
    term = ForeignKey(Term, on_delete=CASCADE, related_name="+")

    def __str__(self):
        return (
            f"CourseOffering[{self.id}](term={self.term}, subject={self.subject.id}, course={self.course.id})"
        )

    class Meta:
        ordering = ["term", "course"]
        unique_together = [["course", "term"]]


class Instructor(Model):
    id = AutoField(primary_key=True)
    name = CharField(max_length=2**6, unique=True)
    email = EmailField(null=True)

    def __str__(self):
        return f"Instructor(name='{self.name}', email='{self.email}')"

    class Meta:
        ordering = ["name", "email"]


class Section(Model):
    id = AutoField(primary_key=True)
    spire_id = CharField(max_length=2**5, validators=[_section_id_validator])
    offering = ForeignKey(CourseOffering, on_delete=CASCADE, related_name="sections")
    description = CharField(max_length=2**12, null=True)
    overview = CharField(max_length=2**15, null=True)
    _updated_at = DateTimeField()

    def __str__(self):
        return f"Section[{self.spire_id}](offering={self.offering})"

    class Meta:
        ordering = ["offering", "spire_id"]


class SectionDetail(Model):
    section = OneToOneField(Section, on_delete=CASCADE, primary_key=True, related_name="details")
    status = CharField(null=True, max_length=2**6)
    class_number = IntegerField()
    session = CharField(null=True, max_length=2**6)
    units = ForeignKey(CourseUnits, on_delete=SET_NULL, related_name="+", null=True)
    class_components = JSONField(null=True)
    career = CharField(null=True, max_length=2**6)
    topic = CharField(null=True, max_length=2**6)
    grading = CharField(null=True, max_length=2**6)
    gened = JSONField(null=True)
    rap_tap_hlc = CharField(null=True, max_length=2**6)

    def __str__(self) -> str:
        return f"SectionDetail[{self.section.id}]"

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

    def __str__(self) -> str:
        return f"SectionAvailability[{self.section.id}]"

    class Meta:
        ordering = ["section"]


class SectionCombinedAvailability(Model):
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

    def __str__(self) -> str:
        return f"SectionCombinedAvailability[{self.individual_availability.section.id}]"

    class Meta:
        ordering = ["individual_availability"]


class SectionRestriction(Model):
    section = OneToOneField(Section, on_delete=CASCADE, primary_key=True, related_name="restrictions")
    drop_consent = CharField(null=True, max_length=2**12)
    enrollment_requirements = CharField(null=True, max_length=2**12)
    add_consent = CharField(null=True, max_length=2**12)

    def __str__(self) -> str:
        return f"SectionRestriction[{self.section.id}]"

    class Meta:
        ordering = ["section"]


class SectionMeetingInformation(Model):
    id = AutoField(primary_key=True)
    section = ForeignKey(Section, on_delete=CASCADE, related_name="meeting_information")
    room = ForeignKey(BuildingRoom, on_delete=SET_NULL, null=True, related_name="+")
    room_raw = CharField(max_length=2**6)
    instructors = ManyToManyField(Instructor, "sections")

    def __str__(self) -> str:
        return f"SectionMeetingInformation[{self.id}]"

    class Meta:
        ordering = ["section"]


class SectionMeetingDates(Model):
    meeting_information = ForeignKey(
        SectionMeetingInformation, on_delete=CASCADE, related_name="meeting_dates"
    )
    start = DateField()
    end = DateField()

    def __str__(self) -> str:
        return f"SectionMeetingDates[{self.meeting_information.id}](start={self.start}, end={self.end})"


class SectionMeetingSchedule(Model):
    meeting_information = OneToOneField(
        SectionMeetingInformation, primary_key=True, on_delete=CASCADE, related_name="schedule"
    )
    days = JSONField()
    start_time = TimeField()
    end_time = TimeField()

    def __str__(self) -> str:
        return f"SectionMeetingSchedule[{self.meeting_information.id}](days={self.days}, start_time={self.start_time}, end_time={self.end_time})"

    class Meta:
        ordering = ["meeting_information", "start_time"]


class SectionCoverage(Model):
    term = OneToOneField(Term, primary_key=True, on_delete=CASCADE)
    completed = BooleanField(default=False)
    start_time = DateTimeField()
    end_time = DateTimeField(null=True)

    class Meta:
        ordering = ["term"]
