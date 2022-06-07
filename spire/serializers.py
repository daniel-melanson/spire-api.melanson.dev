from rest_framework.serializers import HyperlinkedModelSerializer

from .models import Course, Section, SectionCoverage, Staff, Subject


class CourseSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Course
        fields = ["course_id", "subject", "number", "title", "description"]


class SectionSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Section
        fields = [
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
        ]


class StaffSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Staff
        fields = ["name", "email"]


class SubjectSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Subject
        fields = ["name", "subject_id"]


class SectionCoverageSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = SectionCoverage
        fields = ["term", "completed", "start_time", "end_time"]
