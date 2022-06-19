from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer, RelatedField

from spire.models import (
    Course,
    CourseDetail,
    CourseEnrollmentInformation,
    Section,
    SectionCoverage,
    SectionDetail,
    Staff,
    Subject,
)


class CourseFieldSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = ["url", "id"]


class SubjectSerializer(HyperlinkedModelSerializer):
    courses = CourseFieldSerializer(many=True, read_only=True)

    class Meta:
        model = Subject
        fields = ["url", "id", "title", "courses"]


class SectionFieldSerializer(ModelSerializer):
    class Meta:
        model = Section
        fields = ["url", "id"]


class SubjectFieldSerializer(RelatedField):
    def to_representation(self, value):
        return str(value)


class DetailsFieldSerializer(ModelSerializer):
    class Meta:
        model = CourseDetail
        exclude = ["course"]


class EnrollInfoFieldSerializer(ModelSerializer):
    class Meta:
        model = CourseEnrollmentInformation
        exclude = ["course"]


class CourseSerializer(HyperlinkedModelSerializer):
    sections = SectionFieldSerializer(many=True, read_only=True)
    subject = SubjectFieldSerializer(read_only=True)
    details = DetailsFieldSerializer(read_only=True)
    enrollment_information = EnrollInfoFieldSerializer(read_only=True)

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


class SectionDetailFieldSerializer(ModelSerializer):
    class Meta:
        model = SectionDetail
        exclude = ["section"]


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
            "instructors",
            "_updated_at",
        ]


class SectionDetailSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = SectionDetail
        fields = "__all__"


class StaffSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Staff
        fields = "__all__"


class SectionCoverageSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = SectionCoverage
        fields = "__all__"
