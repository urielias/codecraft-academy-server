from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.response import Response
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token

from .models import UserProfile
from .serializers import LoginSerializer, UserSerializer


class SignupAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        if not user:
            return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        user_profile = model_to_dict(UserProfile.objects.get(user=user))

        if not user_profile:
            return Response("Server Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        token, _ = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user).data
        user_data["token"] = token.key
        user_data = {**user_data, **user_profile}

        return Response(user_data, status=status.HTTP_200_OK)


class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, username=request.data.get(
            'username'), password=request.data.get('password'))

        if not user:
            return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        user_profile = model_to_dict(UserProfile.objects.get(user=user), fields=[
                                     field.name for field in UserProfile._meta.fields])

        if not user_profile:
            return Response("Server Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        token, _ = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user).data
        user_data["token"] = token.key
        user_data = {*user_data, *user_profile}

        return Response(user_data, status=status.HTTP_200_OK)
