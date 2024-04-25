from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F, OuterRef, Subquery
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from spire.models import (
    AcademicGroup,
    Building,
    BuildingRoom,
    Course,
    CourseOffering,
    Instructor,
    Section,
    SectionCoverage,
    SectionMeetingInformation,
    Subject,
    Term,
)
from spire.serializers.academic_group import AcademicGroupSerializer
from spire.serializers.building import BuildingRoomSerializer, BuildingSerializer
from spire.serializers.course import (
    CourseInstructorsSerializer,
    CourseOfferingSerializer,
    CourseSerializer,
)
from spire.serializers.instructor import InstructorSerializer
from spire.serializers.section import SectionCoverageSerializer, SectionSerializer
from spire.serializers.subject import SubjectSerializer
from spire.serializers.term import TermSerializer


class BuildingViewSet(ReadOnlyModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name"]


class BuildingRoomViewSet(ReadOnlyModelViewSet):
    queryset = BuildingRoom.objects.all()
    serializer_class = BuildingRoomSerializer


class TermViewSet(ReadOnlyModelViewSet):
    queryset = Term.objects.all()
    serializer_class = TermSerializer


class AcademicGroupViewSet(ReadOnlyModelViewSet):
    queryset = AcademicGroup.objects.all()
    serializer_class = AcademicGroupSerializer
    filter_backends = [SearchFilter]
    search_fields = ["title"]


class SubjectViewSet(ReadOnlyModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    filter_backends = [SearchFilter]
    search_fields = ["id", "title"]


class CourseViewSet(ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [SearchFilter]
    search_fields = ["id", "title"]

    @action(
        detail=True,
        serializer_class=SectionSerializer,
    )
    def sections(self, request, pk=None):
        course = self.get_object()
        section_list = Section.objects.filter(offering__course__id=course.id)
        page = self.paginate_queryset(section_list)
        assert page
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    # TODO Paginate?
    @action(
        detail=True,
        serializer_class=CourseInstructorsSerializer,
    )
    def instructors(self, request, pk=None):
        course = self.get_object()

        queryset = (
            SectionMeetingInformation.objects.filter(
                section__offering__course_id=course.id
            )
            .annotate(
                instructor=Subquery(
                    Instructor.objects.filter(id=OuterRef("instructors__id")).values(
                        "id"
                    )[:1]
                ),
            )
            .values("section__offering_id")
            .order_by("section__offering")
            .annotate(
                offering=F("section__offering_id"),
                instructors=ArrayAgg("instructor", distinct=True),
            )
            .values("offering", "instructors")
        )

        page = self.paginate_queryset(queryset)
        assert page
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class CourseOfferingViewSet(ReadOnlyModelViewSet):
    queryset = CourseOffering.objects.all()
    serializer_class = CourseOfferingSerializer


class InstructorViewSet(ReadOnlyModelViewSet):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name"]

    @action(
        detail=True,
        serializer_class=SectionSerializer,
    )
    def sections(self, request, pk=None):
        instructor = self.get_object()
        section_list = Section.objects.filter(
            meeting_information__instructors__id=instructor.id
        )

        page = self.paginate_queryset(section_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(section_list, many=True)
        return Response(serializer.data)


class SectionViewSet(ReadOnlyModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer


class CoverageViewSet(ReadOnlyModelViewSet):
    queryset = SectionCoverage.objects.all()
    serializer_class = SectionCoverageSerializer


class CurrentTermsView(GenericAPIView):
    queryset = Term.objects.all()
    serializer_class = TermSerializer

    def get(self, request):
        queryset = self.get_queryset().filter(
            start_date__lte=timezone.now(), end_date__gte=timezone.now()
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
