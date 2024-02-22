from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from users.permissions import IsAuthenticated, IsStudentUser

from .models import Course
from .permissions import IsTeacherOrEnrolledStudent
from .serializers import CourseSerializer, CoursePreviewSerializer


class CourseListView(ListAPIView):
    permission_classes = [IsAuthenticated, IsStudentUser]

    def get(self, request):
        user_id = request.user.id
        courses = Course.objects.all()
        serializer = CoursePreviewSerializer(
            courses, many=True, context={'user_id': user_id})

        return Response(serializer.data)


class CourseDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrEnrolledStudent]

    def get(self, request, id):
        course = Course.objects.get(pk=id)
        self.check_object_permissions(request, course)
        serializer = CourseSerializer(course)

        return Response(serializer.data)
