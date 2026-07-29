import pytest
from django.contrib.auth import get_user_model
from django_bolt import BoltAPI
from django_bolt.testing import TestClient

from app.auth import create_api_key
from app.routes.auth import register_auth_routes

User = get_user_model()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_api_key_authentication(db):
    api = BoltAPI()
    register_auth_routes(api)

    user = await User.objects.acreate(username="apikeyuser", email="key@example.com")
    user.set_password("Password123!")
    await user.asave()

    key_obj, raw_secret = await create_api_key(user, name="CLI Access Key")
    assert key_obj.prefix == raw_secret[:12]

    client = TestClient(api)

    # 1. Access protected route with X-API-Key
    resp = client.get("/api/auth/me", headers={"X-API-Key": raw_secret})
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "apikeyuser"

    # 2. Access with invalid API key
    resp_bad = client.get("/api/auth/me", headers={"X-API-Key": "invalid_key_123"})
    assert resp_bad.status_code == 401
