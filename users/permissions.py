from .models import User
from rest_framework import permissions


class IsTeacherUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.user_type in [User.UserType.TEACHER])


class IsStudentUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.user_type in [User.UserType.STUDENT, User.UserType.TEACHER])
