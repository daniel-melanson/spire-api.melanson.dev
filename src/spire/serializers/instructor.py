from rest_framework.serializers import HyperlinkedModelSerializer

from spire.models import Instructor


class InstructorSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Instructor
        fields = "__all__"
