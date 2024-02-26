from .models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


class SignupSerializer(serializers.ModelSerializer):
    """
        A serializer for registering new users.

        Validates provided username and email to ensure uniqueness within the database, then creates a new user instance with the validated data.

        Attributes:
            Meta.model: The user model associated with this serializer.
            Meta.fields: Fields included in the serialization/deserialization process.
            Meta.extra_kwargs: Specifies that the password field is write-only to ensure it is not returned in any response.
    """

    class Meta:
        model = User
        fields = ['username', 'password', 'email',
                  'user_type', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, email):
        """
            Validates that the provided email is not already in use by another account.

            Args:
                email (str): The email address to validate.

            Returns:
                str: The validated email if it's unique.
        """
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email is already in use.")
        return email

    def validate_username(self, username):
        """
            Validates that the provided username is not already taken.

            Args:
                username (str): The username to validate.

            Returns:
                str: The validated username if it's unique.
        """
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                "This username is already taken.")
        return username

    def create(self, validated_data):
        """
            Creates a new user instance with the validated data.

            Args:
                validated_data (dict): The validated user data.

            Returns:
                User: The newly created user instance.
        """
        user = User.objects.create_user(
            user_type=User.UserType.STUDENT, **validated_data)
        user.set_password(validated_data['password'])
        return user


class LoginSerializer(serializers.Serializer):
    """
        A serializer for user login.

        Authenticates a user based on username and password, raising an exception if authentication fails.

        Fields:
            username (CharField): The username field for authentication.
            password (CharField): The password field for authentication.
    """
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        """
            Validates the user's credentials.

            Args:
                attrs (dict): The attributes to validate, containing username and password.

            Returns:
                User: The authenticated user instance.
        """
        username = attrs.get('username')
        password = attrs.get('password')
        user = authenticate(username=username, password=password)

        if user:
            return user
        else:
            raise AuthenticationFailed('Incorrect username or password')


class UserSerializer(serializers.ModelSerializer):
    """
        A serializer for the User model.

        Handles serialization and deserialization of User instances. Passwords are handled as write-only fields for security.

        Attributes:
            Meta.model: The user model associated with this serializer.
            Meta.fields: Fields included in the serialization/deserialization process.
            Meta.extra_kwargs: Specifies that the password field is write-only.
    """
    class Meta:
        model = User
        fields = ['username', 'password', 'email',
                  'user_type', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}
