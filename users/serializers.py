from .models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email',
                  'user_type', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email is already in use.")
        return email

    def validate_username(self, username):
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                "This username is already taken.")
        return username

    def create(self, validated_data):
        user = User.objects.create_user(
            user_type=User.UserType.STUDENT, **validated_data)
        user.set_password(validated_data['password'])
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        user = authenticate(username=username, password=password)

        if user:
            return user
        else:
            raise AuthenticationFailed('Incorrect username or password')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email',
                  'user_type', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}
