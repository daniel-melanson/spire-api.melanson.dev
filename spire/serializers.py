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


class BaseFieldSerializer(ModelSerializer):
    def __init__(self, instance=None, data=..., **kwargs):
        super().__init__(instance, data, read_only=True, **kwargs)


# Field Serializers


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
        exclude = ["course"]


class CourseEnrollmentInformationFieldSerializer(BaseFieldSerializer):  # lmao
    class Meta:
        model = CourseEnrollmentInformation
        exclude = ["course"]


# Offering
class CourseOfferingFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = CourseOffering
        fields = ["url", "id", "term"]


# Section
class SectionFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = Section
        fields = ["url", "id"]


class SectionDetailFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = SectionDetail
        exclude = ["section"]


class SectionAvailabilityFieldSerializer:
    class Meta:
        model = SectionAvailability
        exclude = ["section"]


class CombinedSectionAvailabilityFieldSerializer:
    class Meta:
        model = SectionCombinedAvailability
        exclude = ["individual_availability"]


# Regular Serializers


class AcademicGroupSerializer(HyperlinkedModelSerializer):
    subjects = SubjectFieldSerializer(many=True)

    class Meta:
        model = AcademicGroup
        fields = ["url", "id", "title", "subjects"]


class SubjectSerializer(HyperlinkedModelSerializer):
    courses = CourseFieldSerializer(many=True)

    class Meta:
        model = Subject
        fields = ["url", "id", "title", "courses"]


class CourseSerializer(HyperlinkedModelSerializer):
    offerings = CourseOfferingFieldSerializer(many=True)
    subject = SubjectFieldSerializer()
    details = CourseDetailsFieldSerializer()
    enrollment_information = CourseEnrollmentInformationFieldSerializer()

    class Meta:
        model = Course
        fields = "__all__"


class CourseDetailSerializer(ModelSerializer):
    course = CourseFieldSerializer()

    class Meta:
        model = CourseDetail
        fields = "__all__"


class CourseEnrollmentInformationSerializer(ModelSerializer):
    course = CourseFieldSerializer()

    class Meta:
        model = CourseEnrollmentInformation
        fields = "__all__"


class CourseOfferingSerializer(ModelSerializer):
    sections = SectionFieldSerializer(many=True)

    class Meta:
        model = CourseEnrollmentInformation
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
    meeting_information = MeetingInformationSerializer(read_only=True, many=True)

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
        fields = ["url", "term", "completed", "start_time", "end_time"]
