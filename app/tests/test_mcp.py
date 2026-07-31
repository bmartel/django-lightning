import json

import pytest
from django_bolt.testing import TestClient

from app.api import api


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


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_mcp_tools_direct_invocation():
    from django_bolt import BoltAPI

    from app.routes.mcp_server import setup_mcp_server

    test_api = BoltAPI()
    mcp = setup_mcp_server(test_api)

    def get_tool_fn(name: str):
        tool_obj = mcp._tools[name]
        return getattr(
            tool_obj, "fn", getattr(tool_obj, "func", getattr(tool_obj, "handler", None))
        )

    # Test count_users tool
    count_fn = get_tool_fn("count_users")
    res = await count_fn()
    assert "count" in res
    assert isinstance(res["count"], int)

    # Test inspect_db_schema tool
    schema_fn = get_tool_fn("inspect_db_schema")
    res = await schema_fn()
    assert "models" in res
    assert len(res["models"]) > 0

    # Test run_query_explain tool
    explain_fn = get_tool_fn("run_query_explain")
    res = await explain_fn("SELECT * FROM app_user WHERE email LIKE '%test%'")
    assert "is_scalable" in res
    assert "detected_issues" in res

    # Test get_async_migration_status tool
    migration_fn = get_tool_fn("get_async_migration_status")
    res = await migration_fn()
    assert "migrations" in res

    # Test get_latency_metrics tool
    metrics_fn = get_tool_fn("get_latency_metrics")
    res = await metrics_fn()
    assert "total_requests" in res
    assert "compliance_rate_pct" in res


def test_mcp_disabled_in_production(settings):
    from django_bolt import BoltAPI

    from app.routes.mcp_server import setup_mcp_server

    settings.ENABLE_MCP_SERVER = False
    test_api = BoltAPI()
    result = setup_mcp_server(test_api)
    assert result is None
