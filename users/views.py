from django.db.models import Q
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import User
from .permissions import IsAuthenticated, IsStudentUser, IsTeacherUser
from .serializers import LoginSerializer, SignupSerializer, UserSerializer


def get_user_data_token(user: User):
    """
        Generates or retrieves an authentication token for a given user and
        packages the user's data along with the token into a single dictionary.

        Args:
            user (User): The user instance for whom the token is generated or retrieved.

        Returns:
            dict: A dictionary containing the user's serialized data and authentication token.
    """
    token, _ = Token.objects.get_or_create(user=user)
    user_data = UserSerializer(user).data
    user_data["token"] = token.key

    return user_data


class SignupAPIView(APIView):
    """
        API view for user signup.

        Allows new users to register to the system. Upon successful registration,
        it also provides an authentication token for immediate login capability.

        On POST request with user signup data, creates the user and returns its data and token 
    """

    def post(self, request):
        serializer = SignupSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({}, status=403)

        user: User = serializer.save()
        user_data = get_user_data_token(user)

        return Response(user_data, status=200)


class LoginAPIView(APIView):
    """
        API view for user login.

        Authenticates the user and returns an authentication token if the credentials are valid.

        On POST request with user login data, logs the user in and returns its data and token 
    """

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({}, status=403)

        user = serializer.validated_data
        user_data = get_user_data_token(user)

        return Response(user_data, status=200)


class LogoutAPIView(APIView):
    """
        API view for user logout.

        Invalidates the user's authentication token, effectively logging them out.

        on POST request, uses data from the request headers to log out a user by deleting their authentication token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response({"message": "Logged out successfully"}, status=200)
        except Token.DoesNotExist:
            return Response({"error": "Token not found"}, status=400)


class FetchStudents(generics.ListAPIView):
    """
        API view for fetching a list of student users.

        Supports searching by username, first name, or last name.
    """
    permission_classes = [IsAuthenticated, IsStudentUser]
    serializer_class = UserSerializer

    def get_queryset(self):
        """
            Overrides the default queryset to return a list of students, optionally filtered by a search query.

            Returns:
                QuerySet: A queryset of User instances filtered by user_type and search query.
        """
        queryset = User.objects.all().filter(user_type=User.UserType.STUDENT)
        search = self.request.query_params.get("search", None)

        if search is not None and search != "":
            queryset = queryset.filter(Q(first_name__icontains=search) | Q(
                last_name__icontains=search) | Q(username__icontains=search))

        return queryset


class FetchTeachers(generics.ListAPIView):
    """
        ListAPIView for fetching users designated as teachers in the system.

        This view extends Django REST Framework's generics.ListAPIView to provide a list
        of users with a user_type of TEACHER. It supports searching by username, first name,
        or last name to allow for easy filtering of teacher records.

        Attributes:
            permission_classes: Ensures that the requestor is authenticated and has a teacher user type.
            serializer_class: Specifies the serializer to use for formatting the teacher user data.
    """
    permission_classes = [IsAuthenticated, IsTeacherUser]
    serializer_class = UserSerializer

    def get_queryset(self):
        """
            Overrides the default queryset to filter users by the teacher role and optional search criteria.

            The search functionality is case-insensitive and matches partial strings in the username,
            first name, and last name fields, allowing for flexible user searches.

            Returns:
                QuerySet: A Django QuerySet containing User instances that match the filter criteria.
        """
        queryset = User.objects.all().filter(user_type=User.UserType.TEACHER)
        search: str = self.request.query_params.get("search", None)

        # If a search query is provided, filter the queryset based on the search criteria.
        if search is not None and search != "":
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(username__icontains=search)
            )

        return queryset
