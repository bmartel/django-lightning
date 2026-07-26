import pytest
from django_bolt.testing import TestClient

from app.api import api


@pytest.mark.django_db
def test_user_registration_login_and_profile_update():
    client = TestClient(api)

    # Register user with bio and avatar
    reg_resp = client.post(
        "/api/auth/register",
        json={
            "username": "alex",
            "email": "alex@example.com",
            "password": "password123",
            "bio": "Building fast APIs",
            "avatar_url": "https://example.com/avatar.png",
        },
    )
    assert reg_resp.status_code == 201
    user_data = reg_resp.json()
    assert user_data["username"] == "alex"
    assert user_data["bio"] == "Building fast APIs"

    # Login
    login_resp = client.post(
        "/api/auth/login",
        json={"username": "alex", "password": "password123"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get profile
    me_resp = client.get("/api/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "alex@example.com"

    # Update profile
    patch_resp = client.patch(
        "/api/auth/me",
        headers=headers,
        json={"bio": "Django-Bolt Enthusiast"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["bio"] == "Django-Bolt Enthusiast"
