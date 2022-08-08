from rest_framework.serializers import HyperlinkedModelSerializer

from spire.models import AcademicGroup, Course, CourseOffering, Section, Subject


class BaseFieldSerializer(HyperlinkedModelSerializer):
    def __init__(self, instance=None, data=..., **kwargs):
        super().__init__(instance, data, read_only=True, **kwargs)


class AcademicGroupFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = AcademicGroup
        fields = ["url", "title"]


class SubjectFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = Subject
        fields = ["url", "id", "title"]


class CourseFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = Course
        fields = ["url", "id"]


class CourseOfferingFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = CourseOffering
        fields = ["url", "term"]


class SectionFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = Section
        fields = ["url", "id"]
