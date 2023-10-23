from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer

from spire.models import (
    CourseOffering,
    Section,
    SectionAvailability,
    SectionCombinedAvailability,
    SectionCoverage,
    SectionDetail,
    SectionMeetingInformation,
    SectionMeetingSchedule,
    SectionRestriction,
)
from spire.serializers.fields import (
    BaseFieldSerializer,
    BuildingRoomFieldSerializer,
    CourseFieldSerializer,
    CourseUnitsFieldSerializer,
    SectionFieldSerializer,
    TermFieldSerializer,
)
from spire.serializers.instructor import InstructorSerializer


class SectionCourseOfferingFieldSerializer(BaseFieldSerializer):
    course = CourseFieldSerializer()
    term = TermFieldSerializer()

    class Meta:
        model = CourseOffering
        fields = ["url", "term", "course"]


class SectionDetailSerializer(ModelSerializer):
    units = CourseUnitsFieldSerializer()

    class Meta:
        model = SectionDetail
        exclude = ["section"]


class SectionMeetingScheduleSerializer(ModelSerializer):
    class Meta:
        model = SectionMeetingSchedule
        fields = ["days", "start_time", "end_time"]


class SectionMeetingInformationSerializer(ModelSerializer):
    schedule = SectionMeetingScheduleSerializer()
    instructors = InstructorSerializer(many=True)
    room = BuildingRoomFieldSerializer()

    class Meta:
        model = SectionMeetingInformation
        exclude = ["section", "id"]


class SectionAvailabilitySerializer(ModelSerializer):
    class Meta:
        model = SectionAvailability
        exclude = ["section"]


class SectionCombinedAvailabilitySerializer(HyperlinkedModelSerializer):
    section = SectionFieldSerializer()

    class Meta:
        model = SectionCombinedAvailability
        fields = "__all__"


class SectionRestrictionSerializer(ModelSerializer):
    class Meta:
        model = SectionRestriction
        exclude = ["section"]


class SectionCoverageSerializer(HyperlinkedModelSerializer):
    term = TermFieldSerializer()

    class Meta:
        model = SectionCoverage
        fields = ["completed", "term", "start_time", "end_time"]


class SectionSerializer(HyperlinkedModelSerializer):
    offering = SectionCourseOfferingFieldSerializer()
    details = SectionDetailSerializer()
    availability = SectionAvailabilitySerializer()
    restrictions = SectionRestrictionSerializer()
    meeting_information = SectionMeetingInformationSerializer(many=True)

    class Meta:
        model = Section
        fields = [
            "url",
            "spire_id",
            "offering",
            "description",
            "overview",
            "details",
            "offering",
            "details",
            "availability",
            "restrictions",
            "meeting_information",
            "_updated_at",
        ]
