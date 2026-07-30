import secrets
import time
from typing import Any

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django_bolt.exceptions import HTTPException

User = get_user_model()


def create_token(user) -> str:
    """Create a signed JWT access token for a user."""
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "is_staff": user.is_staff,
        "exp": int(time.time()) + 3600,  # 1 hour expiration
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid authorization token")


async def get_current_user(request) -> dict[str, Any]:
    """Dependency that extracts user payload from Authorization header or X-API-Key."""
    # Check for X-API-Key header first
    api_key_header = request.headers.get("X-API-Key", "") or request.headers.get("x-api-key", "")
    if api_key_header:
        from app.models import APIKey

        prefix = api_key_header[:12]
        matching_keys = [
            k
            async for k in APIKey.objects.filter(prefix=prefix, is_active=True).select_related(
                "user"
            )
        ]

        key_obj = None
        for k in matching_keys:
            if check_password(api_key_header, k.key_hash):
                key_obj = k
                break

        if not key_obj:
            raise HTTPException(401, "Invalid or inactive API key")

        return {
            "sub": str(key_obj.user.id),
            "username": key_obj.user.username,
            "is_staff": key_obj.user.is_staff,
            "auth_type": "api_key",
        }

    # Fallback to Bearer JWT token
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid Bearer authentication or X-API-Key header")

    token = auth_header.split(" ", 1)[1]
    payload = decode_token(token)
    payload["auth_type"] = "jwt"
    return payload


async def create_api_key(user, name: str = "Default Key"):
    """Generate and store a new secure API key for programmatic access."""
    from app.models import APIKey

    raw_secret = f"bolt_{secrets.token_urlsafe(32)}"
    prefix = raw_secret[:12]
    key_hash = make_password(raw_secret)

    key_obj = await APIKey.objects.acreate(
        user=user,
        name=name,
        prefix=prefix,
        key_hash=key_hash,
    )
    return key_obj, raw_secret


