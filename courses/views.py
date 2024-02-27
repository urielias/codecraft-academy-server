from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from users.models import User
from users.permissions import IsAuthenticated, IsStudentUser, IsTeacherUser

from .models import Course, CourseStudent
from .serializers import CourseSerializer, CourseStudentSerializer
from .permissions import IsTeacherOrEnrolledStudent, IsCourseTeacher, IsNotEnrolledStudent


class CourseListView(ListAPIView):
    """
        Provides a list view of all courses available in the system.

        Permissions:
            - IsAuthenticated: Ensures that only authenticated users can access this view.
            - IsStudentUser: Further restricts access to authenticated users identified as students.

        The view returns a list of courses with a preview context to limit the amount of detailed information returned.
    """
    permission_classes = [IsAuthenticated, IsStudentUser]

    def get(self, request):
        user_id: int = request.user.id
        courses = Course.objects.all()
        serializer = CourseSerializer(
            courses, many=True, context={'preview': True, 'user_id': user_id})

        return Response(serializer.data)


class CourseDetailView(APIView):
    """
        Provides detailed information for a specific course identified by its ID.

        Permissions:
            - IsAuthenticated: Ensures that only authenticated users can access this view.
            - IsTeacherOrEnrolledStudent: Restricts access to the course's teacher or students who are enrolled in the course.

        Retrieves and serializes detailed information of a course, including sections and resources associated with it.
    """
    permission_classes = [IsAuthenticated, IsTeacherOrEnrolledStudent]

    def get(self, request, id):
        course = Course.objects.get(pk=id)
        self.check_object_permissions(request, course)
        serializer = CourseSerializer(course)

        return Response(serializer.data)


class StudentEnrollView(APIView):
    """
        Handles enrollment of authenticated students into a specified course.

        Permissions:
            - IsAuthenticated: Ensures that only authenticated users can access this view.
            - IsNotEnrolledStudent: Ensures that the user is a student and not already enrolled in the specified course.

        On POST request with a course_id, enrolls the authenticated user (student) into the specified course if not already enrolled.
    """
    permission_classes = [IsAuthenticated, IsNotEnrolledStudent]

    def post(self, request):
        student_id: int = request.user.pk
        course_id = request.data.get('course_id', None)

        serializer = CourseStudentSerializer(
            data={'student': student_id, 'course': course_id})

        if serializer.is_valid() and not serializer.is_enrolled(student_id, course_id):
            serializer.save()
            return Response({'message': 'Student enrolled in course successfully'}, status=201)

        return Response(serializer.errors, status=400)


class StudentRemoveView(APIView):
    """
        Allows for the removal of a student from a specified course.

        Permissions:
            - IsAuthenticated: Ensures that only authenticated users can access this view.
            - IsCourseTeacher: Ensures that only the teacher of the specified course can remove students.

        On DELETE request with student_id and course_id, removes the specified student from the course.
    """
    permission_classes = [IsAuthenticated, IsCourseTeacher]

    def delete(self, request):
        student_id = request.data.get('student_id', None)
        course_id = request.data.get('course_id', None)

        if (not student_id or not course_id):
            return Response({'message': 'Missing data'}, status=400)

        student = User.objects.get(pk=student_id)
        course = Course.objects.get(pk=course_id)
        course_student = CourseStudent.objects.get(
            student=student, course=course)
        self.check_object_permissions(request, obj=course)
        course_student.delete()

        return Response({'message': 'Student removed from course successfully'}, status=202)


class CourseView(APIView):
    """
        Supports creation and partial update of courses.

        Permissions:
            - IsAuthenticated: Ensures that only authenticated users can access this view.
            - IsTeacherUser: Ensures that only users identified as teachers can create or update courses.

        On POST request, creates a new course with the authenticated teacher as the course teacher.
        On PATCH request with course_id, updates the specified fields of an existing course.
    """
    permission_classes = [IsAuthenticated, IsTeacherUser]

    def post(self, request):
        teacher = request.user
        name = request.data.get('name', None)
        description = request.data.get('description', None)

        serializer = CourseSerializer(data={
            'teacher': teacher.pk,
            'name': name,
            'description': description
        })

        if serializer.is_valid():
            course = serializer.save()
            return Response({'id': course.pk}, status=201)

        return Response(serializer.errors, status=400)

    def patch(self, request):
        course_id = request.data.get('course_id')
        name = request.data.get('name', None)
        description = request.data.get('description', None)

        try:
            instance = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({"message": "Course not found"}, status=400)

        raw_data = {'name': name, 'description': description}
        new_data = {k: v for k, v in raw_data.items() if v is not None}

        serializer = CourseSerializer(instance, data=new_data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Course updated successfully'}, status=200)

        return Response(serializer.errors, status=400)
