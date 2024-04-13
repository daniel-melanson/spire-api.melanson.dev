from rest_framework.serializers import (
    HyperlinkedModelSerializer,
    ModelSerializer,
    Serializer,
)

from spire.models import (
    Course,
    CourseDetail,
    CourseEnrollmentInformation,
    CourseOffering,
    Instructor,
)
from spire.serializers.fields import (
    CourseFieldSerializer,
    CourseOfferingFieldSerializer,
    CourseUnitsFieldSerializer,
    SectionFieldSerializer,
    SubjectFieldSerializer,
    TermFieldSerializer,
)
from spire.serializers.instructor import InstructorSerializer


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


class DummyObject:
    def __init__(self, pk):
        self.pk = pk


class CourseInstructorsSerializer(Serializer):
    offering = CourseOfferingFieldSerializer()
    instructors = InstructorSerializer(many=True)

    def to_representation(self, instance):
        return super().to_representation(
            {
                "offering": CourseOffering.objects.get(pk=instance["offering"]),
                "instructors": Instructor.objects.filter(
                    pk__in=instance["instructors"]
                ),
            }
        )
