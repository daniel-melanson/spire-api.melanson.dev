from rest_framework.serializers import HyperlinkedModelSerializer

from spire.models import Course, CourseDetail, CourseEnrollmentInformation, CourseOffering
from spire.serializers.fields import (
    CourseFieldSerializer,
    CourseOfferingFieldSerializer,
    SectionFieldSerializer,
    SubjectFieldSerializer,
)


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
    course = CourseFieldSerializer()
    sections = SectionFieldSerializer(many=True)

    class Meta:
        model = CourseOffering
        exclude = ["_term_ordinal"]


class CourseSerializer(HyperlinkedModelSerializer):
    subject = SubjectFieldSerializer()
    details = CourseDetailSerializer()
    enrollment_information = CourseEnrollmentInformationSerializer()
    offerings = CourseOfferingFieldSerializer(many=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "subject",
            "number",
            "title",
            "description",
            "details",
            "enrollment_information",
            "offerings",
            "_updated_at",
        ]