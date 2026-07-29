from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from app.models import AsyncMigration, User


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
    fieldsets = tuple(BaseUserAdmin.fieldsets or ()) + (
        ("Profile Information", {"fields": ("bio", "avatar_url")}),
    )
    add_fieldsets = tuple(BaseUserAdmin.add_fieldsets or ()) + (
        ("Profile Information", {"fields": ("bio", "avatar_url")}),
    )


@admin.register(AsyncMigration)
class AsyncMigrationAdmin(admin.ModelAdmin):
    """Admin configuration for tracking background async data migrations."""

    list_display = (
        "name",
        "status",
        "processed_count",
        "total_count",
        "batch_size",
        "started_at",
        "completed_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("name", "error_message")
    readonly_fields = (
        "name",
        "status",
        "processed_count",
        "total_count",
        "error_message",
        "started_at",
        "completed_at",
        "created_at",
        "updated_at",
    )
