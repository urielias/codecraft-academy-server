from django.contrib import admin

from .models import Course, CourseStudent, Section, TextElement, VideoElement, Resource


@admin.register(Course, CourseStudent, Section, TextElement, VideoElement, Resource)
class CourseAdmin(admin.ModelAdmin):
    pass
