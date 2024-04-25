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
    CurrentTermsView,
    InstructorViewSet,
    SectionViewSet,
    SubjectViewSet,
    TermViewSet,
)

router = DefaultRouter()


router.register("buildings", BuildingViewSet, basename="building")
router.register("building-rooms", BuildingRoomViewSet, basename="buildingroom")

router.register("terms", TermViewSet, basename="term")

router.register("academic-groups", AcademicGroupViewSet, basename="academicgroup")

router.register("subjects", SubjectViewSet, basename="subject")

router.register("courses", CourseViewSet, basename="course")
router.register("course-offerings", CourseOfferingViewSet, basename="courseoffering")

router.register("instructors", InstructorViewSet, basename="instructor")

router.register("sections", SectionViewSet, basename="section")

router.register("coverage", CoverageViewSet, basename="coverage")

urlpatterns = [
    path("", include(router.urls)),
    path("current-terms/", CurrentTermsView.as_view()),
]
