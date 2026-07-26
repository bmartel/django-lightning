from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model ready out of the box for django-lightning applications."""

    bio = models.TextField(blank=True, default="")
    avatar_url = models.URLField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return self.username


class AsyncMigration(models.Model):
    """Tracks status, batch execution, and progress of non-blocking background data migrations."""

    STATUS_PENDING = "PENDING"
    STATUS_RUNNING = "RUNNING"
    STATUS_DEFERRED = "DEFERRED"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_FAILED = "FAILED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_RUNNING, "Running"),
        (STATUS_DEFERRED, "Deferred"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    ]

    name = models.CharField(max_length=255, unique=True, db_index=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True
    )
    batch_size = models.PositiveIntegerField(default=1000)
    processed_count = models.PositiveIntegerField(default=0)
    total_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True, default="")
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} [{self.status}] ({self.processed_count}/{self.total_count})"
