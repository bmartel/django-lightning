---
name: django-bolt-testing-observability
description: Testing django-bolt handlers with TestClient & pytest-asyncio, OpenAPI rendering with Scalar, timing/logging middleware, and metrics.
compatibility: Agentic coding assistants building web applications with django-bolt.
metadata:
  category: testing
  tags: [django-bolt, testing, pytest, testclient, openapi, scalar, logging]
---

# Django-Bolt Testing & Observability

## Testing with `TestClient` and `pytest`

Use `django_bolt.testing.TestClient` to execute lightweight, in-memory requests against `BoltAPI` instances without firing up network sockets.

```python
import pytest
from django_bolt.testing import TestClient
from app.api import api


@pytest.mark.django_db
def test_create_and_get_item():
    client = TestClient(api)

    # POST request
    resp = client.post("/api/items", json={"name": "Widget", "price": 10.0})
    assert resp.status_code == 201
    item_id = resp.json()["id"]

    # GET request
    get_resp = client.get(f"/api/items/{item_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Widget"
```

## Middleware & OpenAPI

```python
from django_bolt import (
    BoltAPI,
    TimingMiddleware,
    LoggingMiddleware,
    OpenAPIConfig,
    ScalarRenderPlugin,
)
from app.middleware import LatencyBudgetMiddleware

api = BoltAPI(
    enable_logging=True,
    middleware=[LatencyBudgetMiddleware, TimingMiddleware, LoggingMiddleware],
    openapi_config=OpenAPIConfig(
        title="Production API",
        version="1.0.0",
        path="/docs",
        render_plugins=[ScalarRenderPlugin()],
    ),
)
```

## Scalability Assertions & Latency Budget Testing

### 1. Asserting Query Scalability (`assert_scalable_query`)
Force PostgreSQL and database engines to evaluate index paths on small test tables (`enable_seqscan = OFF`) to prevent unindexed table scans or unindexed sorts from reaching production:

```python
import pytest
from app.models import User
from app.profiling import assert_scalable_query


@pytest.mark.django_db(transaction=True)
async def test_user_query_scalability():
    queryset = User.objects.filter(id=1)
    report = await assert_scalable_query(queryset)
    assert report.is_scalable is True
```

### 2. Verifying Response Latency Headers
Every request returns `X-Response-Time-Ms` and `X-Latency-Budget-Passed` (target **< 100ms**):

```python
def test_api_latency_budget():
    client = TestClient(api)
    response = client.get("/health")

    assert response.status_code == 200
    assert "X-Response-Time-Ms" in response.headers
    assert response.headers.get("X-Latency-Budget-Passed") == "true"
```

