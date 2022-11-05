from django.conf import settings
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import SearchFilter

from spire.models import (
    AcademicGroup,
    Building,
    BuildingRoom,
    Course,
    CourseOffering,
    Instructor,
    Section,
    SectionCoverage,
    Subject,
    Term,
    TermEvent,
)
from spire.serializers.academic_group import AcademicGroupSerializer
from spire.serializers.building import BuildingRoomSerializer, BuildingSerializer
from spire.serializers.course import (
    CourseOfferingSerializer,
    CourseSerializer,
)
from spire.serializers.instructor import InstructorSerializer
from spire.serializers.section import (
    SectionCoverageSerializer,
    SectionSerializer,
)
from spire.serializers.subject import SubjectSerializer
from spire.serializers.term import TermEventSerializer, TermSerializer


class BaseViewSet(ReadOnlyModelViewSet):
    @method_decorator(cache_page(settings.VIEW_CACHE_TTL))
    def dispatch(self, *args, **kwargs):
        return super(BaseViewSet, self).dispatch(*args, **kwargs)


class BuildingViewSet(BaseViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name"]


class BuildingRoomViewSet(BaseViewSet):
    queryset = BuildingRoom.objects.all()
    serializer_class = BuildingRoomSerializer


class TermViewSet(BaseViewSet):
    queryset = Term.objects.all()
    serializer_class = TermSerializer


class TermEventViewSet(BaseViewSet):
    queryset = TermEvent.objects.all()
    serializer_class = TermEventSerializer


class AcademicGroupViewSet(BaseViewSet):
    queryset = AcademicGroup.objects.all()
    serializer_class = AcademicGroupSerializer
    filter_backends = [SearchFilter]
    search_fields = ["title"]


class SubjectViewSet(BaseViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    filter_backends = [SearchFilter]
    search_fields = ["id", "name"]


class CourseViewSet(BaseViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [SearchFilter]
    search_fields = ["id", "name"]


class CourseOfferingViewSet(BaseViewSet):
    queryset = CourseOffering.objects.all()
    serializer_class = CourseOfferingSerializer


class InstructorViewSet(BaseViewSet):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name"]

    @action(detail=True)
    def sections(self, request, pk=None):
        instructor = self.get_object()
        section_list = Section.objects.filter(meeting_information__instructors__id=instructor.id)
        serializer = SectionSerializer(section_list, many=True, context={"request": request})
        return Response(serializer.data)


class SectionViewSet(BaseViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer


class CoverageViewSet(BaseViewSet):
    queryset = SectionCoverage.objects.all()
    serializer_class = SectionCoverageSerializer
