from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_teacher = models.BooleanField(default=False)


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)
    real_name = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)
