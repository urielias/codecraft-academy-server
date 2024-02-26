from django.urls import path

from .views import LoginAPIView, LogoutAPIView, SignupAPIView, FetchStudents, FetchTeachers

urlpatterns = [
    # Endpoint for user login.
    # This route connects to the LoginAPIView, which handles user authentication,
    # and upon successful authentication, returns a token for accessing protected routes.
    path('login/', LoginAPIView.as_view(), name='login'),

    # Endpoint for user logout.
    # The LogoutAPIView is used here to handle the invalidation and deletion of the user's token,
    # effectively logging them out of the system.
    path('logout/', LogoutAPIView.as_view(), name='logout'),

    # Endpoint for new user registration.
    # SignupAPIView allows new users to create an account by providing necessary information.
    path('signup/', SignupAPIView.as_view(), name='signup'),

    # Endpoint for listing student.
    # FetchStudents view provides a list of users marked as students, optionally filtered by a search query.
    path('list_students/', FetchStudents.as_view(), name='list_students'),

    # Endpoint for listing teacher.
    # Similar to FetchStudents, FetchTeachers view returns a list of teacher users,
    path('list_teachers/', FetchTeachers.as_view(), name='list_teachers'),
]
