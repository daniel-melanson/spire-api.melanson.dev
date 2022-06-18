from django.urls import include, path
from rest_framework.routers import DefaultRouter

from spire.views import (
    CourseDetailsViewSet,
    CourseEnrollmentInformationViewSet,
    CourseViewSet,
    CoverageViewSet,
    SectionViewSet,
    StaffViewSet,
    SubjectsViewSet,
)

router = DefaultRouter()
router.register("subjects", SubjectsViewSet, basename="subject")
router.register("courses", CourseViewSet, basename="course")
router.register("course-details", CourseDetailsViewSet, basename="details")
router.register("course-enroll-info", CourseEnrollmentInformationViewSet, basename="enroll-info")
router.register("sections", SectionViewSet, basename="section")
router.register("staff", StaffViewSet, basename="staff")
router.register("coverage", CoverageViewSet, basename="coverage")

urlpatterns = [
    path("", include(router.urls)),
]
