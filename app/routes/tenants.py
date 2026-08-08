from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django_bolt import BoltAPI, Depends
from django_bolt.exceptions import HTTPException

from app.auth import get_current_user
from app.models import Tenant, TenantMember
from app.schemas.tenant import TenantCreate, TenantOut

User = get_user_model()


def _create_tenant_with_owner(name: str, slug: str, user) -> Tenant:
    """Create a tenant and its owner membership atomically (both rows or neither)."""
    with transaction.atomic():
        tenant = Tenant.objects.create(name=name, slug=slug)
        TenantMember.objects.create(tenant=tenant, user=user, role=TenantMember.ROLE_OWNER)
    return tenant


def register_tenant_routes(api: BoltAPI):
    @api.post(
        "/api/tenants",
        response_model=TenantOut,
        status_code=201,
        tags=["Tenants"],
        summary="Create a new multi-tenant scope",
    )
    async def create_tenant(
        payload: TenantCreate,
        current_user: dict = Depends(get_current_user),
    ):
        user_id = int(current_user["sub"])
        user = await User.objects.filter(id=user_id).afirst()
        if not user:
            raise HTTPException(404, "User not found")

        # Create tenant + owner membership atomically. A concurrent request racing on the
        # same slug loses the unique constraint and gets a clean 400 (never an orphan tenant).
        try:
            tenant = await sync_to_async(_create_tenant_with_owner)(
                payload.name, payload.slug, user
            )
        except IntegrityError:
            raise HTTPException(400, "Tenant slug already taken.")

        return {"id": tenant.id, "name": tenant.name, "slug": tenant.slug, "role": "OWNER"}

    @api.get(
        "/api/tenants",
        response_model=list[TenantOut],
        tags=["Tenants"],
        summary="List user's tenant memberships",
    )
    async def list_tenants(current_user: dict = Depends(get_current_user)):
        user_id = int(current_user["sub"])

        memberships = TenantMember.objects.filter(user_id=user_id).select_related("tenant")
        results = []
        async for m in memberships:
            results.append(
                {
                    "id": m.tenant.id,
                    "name": m.tenant.name,
                    "slug": m.tenant.slug,
                    "role": m.role,
                }
            )

        return results
