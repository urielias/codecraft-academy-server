from django.db import models
from users.models import User


class Course(models.Model):
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    rating = models.IntegerField(default=0)

    def student_enrolled(self, student_id: str):
        return CourseStudent.objects.filter(
            student_id=student_id, course=self).exists()


class CourseStudent(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    text_feedback = models.TextField(blank=True, null=True)
    numeric_feedback = models.IntegerField(null=True)


class Section(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')


class TextElement(models.Model):
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name='text_elements')
    order = models.IntegerField(default=0)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, default='')


class VideoElement(models.Model):
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name='video_elements')
    order = models.IntegerField(default=0)
    title = models.CharField(max_length=200)
    content = models.URLField()


class Resource(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='resources')
    name = models.CharField(max_length=200)
    url = models.URLField()
