from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from users.models import User
from users.permissions import IsAuthenticated, IsStudentUser

from .models import Course, CourseStudent
from .serializers import CourseSerializer, CourseStudentSerializer
from .permissions import IsTeacherOrEnrolledStudent, IsCourseTeacher, IsNotEnrolledStudent


class CourseListView(ListAPIView):
    permission_classes = [IsAuthenticated, IsStudentUser]

    def get(self, request):
        user_id: int = request.user.id
        courses = Course.objects.all()
        serializer = CourseSerializer(
            courses, many=True, context={'preview': True, 'user_id': user_id})

        return Response(serializer.data)


class CourseDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrEnrolledStudent]

    def get(self, request, id):
        course = Course.objects.get(pk=id)
        self.check_object_permissions(request, course)
        serializer = CourseSerializer(course)

        return Response(serializer.data)


class StudentEnrollView(APIView):
    permission_classes = [IsAuthenticated, IsNotEnrolledStudent]

    def post(self, request, course_id):
        student_id: int = request.user.pk
        serializer = CourseStudentSerializer(
            data={'student': student_id, 'course': course_id})

        if serializer.is_valid() and not serializer.is_enrolled(student_id, course_id):
            serializer.save()
            return Response({'message': 'Student enrolled in course successfully'}, status=201)
        else:
            return Response(serializer.errors, status=400)


class StudentRemoveView(APIView):
    permission_classes = [IsAuthenticated, IsCourseTeacher]

    def delete(self, request, student_id, course_id):
        student = User.objects.get(pk=student_id)
        course = Course.objects.get(pk=course_id)
        course_student = CourseStudent.objects.get(
            student=student, course=course)
        self.check_object_permissions(request, obj=course)
        course_student.delete()

        return Response({'message': 'Student removed from course successfully'}, status=202)
