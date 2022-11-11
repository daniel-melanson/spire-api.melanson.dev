# type: ignore
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from spire.views import (
    AcademicGroupViewSet,
    BuildingRoomViewSet,
    BuildingViewSet,
    CourseOfferingViewSet,
    CourseViewSet,
    CoverageViewSet,
    InstructorViewSet,
    SectionViewSet,
    SubjectViewSet,
    TermEventViewSet,
    TermViewSet,
)

router = DefaultRouter()


router.register("buildings", BuildingViewSet, basename="building")
router.register("building-rooms", BuildingRoomViewSet, basename="buildingroom")

router.register("terms", TermViewSet, basename="term")
# router.register("term-events", TermEventViewSet, basename="termevent")

router.register("academic-groups", AcademicGroupViewSet, basename="academicgroup")

router.register("subjects", SubjectViewSet, basename="subject")

router.register("courses", CourseViewSet, basename="course")
#router.register("course-detail", CourseDetailViewSet, basename="coursedetail")
# router.register(
#     "course-enrollment-information",
#     CourseEnrollmentInformationViewSet,
#     basename="courseenrollmentinformation",
# )
router.register("course-offerings", CourseOfferingViewSet, basename="courseoffering")

router.register("instructors", InstructorViewSet, basename="instructor")

router.register("sections", SectionViewSet, basename="section")
# router.register("section-detail", SectionDetailViewSet, basename="sectiondetail")
# router.register("section-availability", SectionAvailabilityViewSet, basename="sectionavailability")
# router.register(
#     "section-combined-availability",
#     SectionCombinedAvailabilityViewSet,
#     basename="sectioncombinedavailability",
# )
# router.register("section-restriction", SectionRestrictionViewSet, basename="sectionrestriction")
# router.register(
#     "section-meeting-information", SectionMeetingInformationViewSet, basename="sectionmeetinginformation"
# )

router.register("coverage", CoverageViewSet, basename="coverage")

urlpatterns = [
    path("", include(router.urls)),
]
