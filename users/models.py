from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class UserType(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        TEACHER = 'TEACHER', 'Teacher'

    user_type = models.CharField(
        max_length=10, choices=UserType.choices, default=UserType.STUDENT)


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    photo_url = models.CharField(max_length=200, blank=True)
