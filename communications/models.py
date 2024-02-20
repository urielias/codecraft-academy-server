from django.db import models
from users.models import User


class StatusUpdate(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='status_updates')
    content = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)
