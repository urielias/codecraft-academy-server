from .models import User
from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):
    """
        Permission check for authenticated users.

        Ensures that the current request is made by a user who is authenticated. This class can be used
        to protect views and ensure that only authenticated users have access.

        Methods:
            has_permission: Checks if the request comes from an authenticated user.
    """

    def has_permission(self, request):
        return bool(request.user and request.user.is_authenticated)


class IsStudentUser(BasePermission):
    """
        Permission check for student users or higher roles.

        Allows access to users identified as students or teachers, effectively restricting access to
        unauthorized user types. This is useful for resources that should be available to all educational
        roles but not to other types of users.

        Methods:
            has_permission: Checks if the user is a student or a teacher.
    """

    def has_permission(self, request):
        return request.user.user_type in [User.UserType.STUDENT, User.UserType.TEACHER]


class IsTeacherUser(BasePermission):
    """
        Permission check for teacher users.

        Restricts access to resources specifically intended for teachers, ensuring that only users
        with a teacher role can access certain views or perform certain actions.

        Methods:
            has_permission: Checks if the user has a teacher role.
    """

    def has_permission(self, request):
        return request.user.user_type == User.UserType.TEACHER
