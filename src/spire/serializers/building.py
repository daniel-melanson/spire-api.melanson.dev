from rest_framework.serializers import HyperlinkedModelSerializer

from spire.models import AcademicGroup
from spire.serializers.fields import BuildingRoomFieldSerializer


class BuildingSerializer(HyperlinkedModelSerializer):
    rooms = BuildingRoomFieldSerializer(many=True)

    class Meta:
        model = AcademicGroup
        fields = ["url", "id", "title", "address", "rooms"]
