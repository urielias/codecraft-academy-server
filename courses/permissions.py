from rest_framework.permissions import BasePermission

from users.models import User


class IsNotEnrolledStudent(BasePermission):
    """
        Allows access only to students who are not enrolled in the course.

        This permission checks if the request user is a student and not currently enrolled in the course,
        denying access to teachers or enrolled students.
    """

    def has_object_permission(self, request, _, obj):
        if not request.user.user_type == User.UserType.STUDENT:
            return False

        return not obj.student_enrolled(request.user)


class IsTeacherOrEnrolledStudent(BasePermission):
    """
        Allows access to teachers of the course or students who are enrolled in it.

        This permission checks if the request user is a teacher or if the student is enrolled in the course,
        granting access based on this condition.
    """

    def has_object_permission(self, request, _, obj):
        if request.user.user_type == User.UserType.TEACHER:
            return True

        return obj.student_enrolled(request.user)


class IsCourseTeacher(BasePermission):
    """
        Allows access only to the teacher of the course.

        This permission ensures that only the teacher who is teaching the course can access certain actions or views.
    """

    def has_object_permission(self, request, _, obj):
        if not request.user.user_type == User.UserType.TEACHER:
            return False

        return obj.is_course_teacher(request.user)
