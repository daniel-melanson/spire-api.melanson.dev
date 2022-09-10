from rest_framework.serializers import HyperlinkedModelSerializer

from spire.models import Term, TermEvent
from spire.serializers.fields import TermEventFieldSerializer, TermFieldSerializer


class TermSerializer(HyperlinkedModelSerializer):
    events = TermEventFieldSerializer(many=True)

    class Meta:
        model = Term
        fields = [
            "url",
            "id",
            "season",
            "year",
            "ordinal",
            "start_date",
            "end_date",
            "events",
        ]


class TermEventSerializer(HyperlinkedModelSerializer):
    term = TermFieldSerializer()

    class Meta:
        model = TermEvent
        fields = ["url", "term", "date", "description"]
