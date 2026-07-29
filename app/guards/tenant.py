"""Tenant awareness and scope guards for multi-tenant django-lightning apps."""

from django_bolt import Header, Request
from django_bolt.exceptions import HTTPException

from app.auth import get_current_user
from app.models import Tenant, TenantMember


async def get_current_tenant(
    tenant_slug: str = Header(alias="X-Tenant-Slug", default=""),
) -> Tenant:
    """Extract and validate the active tenant from the X-Tenant-Slug header."""
    if not tenant_slug:
        raise HTTPException(400, "Header 'X-Tenant-Slug' is required for tenant context.")

    tenant = await Tenant.objects.filter(slug=tenant_slug).afirst()
    if not tenant:
        raise HTTPException(404, f"Tenant '{tenant_slug}' not found.")

    return tenant


class RequireTenantMember:
    """Guard ensuring the authenticated user is a member of the active tenant scope."""

    async def __call__(self, request: Request) -> TenantMember:
        current_user = await get_current_user(request)
        user_id = int(current_user["sub"])

        tenant_slug = request.headers.get("X-Tenant-Slug", "")
        if not tenant_slug:
            raise HTTPException(400, "Header 'X-Tenant-Slug' is required.")

        membership = (
            await TenantMember.objects.filter(tenant__slug=tenant_slug, user_id=user_id)
            .select_related("tenant", "user")
            .afirst()
        )

        if not membership:
            raise HTTPException(403, f"Access denied to tenant '{tenant_slug}'.")

        return membership
