from rest_framework.serializers import HyperlinkedModelSerializer

from spire.models import Building
from spire.serializers.fields import BuildingRoomFieldSerializer


class BuildingSerializer(HyperlinkedModelSerializer):
    rooms = BuildingRoomFieldSerializer(many=True)

    class Meta:
        model = Building
        fields = ["url", "id", "title", "address", "rooms"]
