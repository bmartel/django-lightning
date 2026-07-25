---
name: django-bolt-migration
description: Comprehensive playbook for migrating existing web APIs from FastAPI, Django REST Framework (DRF), and Django Ninja to django-bolt for massive performance gains (~60k+ RPS).
compatibility: Agentic coding assistants building web applications with django-bolt.
metadata:
  category: migration
  tags: [migration, fastapi, drf, django-ninja, django-bolt, conversion-playbook]
---

# Complete Migration Playbook to Django-Bolt

This guide provides an exhaustive mapping of concepts, components, data models, authentication guards, dependencies, background tasks, and streaming endpoints from **FastAPI**, **Django REST Framework (DRF)**, and **Django Ninja** to **`django-bolt`**.

---

## Key Mental Shifts When Migrating to Django-Bolt

1. **Sole Server Engine (`runbolt`)**:
   - **Never run `uvicorn`, `gunicorn`, `daphne`, or `hypercorn`.**
   - Development: `uv run manage.py runbolt --dev`
   - Production: `uv run manage.py runbolt --host 0.0.0.0 --port 8000 --processes 4`

2. **Ultra-Fast Data Schemas (`msgspec.Struct`)**:
   - Replace `pydantic.BaseModel` and `drf.serializers.Serializer` with `msgspec.Struct` for request/response payloads (10-20x faster).
   - Use `django_bolt.serializers.Serializer` for rich field validation (`@field_validator`) and cross-field checks (`@model_validator`).

3. **Async-First Database Access**:
   - Replace sync ORM calls with native Django async ORM (`afirst()`, `acreate()`, `aupdate()`, `adelete()`, `acount()`, `aexists()`, `async for`).

---

## Part 1: Migrating from FastAPI

### 1. Concept Equivalence Table

| FastAPI Concept | Django-Bolt Equivalent | Description / Note |
| --- | --- | --- |
| `app = FastAPI()` | `api = BoltAPI()` | Native Rust-powered router initialization |
| `@app.get(...)` | `@api.get(...)` | Same decorator syntax & HTTP verbs |
| `pydantic.BaseModel` | `msgspec.Struct` | `msgspec` is up to 10-20x faster than Pydantic |
| `uvicorn main:app` | `uv run manage.py runbolt` | Built-in Rust application server |
| `Query`, `Path`, `Header`, `Cookie`, `Form`, `File`, `Body` | `django_bolt.param_functions.*` | Identical parameter annotation syntax |
| `Depends(...)` | `Depends(...)` | Native dependency injection & generator support |
| `HTTPException` | `django_bolt.exceptions.HTTPException` | Built-in HTTP exception handling |
| `JSONResponse` | `django_bolt.JSON` / `Response` | Automatic dict serialization or explicit response |
| `StreamingResponse` | `django_bolt.StreamingResponse` | Chunked streaming & SSE streams |
| `@app.on_event("startup")` | `@api.on_event("startup")` | Lifecycle event hooks |
| `/docs` (Swagger / ReDoc) | `/docs` (Scalar UI) | Configured via `OpenAPIConfig(render_plugins=[ScalarRenderPlugin()])` |

---

### 2. Parameter Extraction Comparison

#### FastAPI
```python
from fastapi import FastAPI, Query, Path, Header, Depends, UploadFile, File

app = FastAPI()


@app.get("/items/{item_id}")
async def get_item(
    item_id: int = Path(..., ge=1),
    q: str | None = Query(None, min_length=2),
    x_token: str = Header(...),
):
    return {"item_id": item_id, "q": q, "x_token": x_token}
```

#### Django-Bolt
```python
from typing import Annotated
from django_bolt import BoltAPI, UploadFile
from django_bolt.param_functions import Query, Path, Header, File

api = BoltAPI()

@api.get("/items/{item_id}")
async def get_item(
    item_id: Annotated[int, Path(ge=1)],
    q: Annotated[str | None, Query(min_length=2)] = None,
    x_token: Annotated[str, Header(alias="x-token")],
):
    return {"item_id": item_id, "q": q, "x_token": x_token}
```

---

### 3. Data Models & Validation (Pydantic -> `msgspec.Struct` / `Serializer`)

#### FastAPI (Pydantic)
```python
from pydantic import BaseModel, Field, field_validator


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3)
    email: str

    @field_validator("email")
    def validate_email(cls, v):
        if "@" not in v:
            raise ValueError("Invalid email")
        return v.lower()
```

#### Django-Bolt (`msgspec.Struct` or `Serializer`)

**Option A: High-Performance DTO (`msgspec.Struct`)**
```python
import msgspec
from typing import Annotated


class UserCreateDTO(msgspec.Struct):
    username: Annotated[str, msgspec.Meta(min_length=3)]
    email: str
```

**Option B: Custom Validator (`django_bolt.serializers.Serializer`)**
```python
from typing import Annotated
import msgspec
from django_bolt.serializers import Serializer, field_validator


class UserCreateSerializer(Serializer):
    username: Annotated[str, msgspec.Meta(min_length=3)]
    email: str

    @classmethod
    @field_validator("email")
    def validate_email(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("Invalid email address format")
        return value.lower().strip()
```

---

### 4. Dependency Injection & Context Managers

#### FastAPI
```python
async def get_db():
    db = await connect_database()
    try:
        yield db
    finally:
        await db.close()


@app.get("/users")
async def list_users(db=Depends(get_db)):
    return await db.fetch_all()
```

#### Django-Bolt
```python
from django_bolt import BoltAPI, Depends

api = BoltAPI()


async def get_db():
    db = await connect_database()
    try:
        yield db
    finally:
        await db.close()


@api.get("/users")
async def list_users(db=Depends(get_db)):
    return await db.fetch_all()
```

---

## Part 2: Migrating from Django REST Framework (DRF)

### 1. Concept Equivalence Table

| DRF Concept | Django-Bolt Equivalent | Migration Action |
| --- | --- | --- |
| `APIView` / `@api_view(['GET'])` | `@api.get(...)` | Replace view functions/classes with Bolt route decorators |
| `serializers.Serializer` / `ModelSerializer` | `msgspec.Struct` / `Serializer` | Convert DRF fields to typed Python hints & `msgspec` structs |
| `request.data` / `request.query_params` | Typed function parameters | Declare typed parameters (`data: UserCreate`, `page: int = 1`) |
| Sync ORM (`Item.objects.filter(...)`) | Async ORM (`await Item.objects.filter(...).afirst()`) | Replace sync ORM calls with async ORM prefixed methods |
| `permission_classes = [IsAuthenticated]` | `guards=[IsAuthenticated()]` | Use `@guard` decorators or `guards=[...]` parameter |
| `authentication_classes = [JWTAuthentication]` | `auth=[JWTAuthentication()]` | Attach auth backends or use `Depends(get_current_user)` |
| `APIException` / `ValidationError` | `HTTPException(status_code, detail)` | Raise `django_bolt.exceptions.HTTPException` |
| `APIClient` | `django_bolt.testing.TestClient` | In-memory test client (no network sockets needed) |

---

### 2. Complete DRF -> Django-Bolt Endpoint Conversion

#### DRF Implementation
```python
# DRF Views & Serializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from .models import Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "name", "price"]


class ItemListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Item.objects.filter(is_active=True)
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save(created_by=request.user)
        return Response(ItemSerializer(item).data, status=201)
```

#### Django-Bolt Equivalent
```python
import msgspec
from django_bolt import BoltAPI, Depends
from django_bolt.exceptions import HTTPException
from app.models import Item
from app.auth import get_current_user
from app.guards import IsAuthenticated

api = BoltAPI()


class ItemIn(msgspec.Struct):
    name: str
    price: float


class ItemOut(msgspec.Struct):
    id: int
    name: str
    price: float


@api.get("/items", response_model=list[ItemOut], guards=[IsAuthenticated()])
async def list_items():
    items = []
    async for item in Item.objects.filter(is_active=True):
        items.append({"id": item.id, "name": item.name, "price": float(item.price)})
    return items


@api.post("/items", response_model=ItemOut, status_code=201, guards=[IsAuthenticated()])
async def create_item(payload: ItemIn, current_user: dict = Depends(get_current_user)):
    item = await Item.objects.acreate(
        name=payload.name,
        price=payload.price,
        created_by_id=int(current_user["sub"]),
    )
    return {"id": item.id, "name": item.name, "price": float(item.price)}
```

---

## Part 3: Migrating from Django Ninja

### 1. Concept Equivalence Table

| Django Ninja Concept | Django-Bolt Equivalent | Key Difference |
| --- | --- | --- |
| `api = NinjaAPI()` | `api = BoltAPI()` | Bolt uses native Rust router (~60k+ RPS) |
| `ninja.Schema` | `msgspec.Struct` | `msgspec` is drastically faster and lower memory |
| `router = Router()` | `sub_api = BoltAPI()` | Bolt supports sub-API composition with `api.mount()` |
| `HttpBearer` | `Depends(get_current_user)` / `@guard` | Native dependency injection & custom guards |
| `sync_to_async` wrappers | Native Django Async ORM | Bolt runs natively async, eliminating `sync_to_async` overhead |
| `UploadedFile` | `UploadFile` | Async streaming file upload support |

---

### 2. Django Ninja -> Django-Bolt Conversion Example

#### Django Ninja
```python
from ninja import NinjaAPI, Schema, File, UploadedFile
from ninja.security import HttpBearer

api = NinjaAPI()


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        if token == "secret":
            return token


class PayloadSchema(Schema):
    title: str


@api.post("/upload", auth=AuthBearer())
def upload(request, payload: PayloadSchema, file: UploadedFile = File(...)):
    return {"title": payload.title, "filename": file.name}
```

#### Django-Bolt Equivalent
```python
from typing import Annotated
import msgspec
from django_bolt import BoltAPI, Depends, UploadFile
from django_bolt.param_functions import File
from app.auth import get_current_user

api = BoltAPI()


class PayloadStruct(msgspec.Struct):
    title: str


@api.post("/upload")
async def upload(
    payload: PayloadStruct,
    file: Annotated[UploadFile, File()],
    user: dict = Depends(get_current_user),
):
    content = await file.read()
    return {"title": payload.title, "filename": file.filename, "size": len(content)}
```

---

## Part 4: Step-by-Step Conversion Strategy

When converting an existing application to `django-lightning` (Django-Bolt):

1. **Initialize Project with `uv`**:
   Ensure `pyproject.toml` includes `django-bolt` and `bolt-mcp`.
2. **Setup Custom User Model**:
   Configure `AUTH_USER_MODEL = "app.User"` in `config/settings.py`.
3. **Convert Schemas**:
   Replace `Pydantic` or `DRF Serializers` with `msgspec.Struct` and `django_bolt.serializers.Serializer`.
4. **Convert Route Handlers**:
   Annotate handler inputs explicitly with `Query`, `Path`, `Header`, `Form`, `File`, `Body`, or `Depends`.
5. **Convert Database Access**:
   Replace blocking ORM calls with `afirst()`, `acreate()`, `aupdate()`, `adelete()`, `acount()`, `aexists()`, and `async for`.
6. **Replace Server Command**:
   Run with `uv run manage.py runbolt --dev` locally and `uv run manage.py runbolt --host 0.0.0.0 --port 8000 --processes 4` in production containers.
7. **Run Verification**:
   Execute `uv run manage.py check`, `uv run ruff check .`, and `uv run pytest -v`.
