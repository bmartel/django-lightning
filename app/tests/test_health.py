import pytest
from django_bolt.testing import TestClient

from app.api import api


@pytest.mark.django_db
def test_health_check():
    client = TestClient(api)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ok", "degraded")
    assert data["database"] == "connected"
    assert "cache" in data
    assert "version" in data
