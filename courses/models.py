from django.db import models
from users.models import User


class Course(models.Model):
    course_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='courses_taught')


class Enrollment(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='enrolled_students')


class Feedback(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='feedbacks')
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='given_feedbacks')
    feedback_content = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)
