from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from app.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom UserAdmin displaying custom fields in Django Admin out of the box."""

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "created_at",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)

    # Include custom bio & avatar_url in admin detail view
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Profile Information", {"fields": ("bio", "avatar_url")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Profile Information", {"fields": ("bio", "avatar_url")}),
    )
