from django.urls import path
from .views import LoginAPIView, SignupAPIView, FetchStudents, FetchTeachers

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("signup/", SignupAPIView.as_view(), name="signup"),
    path("list_students/", FetchStudents.as_view(), name="list_students"),
    path("list_teachers/", FetchTeachers.as_view(), name="list_teachers"),
]
