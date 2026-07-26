---
name: django-bolt-realtime-mcp
description: Realtime streaming endpoints, Server-Sent Events (SSE), WebSockets, and bolt-mcp (Model Context Protocol) server integration.
compatibility: Agentic coding assistants building web applications with django-bolt.
metadata:
  category: realtime
  tags: [django-bolt, websocket, sse, streaming, mcp, model-context-protocol, bolt-mcp]
---

# Django-Bolt Realtime & MCP Integration

## Server-Sent Events (SSE)

```python
import asyncio, json, time
from django_bolt import BoltAPI, StreamingResponse

api = BoltAPI()


@api.get("/events")
async def sse():
    async def generator():
        for i in range(100):
            await asyncio.sleep(1)
            payload = json.dumps({"step": i, "timestamp": time.time()})
            yield f"data: {payload}\n\n"

    return StreamingResponse(generator(), media_type="text/event-stream")
```

## Model Context Protocol (bolt-mcp)

`bolt-mcp` allows exposing tools, resources, and prompts over Streamable HTTP transport at `/mcp` directly driven by `django-bolt`'s engine without Starlette or extra dependencies.

```python
from django_bolt import BoltAPI
from bolt_mcp import MCP
from app.models import Item

api = BoltAPI()
mcp = MCP("my-mcp-server", "1.0.0")


@mcp.tool(name="count_items", description="Count active items using Django async ORM")
async def count_items() -> dict:
    count = await Item.objects.filter(is_active=True).acount()
    return {"count": count}


@mcp.resource("config://app", mime_type="application/json")
async def app_config() -> str:
    return '{"env": "production"}'


@mcp.prompt
async def summarize(topic: str) -> str:
    return f"Write a summary about: {topic}"


api.mount_mcp(mcp)  # Mounts Streamable HTTP MCP server at /mcp
```
