from django_bolt.exceptions import HTTPException

from app.auth import get_current_user


class IsAuthenticated:
    """Guard ensuring the request comes from an authenticated user."""

    async def __call__(self, request):
        user = await get_current_user(request)
        if not user:
            raise HTTPException(401, "Authentication required")
        return True


class IsStaffUser:
    """Guard ensuring the user has staff/admin privileges."""

    async def __call__(self, request):
        user = await get_current_user(request)
        if not user.get("is_staff", False):
            raise HTTPException(403, "Admin privileges required")
        return True
