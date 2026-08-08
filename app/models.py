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
        indexes = [
            models.Index(fields=["-date_joined"], name="user_date_joined_idx"),
        ]
        constraints = [
            # Enforce unique, indexed emails for real addresses while still allowing
            # multiple accounts with a blank email (a partial index also serves the
            # email lookup done at registration).
            models.UniqueConstraint(
                fields=["email"],
                condition=~models.Q(email=""),
                name="user_unique_email_when_set",
            ),
        ]

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

    name = models.CharField(max_length=255, unique=True)
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


class Tenant(models.Model):
    """Multi-tenancy Tenant model representing a workspace, project, or customer scope."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class TenantMember(models.Model):
    """Membership mapping connecting Users to Tenants with role-based access control."""

    ROLE_OWNER = "OWNER"
    ROLE_ADMIN = "ADMIN"
    ROLE_MEMBER = "MEMBER"

    ROLE_CHOICES = [
        (ROLE_OWNER, "Owner"),
        (ROLE_ADMIN, "Admin"),
        (ROLE_MEMBER, "Member"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(
        "app.User", on_delete=models.CASCADE, related_name="tenant_memberships"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # The unique constraint already provides the (tenant, user) composite index,
        # so no explicit Index is needed (it would just duplicate write cost).
        unique_together = [("tenant", "user")]

    def __str__(self):
        return f"{self.user.username} -> {self.tenant.name} [{self.role}]"


class APIKey(models.Model):
    """Authentication API keys for service-to-service and programmatic API access."""

    name = models.CharField(max_length=255)
    prefix = models.CharField(max_length=16, db_index=True)
    key_hash = models.CharField(max_length=128, unique=True)
    user = models.ForeignKey("app.User", on_delete=models.CASCADE, related_name="api_keys")
    is_active = models.BooleanField(default=True, db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"APIKey {self.name} ({self.prefix}...)"
