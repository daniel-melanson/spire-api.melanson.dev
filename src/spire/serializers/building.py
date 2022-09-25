from rest_framework.serializers import HyperlinkedModelSerializer

from spire.models import Building, BuildingRoom
from spire.serializers.fields import BaseFieldSerializer, BuildingFieldSerializer


class BRFSNoBuilding(BaseFieldSerializer):
    building = BuildingFieldSerializer()

    class Meta:
        model = BuildingRoom
        fields = ["id", "url", "number", "alt"]


class BuildingSerializer(HyperlinkedModelSerializer):
    rooms = BRFSNoBuilding(many=True)

    class Meta:
        model = Building
        fields = ["url", "id", "name", "address", "rooms"]


class BuildingRoomSerializer(HyperlinkedModelSerializer):
    building = BuildingFieldSerializer()

    class Meta:
        model = BuildingRoom
        fields = ["url", "id", "building", "number", "alt"]
