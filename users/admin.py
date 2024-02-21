from django.contrib import admin

from .models import User, UserProfile


@admin.register(User, UserProfile)
class UserAdmin(admin.ModelAdmin):
    pass
