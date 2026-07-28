import pytest
from django_bolt.testing import TestClient

from app.api import api
from app.native import aparallel_sum_floats, aparallel_transform_strings


@pytest.mark.django_db
def test_rust_status_endpoint():
    client = TestClient(api)
    response = client.get("/api/rust/status")
    assert response.status_code == 200
    data = response.json()
    assert "available" in data
    assert "engine" in data


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_native_rust_helpers_direct():
    # Test string transformation (works with Rust or Python fallback)
    inputs = ["  hello ", "world  ", "django-lightning"]
    results = await aparallel_transform_strings(inputs)
    assert results == ["HELLO", "WORLD", "DJANGO-LIGHTNING"]

    # Test float sum helper
    total = await aparallel_sum_floats([10.0, 20.0, 30.0, 40.0])
    assert total == 100.0


@pytest.mark.django_db
def test_rust_api_endpoints():
    client = TestClient(api)

    # Test transform strings API endpoint
    res_transform = client.post("/api/rust/transform-strings", json={"items": [" foo ", "bar "]})
    assert res_transform.status_code == 200
    data_transform = res_transform.json()
    assert data_transform["results"] == ["FOO", "BAR"]

    # Test compute metrics API endpoint
    res_metrics = client.post(
        "/api/rust/compute-metrics", json={"values": [1.0, 2.0, 3.0, 4.0, 5.0]}
    )
    assert res_metrics.status_code == 200
    data_metrics = res_metrics.json()
    assert data_metrics["sum"] == 15.0
