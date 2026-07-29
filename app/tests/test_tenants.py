import pytest
from django.contrib.auth import get_user_model
from django_bolt import BoltAPI
from django_bolt.testing import TestClient

from app.auth import create_token
from app.routes.tenants import register_tenant_routes

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_tenant_creation_and_listing(db):
    api = BoltAPI()
    register_tenant_routes(api)

    user = User.objects.create_user(username="tenantowner", password="password123")
    token = create_token(user)

    client = TestClient(api)
    headers = {"Authorization": f"Bearer {token}"}

    # Create Tenant
    resp = client.post(
        "/api/tenants",
        json={"name": "Acme Workspace", "slug": "acme-workspace"},
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Acme Workspace"
    assert data["slug"] == "acme-workspace"
    assert data["role"] == "OWNER"

    # List Tenants
    resp_list = client.get("/api/tenants", headers=headers)
    assert resp_list.status_code == 200
    items = resp_list.json()
    assert len(items) == 1
    assert items[0]["slug"] == "acme-workspace"
