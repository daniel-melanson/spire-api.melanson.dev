from rest_framework.serializers import HyperlinkedModelSerializer

from .models import Course, Section, SectionCoverage, Staff, Subject


class CourseSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Course
        fields = ["course_id", "subjects"]


class SectionSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Section
        fields = [
            "section_id",
            #"course",
            "term",
            "details",
            "restrictions",
            "availability",
            "description",
            "overview",
            "meeting_info",
            "instructors",
            "_updated_at",
            "url",
        ]


class StaffSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Staff
        fields = "__all__"


class SubjectSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Subject
        fields = ["title", "subject_id", "url"]


class SectionCoverageSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = SectionCoverage
        fields = "__all__"
