"""Tenant awareness and organization guards for multi-tenant django-lightning apps."""

from django_bolt import Header, Request
from django_bolt.exceptions import HTTPException

from app.auth import get_current_user
from app.models import Organization, OrganizationMember


async def get_current_organization(
    org_slug: str = Header(alias="X-Organization-Slug", default=""),
) -> Organization:
    """Extract and validate the active organization from the X-Organization-Slug header."""
    if not org_slug:
        raise HTTPException(400, "Header 'X-Organization-Slug' is required for tenant context.")

    org = await Organization.objects.filter(slug=org_slug).afirst()
    if not org:
        raise HTTPException(404, f"Organization '{org_slug}' not found.")

    return org


class RequireOrganizationMember:
    """Guard ensuring the authenticated user is a member of the active organization."""

    async def __call__(self, request: Request) -> OrganizationMember:
        current_user = await get_current_user(request)
        user_id = int(current_user["sub"])

        org_slug = request.headers.get("X-Organization-Slug", "")
        if not org_slug:
            raise HTTPException(400, "Header 'X-Organization-Slug' is required.")

        membership = (
            await OrganizationMember.objects.filter(organization__slug=org_slug, user_id=user_id)
            .select_related("organization", "user")
            .afirst()
        )

        if not membership:
            raise HTTPException(403, f"Access denied to organization '{org_slug}'.")

        return membership
