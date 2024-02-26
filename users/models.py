from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
        Custom User model extending Django's AbstractUser.

        This model adds specific fields to cater to the application's requirements, such as distinguishing
        between different types of users (students and teachers) and storing additional information like
        names and a photo URL.

        Attributes:
            UserType (models.TextChoices): An enumeration of possible user types, including 'STUDENT' and 'TEACHER'.
            user_type (CharField): Specifies the type of user, based on the UserType choices.
            first_name (CharField): The user's first name. Overrides the first_name field from AbstractUser
                                    to customize field options or constraints as necessary.
            last_name (CharField): The user's last name. Overrides the last_name field from AbstractUser
                                to customize field options or constraints as necessary.
            photo_url (CharField): An optional field for storing the URL of the user's photo.

        Methods:
            __str__: Returns a string representation of the user, typically used for administrative interfaces
                    or debugging, which includes the user's full name.
    """
    class UserType(models.TextChoices):
        """
            UserType defines the set of constants representing the possible roles a user can have within the application.
            Each choice is a tuple consisting of an identifier and a human-readable name.
        """
        STUDENT = 'STUDENT', 'Student'
        TEACHER = 'TEACHER', 'Teacher'

    user_type = models.CharField(
        max_length=10, choices=UserType.choices, default=UserType.STUDENT)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    photo_url = models.CharField(max_length=200, blank=True)

    def __str__(self):
        """
            Returns a human-readable string representation of the user, combining their first and last names.

            Returns:
                str: The full name of the user.
        """
        return self.first_name + " " + self.last_name
