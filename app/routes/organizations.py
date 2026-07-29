from django.contrib.auth import get_user_model
from django_bolt import BoltAPI, Depends
from django_bolt.exceptions import HTTPException

from app.auth import get_current_user
from app.models import Organization, OrganizationMember
from app.schemas.organization import OrganizationCreate, OrganizationOut

User = get_user_model()


def register_organization_routes(api: BoltAPI):
    @api.post(
        "/api/organizations",
        response_model=OrganizationOut,
        status_code=201,
        tags=["Organizations"],
        summary="Create a new multi-tenant organization",
    )
    async def create_organization(
        payload: OrganizationCreate,
        current_user: dict = Depends(get_current_user),
    ):
        user_id = int(current_user["sub"])
        user = await User.objects.filter(id=user_id).afirst()
        if not user:
            raise HTTPException(404, "User not found")

        if await Organization.objects.filter(slug=payload.slug).aexists():
            raise HTTPException(400, "Organization slug already taken.")

        org = await Organization.objects.acreate(name=payload.name, slug=payload.slug)
        await OrganizationMember.objects.acreate(
            organization=org, user=user, role=OrganizationMember.ROLE_OWNER
        )

        return {"id": org.id, "name": org.name, "slug": org.slug, "role": "OWNER"}

    @api.get(
        "/api/organizations",
        response_model=list[OrganizationOut],
        tags=["Organizations"],
        summary="List user's organization memberships",
    )
    async def list_organizations(current_user: dict = Depends(get_current_user)):
        user_id = int(current_user["sub"])

        memberships = OrganizationMember.objects.filter(user_id=user_id).select_related(
            "organization"
        )
        results = []
        async for m in memberships:
            results.append(
                {
                    "id": m.organization.id,
                    "name": m.organization.name,
                    "slug": m.organization.slug,
                    "role": m.role,
                }
            )

        return results
