from django.contrib import admin
from customer.models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "name",
        "phone_number",
        "api_key",
        "created_at",
        "is_verified",
    )
    search_fields = ("name", "phone_number")
    list_filter = ("is_verified",)
    readonly_fields = ("api_key",)
