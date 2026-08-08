from django.contrib.auth import get_user_model
from django_bolt.exceptions import HTTPException

from app.auth import get_current_user

User = get_user_model()


class IsAuthenticated:
    """Guard ensuring the request comes from an authenticated user."""

    async def __call__(self, request):
        user = await get_current_user(request)
        if not user:
            raise HTTPException(401, "Authentication required")
        return True


class IsStaffUser:
    """Guard ensuring the user currently has staff/admin privileges.

    The staff flag is re-checked against the database rather than trusted from the
    (up to 1 hour old) JWT claim, so a demoted or deactivated account loses access
    immediately instead of at token expiry.
    """

    async def __call__(self, request):
        payload = await get_current_user(request)
        user = await User.objects.filter(id=int(payload["sub"])).only(
            "id", "is_staff", "is_active"
        ).afirst()
        if not user or not user.is_active or not user.is_staff:
            raise HTTPException(403, "Admin privileges required")
        return True
