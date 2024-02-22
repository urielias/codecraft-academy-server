from django.urls import path
from .views import CourseListView, CourseDetailView

urlpatterns = [
    path("", CourseListView.as_view(), name="course_list"),
    path("detail/<int:id>/", CourseDetailView.as_view(), name="course_detail"),
]
