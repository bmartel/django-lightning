---
name: django-bolt-auth-security
description: Authentication backends (JWT, API keys, Session), permission guards, CORS, rate limiting, and security controls for django-bolt.
compatibility: Agentic coding assistants building web applications with django-bolt.
metadata:
  category: security
  tags: [django-bolt, auth, jwt, api-key, guards, permissions, security]
---

# Django-Bolt Auth & Security

## JWT Authentication Implementation

```python
import jwt, time
from django.conf import settings
from django_bolt.exceptions import HTTPException


def create_jwt(user_id: int, username: str) -> str:
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": int(time.time()) + 3600,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


async def get_current_user(request) -> dict:
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(401, "Bearer authentication required")
    token = auth_header.split(" ", 1)[1]
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid or expired token")
```

## Permission Guards

```python
from django_bolt import BoltAPI, Depends


class RequireStaff:
    async def __call__(self, request):
        user = await get_current_user(request)
        if not user.get("is_staff"):
            raise HTTPException(403, "Staff access required")
        return True


api = BoltAPI()


@api.get("/admin/metrics", guards=[RequireStaff()])
async def admin_metrics():
    return {"status": "ok", "metrics": {}}
```
