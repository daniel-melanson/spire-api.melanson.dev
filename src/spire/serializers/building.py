from rest_framework.serializers import HyperlinkedModelSerializer

from spire.models import Building, BuildingRoom
from spire.serializers.fields import BuildingFieldSerializer, BuildingRoomFieldSerializer


class BuildingSerializer(HyperlinkedModelSerializer):
    rooms = BuildingRoomFieldSerializer(many=True)

    class Meta:
        model = Building
        fields = ["url", "id", "name", "address", "rooms"]


class BuildingRoomSerializer(HyperlinkedModelSerializer):
    building = BuildingFieldSerializer()

    class Meta:
        model = BuildingRoom
        fields = ["url", "id", "building", "number", "alt"]
