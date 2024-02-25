from django.contrib import admin

from .models import ChatRoom, Message


@admin.register(ChatRoom, Message)
class ChatAdmin(admin.ModelAdmin):
    pass
