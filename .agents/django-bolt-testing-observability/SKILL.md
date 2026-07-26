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

api = BoltAPI(
    enable_logging=True,
    middleware=[TimingMiddleware, LoggingMiddleware],
    openapi_config=OpenAPIConfig(
        title="Production API",
        version="1.0.0",
        path="/docs",
        render_plugins=[ScalarRenderPlugin()],
    ),
)
```
