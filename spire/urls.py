from django.urls import include, path
from rest_framework.routers import DefaultRouter

# from spire.views import (
#     CourseDetailsViewSet,
#     CourseEnrollmentInformationViewSet,
#     CourseViewSet,
#     CoverageViewSet,
#     InstructorViewSet,
#     MeetingInformationViewSet,
#     SectionDetailsViewSet,
#     SectionViewSet,
#     SubjectsViewSet,
# )

router = DefaultRouter()
# router.register("subjects", SubjectsViewSet, basename="subject")
# router.register("courses", CourseViewSet, basename="course")
# router.register("course-details", CourseDetailsViewSet, basename="coursedetail")
# router.register(
#     "course-enrollment-information",
#     CourseEnrollmentInformationViewSet,
#     basename="courseenrollmentinformation",
# )
# router.register("sections", SectionViewSet, basename="section")
# router.register("section-details", SectionDetailsViewSet, basename="sectiondetail")
# router.register("meeting-information", MeetingInformationViewSet, basename="meetinginformation")
# router.register("instructors", InstructorViewSet, basename="instructor")
# router.register("coverage", CoverageViewSet, basename="sectioncoverage")

urlpatterns = [
    path("", include(router.urls)),
]
