from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.viewsets import ReadOnlyModelViewSet

from config.settings import VIEW_CACHE_TTL
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


class BaseViewSet(ReadOnlyModelViewSet):
    @method_decorator(cache_page(VIEW_CACHE_TTL))
    def dispatch(self, *args, **kwargs):
        return super(BaseViewSet, self).dispatch(*args, **kwargs)


class AcademicGroupViewSet(BaseViewSet):
    queryset = AcademicGroup.objects.all()
    serializer_class = AcademicGroupSerializer


class SubjectViewSet(BaseViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class CourseViewSet(BaseViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CourseDetailsViewSet(BaseViewSet):
    queryset = CourseDetail.objects.all()
    serializer_class = CourseDetailSerializer


class CourseEnrollmentInformationViewSet(BaseViewSet):
    queryset = CourseEnrollmentInformation.objects.all()
    serializer_class = CourseEnrollmentInformationSerializer


class CourseOfferingViewSet(BaseViewSet):
    queryset = CourseOffering.objects.all()
    serializer_class = CourseOfferingSerializer


class InstructorViewSet(BaseViewSet):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer


class SectionViewSet(BaseViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer


class SectionDetailsViewSet(BaseViewSet):
    queryset = SectionDetail.objects.all()
    serializer_class = SectionDetailSerializer


class SectionAvailabilityViewSet(BaseViewSet):
    queryset = SectionAvailability.objects.all()
    serializer_class = SectionAvailabilitySerializer


class CombinedSectionAvailabilityViewSet(BaseViewSet):
    queryset = SectionCombinedAvailability.objects.all()
    serializer_class = CombinedSectionAvailabilitySerializer


class SectionRestrictionViewSet(BaseViewSet):
    queryset = SectionRestriction.objects.all()
    serializer_class = SectionRestrictionSerializer


class MeetingInformationViewSet(BaseViewSet):
    queryset = MeetingInformation.objects.all()
    serializer_class = MeetingInformationSerializer


class CoverageViewSet(BaseViewSet):
    queryset = SectionCoverage.objects.all()
    serializer_class = SectionCoverageSerializer
