from django.urls import reverse
from rest_framework.test import APITestCase

from users.models import User

from .models import Course, CourseStudent, Section, TextElement


class CourseListViewTests(APITestCase):
    def setUp(self):
        # Create users
        self.student_user = User.objects.create(
            username='student', password='pass', user_type=User.UserType.STUDENT)
        self.teacher_user = User.objects.create(
            username='teacher', password='pass', user_type=User.UserType.TEACHER)

        # Create courses
        self.course1 = Course.objects.create(
            name='Course 1', description='Desc 1', rating=5, teacher=self.teacher_user)
        self.course2 = Course.objects.create(
            name='Course 2', description='Desc 2', rating=4, teacher=self.teacher_user)

        # Enroll student in course1
        CourseStudent.objects.create(
            student=self.student_user, course=self.course1)

        self.url = reverse('course_list')

    def test_access_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_access_student_user(self):
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # Verify the enrolled and teaching fields
        for course_data in response.data:
            if course_data['name'] == 'Course 1':
                self.assertTrue(course_data['enrolled'])
                self.assertFalse(course_data['teaching'])
            else:
                self.assertFalse(course_data['enrolled'])
                self.assertFalse(course_data['teaching'])

    def test_access_teacher_user(self):
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # Verify the enrolled and teaching fields
        for course_data in response.data:
            self.assertTrue(course_data['teaching'])
            self.assertFalse(course_data['enrolled'])


class CourseDetailViewTests(APITestCase):
    def setUp(self):
        # Create users
        self.teacher = User.objects.create(
            username='teacher', password='pass', user_type='TEACHER')
        self.student = User.objects.create(
            username='student1', password='pass', user_type='STUDENT')
        self.other_student = User.objects.create(
            username='student2', password='pass', user_type='STUDENT')

        # Create a course
        self.course = Course.objects.create(
            name='Test Course', description='Test Description', teacher=self.teacher)

        # Create a section
        self.section = Section.objects.create(
            course=self.course, name='my_section', description='my_section_description'
        )

        # Create an element
        self.textElement = TextElement.objects.create(
            section=self.section, title='my_element', content='my_element_content'
        )

        # Enroll the student in the course
        CourseStudent.objects.create(student=self.student, course=self.course)

        # URL for the course detail view
        self.url = reverse('course_detail', kwargs={'id': self.course.pk})

    def test_access_by_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_access_by_enrolled_student(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_access_by_unenrolled_student(self):
        self.client.force_authenticate(user=self.other_student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_access_by_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
