from django.urls import include, path
from rest_framework.routers import DefaultRouter

from spire.views import (CourseViewSet, SectionViewSet, StaffViewSet,
                         SubjectsViewSet, CoverageViewSet)

router = DefaultRouter()
router.register("courses", CourseViewSet, basename="courses")
router.register("subjects", SubjectsViewSet, basename="subjects")
router.register("sections", SectionViewSet, basename="sections")
router.register("staff", StaffViewSet, basename="staff")
router.register("coverage", CoverageViewSet, basename="coverage")

urlpatterns = [
    path("", include(router.urls)),
]
