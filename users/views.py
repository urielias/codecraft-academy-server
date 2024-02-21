from django.db.models import Q
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import User
from .permissions import IsStudentUser, IsTeacherUser
from .serializers import LoginSerializer, SignupSerializer, UserSerializer


def get_user_data_token(user):
    token, _ = Token.objects.get_or_create(user=user)
    user_data = UserSerializer(user).data
    user_data["token"] = token.key

    return user_data


class SignupAPIView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({}, status=403)

        user = serializer.save()
        user_data = get_user_data_token(user)

        return Response(user_data, status=200)


class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({}, status=403)

        user = serializer.validated_data
        user_data = get_user_data_token(user)

        return Response(user_data, status=200)


class FetchStudents(generics.ListAPIView):
    permission_classes = [IsStudentUser]
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.all().filter(user_type=User.UserType.STUDENT)
        search = self.request.query_params.get("search", None)

        if search is not None and search != "":
            queryset = queryset.filter(Q(first_name__icontains=search) | Q(
                last_name__icontains=search) | Q(username__icontains=search))

        return queryset


class FetchTeachers(generics.ListAPIView):
    permission_classes = [IsTeacherUser]
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.all().filter(user_type=User.UserType.TEACHER)
        search = self.request.query_params.get("search", None)

        if search is not None and search != "":
            queryset = queryset.filter(Q(first_name__icontains=search) | Q(
                last_name__icontains=search) | Q(username__icontains=search))

        return queryset
