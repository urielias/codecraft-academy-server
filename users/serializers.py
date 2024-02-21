from .models import User, UserProfile
from rest_framework import serializers
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email',
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
        first_name = validated_data.pop('first_name', "")
        last_name = validated_data.pop('last_name', "")
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            user_type=User.UserType.STUDENT
        )
        user.set_password(validated_data['password'])
        UserProfile.objects.create(
            user=user, first_name=first_name, last_name=last_name)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate_username(self, username):
        return username

    def validate_password(self, password):
        return password
