from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer

from spire.models import Course, CourseDetail, CourseEnrollmentInformation, CourseOffering
from spire.serializers.fields import (
    CourseFieldSerializer,
    CourseOfferingFieldSerializer,
    CourseUnitsFieldSerializer,
    SectionFieldSerializer,
    SubjectFieldSerializer,
    TermFieldSerializer,
)


class CourseDetailSerializer(ModelSerializer):
    units = CourseUnitsFieldSerializer()
    class Meta:
        model = CourseDetail
        exclude = ["course"]


class CourseEnrollmentInformationSerializer(ModelSerializer):

    class Meta:
        model = CourseEnrollmentInformation
        exclude = ["course"]

class CourseOfferingSerializer(HyperlinkedModelSerializer):
    course = CourseFieldSerializer()
    sections = SectionFieldSerializer(many=True)
    subject = SubjectFieldSerializer()
    term = TermFieldSerializer()

    class Meta:
        model = CourseOffering
        fields = [
            "id",
            "url",
            "subject",
            "course",
            "alternative_title",
            "term",
            "sections",
        ]


class CourseSerializer(HyperlinkedModelSerializer):
    subject = SubjectFieldSerializer()
    details = CourseDetailSerializer()
    enrollment_information = CourseEnrollmentInformationSerializer()
    offerings = CourseOfferingFieldSerializer(many=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "url",
            "subject",
            "number",
            "title",
            "description",
            "details",
            "enrollment_information",
            "offerings",
            "_updated_at",
        ]
