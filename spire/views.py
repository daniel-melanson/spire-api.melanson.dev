from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet

from spire.models import (
    Course,
    CourseDetail,
    CourseEnrollmentInformation,
    Section,
    SectionCoverage,
    SectionDetail,
    Staff,
    Subject,
)
from spire.serializers import (
    CourseDetailSerializer,
    CourseEnrollmentInformationSerializer,
    CourseSerializer,
    SectionCoverageSerializer,
    SectionSerializer,
    SectionDetailSerializer,
    StaffSerializer,
    SubjectSerializer,
)


class CourseViewSet(ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["subject"]


class CourseDetailsViewSet(ReadOnlyModelViewSet):
    queryset = CourseDetail.objects.all()
    serializer_class = CourseDetailSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "career",
        "units",
        "grading_basis",
        "academic_group",
        "academic_organization",
        "campus",
    ]


class CourseEnrollmentInformationViewSet(ReadOnlyModelViewSet):
    queryset = CourseEnrollmentInformation.objects.all()
    serializer_class = CourseEnrollmentInformationSerializer


class SubjectsViewSet(ReadOnlyModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class StaffViewSet(ReadOnlyModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer


class SectionViewSet(ReadOnlyModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["course_id"]


class SectionDetailsViewSet(ReadOnlyModelViewSet):
    queryset = SectionDetail.objects.all()
    serializer_class = SectionDetailSerializer


class CoverageViewSet(ReadOnlyModelViewSet):
    queryset = SectionCoverage.objects.all()
    serializer_class = SectionCoverageSerializer
    pagination_class = None
