from django.urls import reverse
from rest_framework.test import APITestCase

from users.models import User

from .models import Course, CourseStudent, Section, TextElement, Resource


class CourseListViewTests(APITestCase):
    """
        Tests for the CourseListView.

        Verifies that different types of users (unauthenticated, students, and teachers) can access the course list
        with the appropriate permissions and receive the correct response based on their role.
    """

    def setUp(self):
        self.student_user = User.objects.create(
            username='student', password='pass', user_type=User.UserType.STUDENT)
        self.teacher_user = User.objects.create(
            username='teacher', password='pass', user_type=User.UserType.TEACHER)
        self.course1 = Course.objects.create(
            name='Course 1', description='Desc 1', rating=5, teacher=self.teacher_user)
        self.course2 = Course.objects.create(
            name='Course 2', description='Desc 2', rating=4, teacher=self.teacher_user)

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

        for course_data in response.data:
            self.assertTrue(course_data['teaching'])
            self.assertFalse(course_data['enrolled'])


class CourseDetailViewTests(APITestCase):
    """
        Tests for the CourseDetailView.

        Ensures that course details are accessible to authenticated users based on their roles
        (teacher or enrolled student) and that unenrolled students or unauthenticated users
        are denied access.
    """

    def setUp(self):
        self.teacher = User.objects.create(
            username='teacher', password='pass', user_type='TEACHER')
        self.student = User.objects.create(
            username='student1', password='pass', user_type='STUDENT')
        self.other_student = User.objects.create(
            username='student2', password='pass', user_type='STUDENT')

        self.course = Course.objects.create(
            name='Test Course', description='Test Description', teacher=self.teacher)

        self.resource = Resource.objects.create(
            course=self.course, name='Test Resource', url='resource_url'
        )

        self.section = Section.objects.create(
            course=self.course, name='my_section', description='my_section_description'
        )

        self.textElement = TextElement.objects.create(
            section=self.section, title='my_element', content='my_element_content'
        )

        CourseStudent.objects.create(student=self.student, course=self.course)

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


class StudentEnrollViewTests(APITestCase):
    """
        Tests for the StudentEnrollView.

        Confirms that students can enroll in a course successfully, unauthorized access is blocked,
        and already enrolled students cannot enroll again in the same course.
    """

    def setUp(self):
        self.student_user = User.objects.create(
            first_name='Student',
            last_name='S1',
            username='student',
            password='testpass123',
            user_type=User.UserType.STUDENT)
        self.teacher_user = User.objects.create(
            first_name='Teacher',
            last_name='T1',
            username='teacher',
            password='testpass123',
            user_type=User.UserType.TEACHER
        )

        self.course = Course.objects.create(
            name="Test Course", description="Test Description", teacher=self.teacher_user)

        self.data = {'course_id': self.course.pk}
        self.enroll_url = reverse('course_enroll')

    def test_student_enrollment_success(self):
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(self.enroll_url, self.data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(CourseStudent.objects.filter(
            student=self.student_user, course=self.course).exists())

    def test_enrollment_unauthorized(self):
        self.client.logout()
        response = self.client.post(self.enroll_url, self.data)
        self.assertEqual(response.status_code, 401)

    def test_student_already_enrolled(self):
        CourseStudent.objects.create(
            student=self.student_user, course=self.course)

        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(self.enroll_url, self.data)
        self.assertEqual(response.status_code, 400)


class StudentRemoveViewTests(APITestCase):
    """
        Tests for the StudentRemoveView.

        Checks that teachers can successfully remove students from their courses, unauthorized
        users cannot remove students, and ensures proper permissions are enforced.
    """

    def setUp(self):
        self.student_user = User.objects.create(
            first_name='Student',
            last_name='S1',
            username='student',
            password='testpass123',
            user_type=User.UserType.STUDENT)
        self.teacher_user = User.objects.create(
            first_name='Teacher',
            last_name='T1',
            username='teacher',
            password='testpass123',
            user_type=User.UserType.TEACHER
        )

        self.course = Course.objects.create(
            name="Test Course", description="Test Description", teacher=self.teacher_user)

        self.remove_url = reverse('course_remove')

    def test_student_removal_success(self):
        CourseStudent.objects.create(
            student=self.student_user, course=self.course)

        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.delete(self.remove_url, {
            'student_id': self.student_user.pk,
            'course_id': self.course.pk
        })
        self.assertEqual(response.status_code, 202)
        self.assertFalse(CourseStudent.objects.filter(
            student=self.student_user, course=self.course).exists())

    def test_remove_student_unauthorized(self):
        CourseStudent.objects.create(
            student=self.student_user, course=self.course)

        self.client.force_authenticate(user=self.student_user)
        response = self.client.delete(self.remove_url, {
            'student_id': self.student_user.pk,
            'course_id': self.course.pk
        })
        self.assertEqual(response.status_code, 403)


class CourseViewTestCase(APITestCase):
    """
        Tests for creating and updating courses through the CourseView.

        Verifies that teachers can create new courses and update existing ones, ensuring that
        the course data is properly handled and persisted.
    """

    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher', password='testpass123', user_type=User.UserType.TEACHER)
        self.client.force_authenticate(user=self.teacher)
        self.course = Course.objects.create(
            name="Test Course", description="Test Description", teacher=self.teacher)
        self.url = reverse('course_edit')

    def test_create_course(self):
        data = {'name': 'New Test Course',
                'description': 'New Course Description'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue('id' in response.data)

    def test_update_course(self):
        data = {'course_id': self.course.pk, 'name': 'Updated Test Course'}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, 'Updated Test Course')
