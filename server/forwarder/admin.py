from django.contrib import admin
from forwarder.models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "created_at", "status")
    list_filter = ("created_at",)
    search_fields = ("message",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
