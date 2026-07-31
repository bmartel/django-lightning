---
name: django-bolt-core
description: Core BoltAPI setup, route registration, HTTP methods, typed parameter extraction (Query, Path, Header, Cookie, Form, File, Body, Depends), responses, headers/cookies, and lifecycle hooks.
compatibility: Agentic coding assistants building web applications with django-bolt.
metadata:
  category: web-framework
  tags: [django, django-bolt, boltapi, routing, parameters, responses]
---

# Django-Bolt Core Routing & Parameter Extraction

## Critical Rules
- **Sole Server Engine**: Always execute and serve with `python manage.py runbolt --dev` (or `--processes N` for production). Do NOT use uvicorn or gunicorn under any circumstances.
- **Async First**: Declare handlers as `async def` unless synchronous blocking code is mandatory.
- **Explicit Parameter Annotations**: Annotate parameters with `Query`, `Path`, `Header`, `Cookie`, `Form`, `File`, `Body`, or `Depends` from `django_bolt.param_functions`.
- **Response Validation**: Use `response_model` on route decorators to validate and document output schemas with `msgspec.Struct`.
- **High-Performance Database Queries**: Route handlers executing database queries MUST prevent N+1 queries (`select_related`/`prefetch_related`) and prevent overfetching unused fields (`.only()`/`.values()`) before transforming models into response payloads.

## BoltAPI Constructor Options

```python
from django_bolt import (
    BoltAPI,
    CompressionConfig,
    LoggingMiddleware,
    OpenAPIConfig,
    ScalarRenderPlugin,
    TimingMiddleware,
)

api = BoltAPI(
    prefix="/api/v1",  # Global route prefix
    trailing_slash="strip",  # "strip", "append", or "keep"
    validate_response=True,  # Validate responses against response_model
    compression=CompressionConfig(),  # Gzip/Brotli response compression
    enable_logging=True,
    middleware=[
        TimingMiddleware,
        LoggingMiddleware,
    ],
    openapi_config=OpenAPIConfig(
        title="My High-Performance API",
        version="1.0.0",
        path="/docs",
        render_plugins=[ScalarRenderPlugin()],
        enabled=True,
    ),
)
```

## Route Handlers & Parameter Extraction

```python
from typing import Annotated
import msgspec
from django_bolt import BoltAPI, Depends, UploadFile, FileSize
from django_bolt.param_functions import Query, Path, Header, Cookie, Form, File, Body

api = BoltAPI()


# Query parameters with validation bounds
@api.get("/search")
async def search(
    q: Annotated[str, Query(min_length=1, max_length=100)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return {"query": q, "page": page, "limit": limit}


# Path parameters
@api.get("/users/{user_id}")
async def get_user(user_id: Annotated[int, Path(ge=1)]):
    return {"user_id": user_id}


# Headers and Cookies
@api.get("/client-info")
async def client_info(
    x_api_key: Annotated[str, Header(alias="X-Api-Key")],
    session_id: Annotated[str, Cookie()] = None,
):
    return {"key": x_api_key, "session": session_id}


# Multipart Form & File Upload
@api.post("/upload")
async def upload_file(
    title: Annotated[str, Form()],
    file: Annotated[
        UploadFile,
        File(max_size=FileSize.MB_30, allowed_types=["image/*", "application/pdf"]),
    ],
):
    content = await file.read()
    return {"filename": file.filename, "size": len(content)}
```

## Response Types

```python
from django_bolt import JSON, Response, StreamingResponse
from django_bolt.responses import PlainText, HTML, Redirect, FileResponse


# Dict / list auto-serializes to JSON
@api.get("/data")
async def get_data():
    return {"status": "ok"}


# Custom Status & Set Cookies
@api.post("/session")
async def create_session():
    return Response({"token": "xyz123"}, status_code=201).set_cookie(
        "session_id", "xyz123", httponly=True, secure=True
    )


# Redirects
@api.get("/old-url")
async def old_url():
    return Redirect("/new-url", status_code=301)


## Standard Django App Route Mounting

To integrate high-performance `django-bolt` async handlers with standard Django apps (`startapp`):

1. Define app route functions in `<app_name>/routes.py` (or `<app_name>/api.py`):
```python
from django_bolt import BoltAPI

def register_my_app_routes(api: BoltAPI):
    @api.get("/api/my-resource")
    async def list_items():
        return []
```
2. Mount the app routes in the project API entrypoint (`app/api.py`):
```python
from my_app.routes import register_my_app_routes

register_my_app_routes(api)
```
```
