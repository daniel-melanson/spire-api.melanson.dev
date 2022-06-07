from django.urls import path

from spire.views import CourseRetrieve, SectionRetrieve, SubjectCourseList, SubjectsView

urlpatterns = [
    path("courses/<str:subject_id>/", SubjectCourseList.as_view()),
    path("courses/<str:subject_id>/<str:number>/", CourseRetrieve.as_view()),
    path("courses/<str:subject_id>/<str:number>/sections", SectionRetrieve.as_view()),
    path("subjects/", SubjectsView.as_view()),
]
