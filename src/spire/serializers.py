from attr import fields
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer

from spire.models import (
    AcademicGroup,
    Course,
    CourseDetail,
    CourseEnrollmentInformation,
    CourseOffering,
    Instructor,
    MeetingInformation,
    Section,
    SectionAvailability,
    SectionCombinedAvailability,
    SectionCoverage,
    SectionDetail,
    SectionRestriction,
    Subject,
)


class BaseFieldSerializer(HyperlinkedModelSerializer):
    def __init__(self, instance=None, data=..., **kwargs):
        super().__init__(instance, data, read_only=True, **kwargs)


# Field Serializers


class AcademicGroupFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = AcademicGroup
        fields = ["url", "title"]


class SubjectFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = Subject
        fields = ["url", "id", "title"]


# Course
class CourseFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = Course
        fields = ["url", "id"]


class CourseDetailsFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = CourseDetail
        fields = "__all__"


class CourseEnrollmentInformationFieldSerializer(BaseFieldSerializer):  # lmao
    class Meta:
        model = CourseEnrollmentInformation
        fields = "__all__"


# Offering
class CourseOfferingFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = CourseOffering
        fields = ["url", "term"]


# Section
class SectionFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = Section
        fields = ["url", "id"]


class SectionDetailFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = SectionDetail
        fields = "__all__"


class CombinedSectionAvailabilityFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = SectionCombinedAvailability
        exclude = ["individual_availability"]


class SectionAvailabilityFieldSerializer(BaseFieldSerializer):
    combined_availability = CombinedSectionAvailabilityFieldSerializer()

    class Meta:
        model = SectionAvailability
        fields = "__all__"


class InstructorFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = Instructor
        fields = "__all__"


class MeetingInformationFieldSerializer(BaseFieldSerializer):
    instructors = InstructorFieldSerializer(many=True)

    class Meta:
        model = MeetingInformation
        exclude = ["section"]


# Regular Serializers


class AcademicGroupSerializer(HyperlinkedModelSerializer):
    subjects = SubjectFieldSerializer(many=True)

    class Meta:
        model = AcademicGroup
        fields = "__all__"


class SubjectSerializer(HyperlinkedModelSerializer):
    courses = CourseFieldSerializer(many=True)
    groups = AcademicGroupFieldSerializer(many=True)

    class Meta:
        model = Subject
        fields = ["url", "title", "id", "groups", "courses"]


class CourseSerializer(HyperlinkedModelSerializer):
    offerings = CourseOfferingFieldSerializer(many=True)
    subject = SubjectFieldSerializer()
    details = CourseDetailsFieldSerializer()
    enrollment_information = CourseEnrollmentInformationFieldSerializer()

    class Meta:
        model = Course
        fields = [
            "url",
            "id",
            "subject",
            "number",
            "title",
            "description",
            "_updated_at",
            "offerings",
            "details",
            "enrollment_information",
        ]


class CourseDetailSerializer(HyperlinkedModelSerializer):
    course = CourseFieldSerializer()

    class Meta:
        model = CourseDetail
        fields = "__all__"


class CourseEnrollmentInformationSerializer(HyperlinkedModelSerializer):
    course = CourseFieldSerializer()

    class Meta:
        model = CourseEnrollmentInformation
        fields = "__all__"


class CourseOfferingSerializer(HyperlinkedModelSerializer):
    sections = SectionFieldSerializer(many=True)
    subject = SubjectFieldSerializer()
    course = CourseFieldSerializer()

    class Meta:
        model = CourseOffering
        fields = "__all__"


class InstructorSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Instructor
        fields = "__all__"


class MeetingInformationSerializer(HyperlinkedModelSerializer):
    instructors = InstructorSerializer(many=True)
    section = SectionFieldSerializer()

    class Meta:
        model = MeetingInformation
        fields = "__all__"


class SectionSerializer(HyperlinkedModelSerializer):
    details = SectionDetailFieldSerializer()
    meeting_information = MeetingInformationFieldSerializer(many=True)

    class Meta:
        model = Section
        fields = "__all__"


class SectionDetailSerializer(HyperlinkedModelSerializer):
    section = SectionFieldSerializer()

    class Meta:
        model = SectionDetail
        fields = "__all__"


class SectionAvailabilitySerializer(HyperlinkedModelSerializer):
    section = SectionFieldSerializer()
    combined_availability = CombinedSectionAvailabilityFieldSerializer()

    class Meta:
        model = SectionAvailability
        fields = "__all__"


class CombinedSectionAvailabilitySerializer(HyperlinkedModelSerializer):
    individual_availability = SectionAvailabilityFieldSerializer()

    class Meta:
        model = SectionCombinedAvailability
        fields = "__all__"


class SectionRestrictionSerializer(HyperlinkedModelSerializer):
    section = SectionFieldSerializer()

    class Meta:
        model = SectionRestriction
        fields = "__all__"


class SectionCoverageSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = SectionCoverage
        fields = "__all__"
