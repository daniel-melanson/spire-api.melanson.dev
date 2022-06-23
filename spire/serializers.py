from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer

from spire.models import (
    Course,
    CourseDetail,
    CourseEnrollmentInformation,
    Instructor,
    MeetingInformation,
    Section,
    SectionCoverage,
    SectionDetail,
    Subject,
)

# Field Serializers


class SubjectFieldSerializer(ModelSerializer):
    class Meta:
        model = Subject
        fields = ["url", "id", "title"]


class CourseFieldSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = ["url", "id"]


class CourseDetailsFieldSerializer(ModelSerializer):
    class Meta:
        model = CourseDetail
        exclude = ["course"]


class CourseEnrollmentInformationFieldSerializer(ModelSerializer):  # lmao
    class Meta:
        model = CourseEnrollmentInformation
        exclude = ["course"]


class SectionFieldSerializer(ModelSerializer):
    class Meta:
        model = Section
        fields = ["url", "id"]


class SectionDetailFieldSerializer(ModelSerializer):
    class Meta:
        model = SectionDetail
        exclude = ["section"]


# Regular Serializers
class SubjectSerializer(HyperlinkedModelSerializer):
    courses = CourseFieldSerializer(many=True, read_only=True)

    class Meta:
        model = Subject
        fields = ["url", "id", "title", "courses"]


class CourseSerializer(HyperlinkedModelSerializer):
    sections = SectionFieldSerializer(many=True, read_only=True)
    subject = SubjectFieldSerializer(read_only=True)
    details = CourseDetailsFieldSerializer(read_only=True)
    enrollment_information = CourseEnrollmentInformationFieldSerializer(read_only=True)

    class Meta:
        model = Course
        fields = [
            "url",
            "id",
            "subject",
            "number",
            "title",
            "description",
            "details",
            "enrollment_information",
            "sections",
            "_updated_at",
        ]


class CourseDetailSerializer(ModelSerializer):
    class Meta:
        model = CourseDetail
        fields = "__all__"


class CourseEnrollmentInformationSerializer(ModelSerializer):
    class Meta:
        model = CourseEnrollmentInformation
        fields = "__all__"


class SectionSerializer(HyperlinkedModelSerializer):
    details = SectionDetailFieldSerializer(read_only=True)

    class Meta:
        model = Section
        fields = [
            "id",
            "course_id",
            "term",
            "details",
            "meeting_information",
            "restrictions",
            "availability",
            "description",
            "overview",
            "_updated_at",
        ]


class SectionDetailSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = SectionDetail
        fields = "__all__"


class InstructorSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Instructor
        fields = "__all__"


class MeetingInformationSerializer(HyperlinkedModelSerializer):
    instructors = InstructorSerializer()

    class Meta:
        model = MeetingInformation
        fields = "__all__"


class SectionCoverageSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = SectionCoverage
        fields = ["url", "term", "completed", "start_time", "end_time"]
