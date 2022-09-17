from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.viewsets import ReadOnlyModelViewSet

from spire.models import (
    AcademicGroup,
    Building,
    BuildingRoom,
    Course,
    CourseDetail,
    CourseEnrollmentInformation,
    CourseOffering,
    Instructor,
    Section,
    SectionAvailability,
    SectionCombinedAvailability,
    SectionCoverage,
    SectionDetail,
    SectionMeetingInformation,
    SectionRestriction,
    Subject,
    Term,
    TermEvent,
)
from spire.serializers.academic_group import AcademicGroupSerializer
from spire.serializers.building import BuildingRoomSerializer, BuildingSerializer
from spire.serializers.course import (
    CourseDetailSerializer,
    CourseEnrollmentInformationSerializer,
    CourseOfferingSerializer,
    CourseSerializer,
)
from spire.serializers.instructor import InstructorSerializer
from spire.serializers.section import (
    SectionAvailabilitySerializer,
    SectionCombinedAvailabilitySerializer,
    SectionCoverageSerializer,
    SectionDetailSerializer,
    SectionMeetingInformationSerializer,
    SectionRestrictionSerializer,
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


class SubjectViewSet(BaseViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class CourseViewSet(BaseViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CourseDetailViewSet(BaseViewSet):
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


class SectionDetailViewSet(BaseViewSet):
    queryset = SectionDetail.objects.all()
    serializer_class = SectionDetailSerializer


class SectionAvailabilityViewSet(BaseViewSet):
    queryset = SectionAvailability.objects.all()
    serializer_class = SectionAvailabilitySerializer


class SectionCombinedAvailabilityViewSet(BaseViewSet):
    queryset = SectionCombinedAvailability.objects.all()
    serializer_class = SectionCombinedAvailabilitySerializer


class SectionRestrictionViewSet(BaseViewSet):
    queryset = SectionRestriction.objects.all()
    serializer_class = SectionRestrictionSerializer


class SectionMeetingInformationViewSet(BaseViewSet):
    queryset = SectionMeetingInformation.objects.all()
    serializer_class = SectionMeetingInformationSerializer


class CoverageViewSet(BaseViewSet):
    queryset = SectionCoverage.objects.all()
    serializer_class = SectionCoverageSerializer
