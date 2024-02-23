from rest_framework.permissions import BasePermission

from users.models import User


class IsNotEnrolledStudent(BasePermission):
    def has_object_permission(self, request, _, obj):
        if request.user.user_type == User.UserType.TEACHER:
            return False

        return not obj.student_enrolled(request.user)


class IsTeacherOrEnrolledStudent(BasePermission):
    def has_object_permission(self, request, _, obj):
        if request.user.user_type == User.UserType.TEACHER:
            return True

        return obj.student_enrolled(request.user)


class IsCourseTeacher(BasePermission):
    def has_object_permission(self, request, _, obj):
        if not request.user.user_type == User.UserType.TEACHER:
            return False

        return obj.is_course_teacher(request.user)


class IsNotEnrolledStudent(BasePermission):
    def has_object_permission(self, request, _, obj):
        if not request.user.user_type == User.UserType.STUDENT:
            return False

        return not obj.is_enrolled(request.user)
