from django.http import Http404
from rest_framework.decorators import api_view, schema, throttle_classes
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema

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


class SubjectCourseList(ListModelMixin, GenericAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get(self, request, subject):
        subject = subject.upper()
        try:
            Subject.objects.get(pk=subject)
        except Subject.DoesNotExist:
            raise Http404

        return Course.objects.filter(subject=subject)


class CourseRetrieve(RetrieveModelMixin, GenericAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get(self, request, subject, number):
        return attempt_course_fetch(subject, number)


class SectionRetrieve(RetrieveModelMixin, GenericAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer

    def get(self, request, subject, number):
        course = attempt_course_fetch()

        return Section.objects.filter(course=course.course_id)


class SubjectsView(ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
