from rest_framework.serializers import HyperlinkedModelSerializer

from .models import Course, Section, SectionCoverage, Staff, Subject


class CourseSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class SectionSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Section
        fields = "__all__"


class StaffSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Staff
        fields = "__all__"


class SubjectSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class SectionCoverageSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = SectionCoverage
        fields = "__all__"
