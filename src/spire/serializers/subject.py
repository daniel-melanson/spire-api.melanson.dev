from rest_framework.serializers import HyperlinkedModelSerializer

from spire.models import Subject
from spire.serializers.fields import AcademicGroupFieldSerializer, CourseFieldSerializer


class SubjectSerializer(HyperlinkedModelSerializer):
    groups = AcademicGroupFieldSerializer(many=True)
    courses = CourseFieldSerializer(many=True)

    class Meta:
        model = Subject
        fields = [
            "id",
            "title",
            "groups",
            "courses",
        ]
