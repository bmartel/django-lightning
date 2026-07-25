import json

import pytest
from django_bolt.testing import TestClient

from app.main import api


@pytest.mark.django_db
def test_mcp_initialize():
    client = TestClient(api)
    resp = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0"},
            },
        },
    )
    assert resp.status_code == 200
    text = resp.text
    # bolt-mcp returns responses via Streamable HTTP SSE format (data: {...})
    if "data: " in text:
        json_str = text.split("data: ", 1)[1].strip()
        data = json.loads(json_str)
    else:
        data = resp.json()
    assert "result" in data
    assert data["result"]["serverInfo"]["name"] == "django-lightning-mcp"
