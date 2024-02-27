from django.urls import path

from .views import CourseListView, CourseDetailView, StudentEnrollView, StudentRemoveView, CourseView

urlpatterns = [
    # Course List URL
    # This endpoint provides a list of all available courses.
    path('', CourseListView.as_view(), name='course_list'),

    # Course Detail URL
    # This endpoint provides detailed information for a specific course identified by its ID.
    path('detail/<int:id>/', CourseDetailView.as_view(), name='course_detail'),

    # Student Enrollment URL
    # This endpoint handles the enrollment of a student into a course.
    path('enroll/', StudentEnrollView.as_view(), name='course_enroll'),

    # Student Removal URL
    # This endpoint allows for the removal of a student from a course.
    path('remove/', StudentRemoveView.as_view(), name='course_remove'),

    # Course Edit URL
    # This endpoint provides an interface for creating a new course or editing the details of an existing one.
    path('edit/', CourseView.as_view(), name='course_edit'),
]
