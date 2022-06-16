from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet

from spire.models import Course, Section, SectionCoverage, Staff, Subject
from spire.serializers import (
    CourseSerializer,
    SectionCoverageSerializer,
    SectionSerializer,
    StaffSerializer,
    SubjectSerializer,
)


def attempt_course_fetch(sub: str, num: str) -> Course:
    try:
        return Course.objects.get(pk=f"{sub.upper()} {num.upper()}")
    except Course.DoesNotExist:
        raise Http404


class CourseViewSet(ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["subject"]


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


class CoverageViewSet(ReadOnlyModelViewSet):
    queryset = SectionCoverage.objects.all()
    serializer_class = SectionCoverageSerializer
    pagination_class = None
