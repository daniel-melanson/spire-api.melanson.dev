from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet as ROMVS

from spire.models import (
    AcademicGroup,
    Course,
    CourseDetail,
    CourseEnrollmentInformation,
    CourseOffering,
    Instructor,
    MeetingInformation,
    Section,
    SectionAvailability,
    SectionCombinedAvailability,
    SectionCoverage,
    SectionDetail,
    SectionRestriction,
    Subject,
)
from spire.serializers import (
    AcademicGroupSerializer,
    CombinedSectionAvailabilitySerializer,
    CourseDetailSerializer,
    CourseEnrollmentInformationSerializer,
    CourseOfferingSerializer,
    CourseSerializer,
    InstructorSerializer,
    MeetingInformationSerializer,
    SectionAvailabilitySerializer,
    SectionCoverageSerializer,
    SectionDetailSerializer,
    SectionRestrictionSerializer,
    SectionSerializer,
    SubjectSerializer,
)


class AcademicGroupViewSet(ROMVS):
    queryset = AcademicGroup.objects.all()
    serializer_class = AcademicGroupSerializer


class SubjectViewSet(ROMVS):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class CourseViewSet(ROMVS):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CourseDetailsViewSet(ROMVS):
    queryset = CourseDetail.objects.all()
    serializer_class = CourseDetailSerializer


class CourseEnrollmentInformationViewSet(ROMVS):
    queryset = CourseEnrollmentInformation.objects.all()
    serializer_class = CourseEnrollmentInformationSerializer


class CourseOfferingViewSet(ROMVS):
    queryset = CourseOffering.objects.all()
    serializer_class = CourseOfferingSerializer


class InstructorViewSet(ROMVS):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer


class SectionViewSet(ROMVS):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer


class SectionDetailsViewSet(ROMVS):
    queryset = SectionDetail.objects.all()
    serializer_class = SectionDetailSerializer


class SectionAvailabilityViewSet(ROMVS):
    queryset = SectionAvailability.objects.all()
    serializer_class = SectionAvailabilitySerializer


class CombinedSectionAvailabilityViewSet(ROMVS):
    queryset = SectionCombinedAvailability.objects.all()
    serializer_class = CombinedSectionAvailabilitySerializer


class SectionRestrictionViewSet(ROMVS):
    queryset = SectionRestriction.objects.all()
    serializer_class = SectionRestrictionSerializer


class MeetingInformationViewSet(ROMVS):
    queryset = MeetingInformation.objects.all()
    serializer_class = MeetingInformationSerializer


class CoverageViewSet(ROMVS):
    queryset = SectionCoverage.objects.all()
    serializer_class = SectionCoverageSerializer
    pagination_class = None
