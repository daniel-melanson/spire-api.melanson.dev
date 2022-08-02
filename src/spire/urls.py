from django.urls import include, path
from rest_framework.routers import DefaultRouter

from spire.views import (
    AcademicGroupViewSet,
    CombinedSectionAvailabilityViewSet,
    CourseDetailsViewSet,
    CourseEnrollmentInformationViewSet,
    CourseOfferingViewSet,
    CourseViewSet,
    CoverageViewSet,
    InstructorViewSet,
    MeetingInformationViewSet,
    SectionAvailabilityViewSet,
    SectionDetailsViewSet,
    SectionRestrictionViewSet,
    SectionViewSet,
    SubjectViewSet,
)

router = DefaultRouter()
router.register("academic-groups", AcademicGroupViewSet, basename="academicgroup")

router.register("subjects", SubjectViewSet, basename="subject")

router.register("courses", CourseViewSet, basename="course")
router.register("course-details", CourseDetailsViewSet, basename="coursedetail")
router.register(
    "course-enrollment-information",
    CourseEnrollmentInformationViewSet,
    basename="courseenrollmentinformation",
)
router.register("course-offerings", CourseOfferingViewSet, basename="courseoffering")

router.register("instructors", InstructorViewSet, basename="instructor")

router.register("sections", SectionViewSet, basename="section")
router.register("section-details", SectionDetailsViewSet, basename="sectiondetail")
router.register("section-availability", SectionAvailabilityViewSet, basename="sectionavailability")
router.register(
    "section-combined-availability",
    CombinedSectionAvailabilityViewSet,
    basename="sectioncombinedavailability",
)
router.register("section-restrictions", SectionRestrictionViewSet, basename="sectionrestriction")
router.register("meeting-information", MeetingInformationViewSet, basename="meetinginformation")

router.register("coverage", CoverageViewSet, basename="sectioncoverage")

urlpatterns = [
    path("", include(router.urls)),
]
