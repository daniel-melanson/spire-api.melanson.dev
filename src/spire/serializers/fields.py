from rest_framework.serializers import HyperlinkedModelSerializer

from spire.models import (
    AcademicGroup,
    Building,
    BuildingRoom,
    Course,
    CourseOffering,
    CourseUnits,
    Section,
    Subject,
    SubjectSectionCoverage,
    Term,
    TermEvent,
)


class BaseFieldSerializer(HyperlinkedModelSerializer):
    def __init__(self, instance=None, data=..., **kwargs):
        super().__init__(instance, data, read_only=True, **kwargs)


class CourseUnitsFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = CourseUnits
        fields = ["base", "min", "max"]


class BuildingFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = Building
        fields = ["id", "name", "address"]


class BuildingRoomFieldSerializer(BaseFieldSerializer):
    building = BuildingFieldSerializer()

    class Meta:
        model = BuildingRoom
        fields = ["id", "url", "number", "alt", "building"]


class TermFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = Term
        fields = ["id", "url", "season", "year", "ordinal"]


class TermEventFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = TermEvent
        fields = ["date", "description"]


class AcademicGroupFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = AcademicGroup
        fields = ["id", "url", "title"]


class SubjectFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = Subject
        fields = ["id", "url", "title"]


class CourseFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = Course
        fields = ["id", "url", "title"]


class CourseOfferingFieldSerializer(BaseFieldSerializer):
    term = TermFieldSerializer()

    class Meta:
        model = CourseOffering
        fields = ["id", "url", "term"]


class SectionFieldSerializer(BaseFieldSerializer):
    class Meta:
        model = Section
        fields = ["id", "url", "spire_id"]


class SubjectSectionCoverageField(BaseFieldSerializer):
    subject = SubjectFieldSerializer()

    class Meta:
        model = SubjectSectionCoverage
        fields = ["subject", "completed", "updated_at", "start_time", "end_time"]
