from rest_framework.serializers import HyperlinkedModelSerializer

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


class SectionDetailSerializer(HyperlinkedModelSerializer):
    section = SectionFieldSerializer()

    class Meta:
        model = SectionDetail
        fields = "__all__"


class SectionMeetingScheduleSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = SectionMeetingSchedule
        exclude = ["url"]


class SectionMeetingInformationSerializer(HyperlinkedModelSerializer):
    section = SectionFieldSerializer()
    schedule = SectionMeetingScheduleSerializer()
    instructors = InstructorSerializer(many=True)
    room = BuildingRoomFieldSerializer()

    class Meta:
        model = SectionMeetingInformation
        fields = "__all__"


class SectionAvailabilitySerializer(HyperlinkedModelSerializer):
    section = SectionFieldSerializer()

    class Meta:
        model = SectionAvailability
        fields = "__all__"


class SectionCombinedAvailabilitySerializer(HyperlinkedModelSerializer):
    section = SectionFieldSerializer()

    class Meta:
        model = SectionCombinedAvailability
        fields = "__all__"


class SectionRestrictionSerializer(HyperlinkedModelSerializer):
    section = SectionFieldSerializer()

    class Meta:
        model = SectionRestriction
        fields = "__all__"


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
            "id",
            "offering",
            "description",
            "overview",
            "_updated_at",
            "details",
            "offering",
            "details",
            "availability",
            "restrictions",
            "meeting_information",
        ]
