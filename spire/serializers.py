from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer

from .models import Course, Section, SectionCoverage, Staff, Subject

class CourseFieldSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = ["url", "course_id"]

class SubjectSerializer(HyperlinkedModelSerializer):
    courses = CourseFieldSerializer(many=True, read_only=True)

    class Meta:
        model = Subject
        fields = ["url", "subject_id", "title", "courses"]

class SectionFieldSerializer(ModelSerializer):
    class Meta:
        model = Section
        fields = ["url", "section_id"]

class CourseSerializer(HyperlinkedModelSerializer):
    sections = SectionFieldSerializer(many=True, read_only=True)
    class Meta:
        model = Course
        fields = [
            "url",
            "course_id",
            "subject",
            "number",
            "title",
            "description",
            "details",
            "enrollment_information",
            "sections",
            "_updated_at",
        ]


class SectionSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Section
        fields = [
            "url",
            "section_id",
            "course",
            "term",
            "details",
            "restrictions",
            "availability",
            "description",
            "overview",
            "meeting_info",
            "instructors",
            "_updated_at",
        ]


class StaffSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Staff
        fields = "__all__"


class SectionCoverageSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = SectionCoverage
        fields = "__all__"
