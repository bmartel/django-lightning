import time

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
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


def decode_token(token: str) -> dict:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid authorization token")


async def get_current_user(request) -> dict:
    """Dependency that extracts user payload from Authorization header."""
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid Bearer authentication header")

    token = auth_header.split(" ", 1)[1]
    payload = decode_token(token)
    return payload
