from django.urls import path
from .views import CourseListView, CourseDetailView, StudentEnrollView, StudentRemoveView

urlpatterns = [
    path('', CourseListView.as_view(), name='course_list'),
    path('detail/<int:id>/', CourseDetailView.as_view(), name='course_detail'),
    path('course/<int:course_id>/enroll/',
         StudentEnrollView.as_view(), name='course_enroll'),
    path('course/<int:course_id>/remove/<int:student_id>',
         StudentRemoveView.as_view(), name='course_remove'),
]
