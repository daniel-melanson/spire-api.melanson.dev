# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework.viewsets import ReadOnlyModelViewSet

# from spire.models import (
#     Course,
#     CourseDetail,
#     CourseEnrollmentInformation,
#     Instructor,
#     MeetingInformation,
#     Section,
#     SectionCoverage,
#     SectionDetail,
#     Subject,
# )
# from spire.serializers import (
#     CourseDetailSerializer,
#     CourseEnrollmentInformationSerializer,
#     CourseSerializer,
#     InstructorSerializer,
#     MeetingInformationSerializer,
#     SectionCoverageSerializer,
#     SectionDetailSerializer,
#     SectionSerializer,
#     SubjectSerializer,
# )


# class CourseViewSet(ReadOnlyModelViewSet):
#     queryset = Course.objects.all()
#     serializer_class = CourseSerializer


# class CourseDetailsViewSet(ReadOnlyModelViewSet):
#     queryset = CourseDetail.objects.all()
#     serializer_class = CourseDetailSerializer


# class CourseEnrollmentInformationViewSet(ReadOnlyModelViewSet):
#     queryset = CourseEnrollmentInformation.objects.all()
#     serializer_class = CourseEnrollmentInformationSerializer


# class SubjectsViewSet(ReadOnlyModelViewSet):
#     queryset = Subject.objects.all()
#     serializer_class = SubjectSerializer


# class InstructorViewSet(ReadOnlyModelViewSet):
#     queryset = Instructor.objects.all()
#     serializer_class = InstructorSerializer


# class SectionViewSet(ReadOnlyModelViewSet):
#     queryset = Section.objects.all()
#     serializer_class = SectionSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ["course_id"]


# class MeetingInformationViewSet(ReadOnlyModelViewSet):
#     queryset = MeetingInformation.objects.all()
#     serializer_class = MeetingInformationSerializer


# class SectionDetailsViewSet(ReadOnlyModelViewSet):
#     queryset = SectionDetail.objects.all()
#     serializer_class = SectionDetailSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = [
#         "status",
#         "session",
#         "units",
#         "career",
#         "topic",
#     ]


# class CoverageViewSet(ReadOnlyModelViewSet):
#     queryset = SectionCoverage.objects.all()
#     serializer_class = SectionCoverageSerializer
#     pagination_class = None
