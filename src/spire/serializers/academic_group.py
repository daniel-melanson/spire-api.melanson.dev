from rest_framework.serializers import HyperlinkedModelSerializer

from spire.models import AcademicGroup
from spire.serializers.fields import SubjectFieldSerializer


class AcademicGroupSerializer(HyperlinkedModelSerializer):
    subjects = SubjectFieldSerializer(many=True)

    class Meta:
        model = AcademicGroup
        fields = ["url", "id", "title", "subjects"]
