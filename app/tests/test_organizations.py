import pytest
from django.contrib.auth import get_user_model
from django_bolt import BoltAPI
from django_bolt.testing import TestClient

from app.auth import create_token
from app.routes.organizations import register_organization_routes

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_organization_creation_and_listing(db):
    api = BoltAPI()
    register_organization_routes(api)

    user = User.objects.create_user(username="orgowner", password="password123")
    token = create_token(user)

    client = TestClient(api)
    headers = {"Authorization": f"Bearer {token}"}

    # Create Organization
    resp = client.post(
        "/api/organizations",
        json={"name": "Acme Corp", "slug": "acme-corp"},
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Acme Corp"
    assert data["slug"] == "acme-corp"
    assert data["role"] == "OWNER"

    # List Organizations
    resp_list = client.get("/api/organizations", headers=headers)
    assert resp_list.status_code == 200
    items = resp_list.json()
    assert len(items) == 1
    assert items[0]["slug"] == "acme-corp"
