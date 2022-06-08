from django.urls import include, path
from rest_framework.routers import DefaultRouter

from spire.views import (CourseViewSet, SectionViewSet, StaffViewSet,
                         SubjectsViewSet)

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")
router.register(r"subjects", SubjectsViewSet, basename="subjects")
router.register(r"sections", SectionViewSet, basename="sections")
router.register(r"staff", StaffViewSet, basename="staff")

urlpatterns = [
    path("", include(router.urls)),
]
