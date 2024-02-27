from django.db import models
from users.models import User


class Course(models.Model):
    """
        Represents a course taught by a teacher with enrolled students.

        Attributes:
            teacher (ForeignKey): A reference to the User model, identifying the teacher of the course.
            name (CharField): The name of the course.
            description (TextField): A brief description of the course, optional.
            rating (IntegerField): An overall rating for the course, defaulting to 0.
            students (ManyToManyField): A many-to-many relationship with the User model, through the CourseStudent model,
                                        representing students enrolled in the course.

        Methods:
            student_enrolled: Checks if a specific student is enrolled in the course.
            is_course_teacher: Verifies if a given user is the teacher of the course.
    """
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='courses_taught')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    rating = models.IntegerField(default=0)
    students = models.ManyToManyField(
        User, through='CourseStudent', related_name='courses_enrolled')

    def student_enrolled(self, student: User):
        return CourseStudent.objects.filter(
            student=student, course=self).exists()

    def is_course_teacher(self, teacher: User):
        return self.teacher == teacher


class CourseStudent(models.Model):
    """
        Intermediate model for the many-to-many relationship between the Course and User models.

        Represents a student's enrollment in a course, including optional feedback.

        Attributes:
            student (ForeignKey): A reference to the User model for the student.
            course (ForeignKey): A reference to the Course model.
            text_feedback (TextField): Optional textual feedback provided by the student.
            numeric_feedback (IntegerField): Optional numeric feedback provided by the student, e.g., a rating.
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    text_feedback = models.TextField(blank=True, null=True)
    numeric_feedback = models.IntegerField(null=True)


class Section(models.Model):
    """
        Represents a section within a course, containing educational content like text or videos.

        Attributes:
            course (ForeignKey): The course this section belongs to.
            name (CharField): The name of the section.
            description (TextField): A brief description of the section, optional.
    """
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')


class TextElement(models.Model):
    """
        Represents a textual content element within a course section.

        Attributes:
            section (ForeignKey): The section this text element belongs to.
            order (IntegerField): The order of the text element within its section.
            title (CharField): The title of the text element.
            content (TextField): The body of the text element.
    """
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name='text_elements')
    order = models.IntegerField(default=0)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, default='')


class VideoElement(models.Model):
    """
        Represents a video content element within a course section.

        Attributes:
            section (ForeignKey): The section this video element belongs to.
            order (IntegerField): The order of the video element within its section.
            title (CharField): The title of the video element.
            content (URLField): The URL to the video content.
    """
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name='video_elements')
    order = models.IntegerField(default=0)
    title = models.CharField(max_length=200)
    content = models.URLField()


class Resource(models.Model):
    """
        Represents an external resource related to a course, such as additional reading material or tools.

        Attributes:
            course (ForeignKey): The course this resource is associated with.
            name (CharField): The name of the resource.
            url (URLField): The URL to the external resource.
    """
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='resources')
    name = models.CharField(max_length=200)
    url = models.URLField()
