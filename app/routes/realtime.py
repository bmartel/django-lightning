import asyncio
import json
import time

from django_bolt import BoltAPI, StreamingResponse


def register_realtime_routes(api: BoltAPI):
    @api.get(
        "/api/events/sse",
        tags=["Realtime"],
        summary="Server-Sent Events (SSE) stream",
    )
    async def sse_events():
        async def event_generator():
            for i in range(10):
                await asyncio.sleep(1)
                data = json.dumps(
                    {"event_id": i + 1, "timestamp": time.time(), "message": f"Tick {i + 1}"}
                )
                yield f"data: {data}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    @api.get(
        "/api/stream/text",
        tags=["Realtime"],
        summary="Chunked text stream response",
    )
    async def stream_text():
        async def text_chunks():
            words = ["Django-Bolt", "delivers", "ultra-low", "latency", "sub-5ms", "APIs!"]
            for word in words:
                await asyncio.sleep(0.3)
                yield f"{word} "

        return StreamingResponse(text_chunks(), media_type="text/plain")
