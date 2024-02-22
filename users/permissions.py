from .models import User
from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsStudentUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type in [User.UserType.STUDENT, User.UserType.TEACHER]


class IsTeacherUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == User.UserType.TEACHER
