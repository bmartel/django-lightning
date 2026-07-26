# AGENTS.md — Django-Bolt Agentic Project Guidance

Welcome agent. This repository is **django-lightning**, a high-performance starter project built on **Django 5.x** and **[django-bolt](https://github.com/dj-bolt/django-bolt)** (~60k+ RPS Rust-powered API framework).

---

## 🚨 MANDATORY ARCHITECTURAL RULES

### 1. Sole Server Engine (`runbolt`)
- **NEVER use uvicorn, gunicorn, daphne, or hypercorn.**
- **Django-Bolt uses its own native Rust-powered application server via `uv run manage.py runbolt`**.
- Development: `uv run manage.py runbolt --dev`
- Production (Docker / K8s / Fly.io): `uv run manage.py runbolt --host 0.0.0.0 --port 8000 --processes 4`

### 2. `uv` Used Exclusively for Python Environments & Tooling
- **Always use `uv` exclusively** for dependency management, virtualenv creation, running management tasks, linting, and testing:
  - Development server: `uv run manage.py runbolt --dev`
  - Migrations: `uv run manage.py makemigrations` & `uv run manage.py migrate`
  - Tests: `uv run pytest`
  - Code quality: `uv run ruff check .` and `uv run ruff format .`
  - Package installation: `uv add <package>` or `uv pip install -e ".[dev]"`

### 3. Custom User Model, Ready-to-Work Auth & Django Admin
- **Custom User Model**: This repository includes a Custom User model (`app.User` extending `AbstractUser`) configured via `AUTH_USER_MODEL = "app.User"`.
- **Django Admin**: Ready out of the box at `/admin/`. Registered via `app/admin.py`. Run `uv run manage.py createsuperuser` to create admin credentials.
- **Authentication**: JWT authentication utilities (`app.auth`), permission guards (`app.guards`), and profile endpoints (`/api/auth/register`, `/api/auth/login`, `/api/auth/me`) work out of the box.

### 4. Async First Handlers & Database Access
- **Always write async handlers** (`async def`).
- **Always use async ORM methods**:
  - `await Model.objects.filter(...).afirst()`
  - `await Model.objects.acreate(...)`
  - `await Model.objects.filter(...).acount()`
  - `await Model.objects.filter(...).aexists()`
  - `await Model.objects.filter(...).aupdate(...)`
  - `await instance.adelete()`
  - `async for obj in Model.objects.filter(...):`
- **Never invoke blocking sync ORM calls in async handlers**.

### 5. Data Validation & Schemas
- **Use `msgspec.Struct` for request/response payloads**: It is up to 10-20x faster than Pydantic.
- **Use `django_bolt.serializers.Serializer`** when you need custom field validators (`@field_validator`) or model-level cross-field checks (`@model_validator`).
- **Use parameter annotations**: Annotate inputs with `Query`, `Path`, `Header`, `Cookie`, `Form`, `File`, `Body`, or `Depends` from `django_bolt.param_functions`.

### 6. Realtime & Model Context Protocol (MCP)
- **WebSockets & SSE**: Use `@api.get(...)` returning `StreamingResponse` for SSE, or `@api.websocket(...)` for WebSockets.
- **bolt-mcp**: MCP server tools, resources, and prompts are mounted at `/mcp` using `api.mount_mcp(mcp)` via the `bolt-mcp` package.

### 7. Zero-Downtime Rolling Deployments & Async Migration Management
- **Never run heavy data backfills in container init scripts or release locks**: Init containers block rolling updates and cause timeouts or table lockouts.
- **2-Phase Migration Paradigm**:
  1. **Pre-rollout Schema DDL**: Run `uv run manage.py migrate` via standalone jobs (`k8s/job-migration.yaml` or Fly `release_command`).
  2. **Post-rollout Async DML Data Backfill**: Use `uv run manage.py async_migrate` or SAQ background worker (`run_async_migration_task`) to run data backfills in non-blocking batches.
- **Async Migration Subsystem**: All background migrations inherit from `BaseAsyncMigration` in `app/async_migrations/` and track progress in `app.models.AsyncMigration`.


---

## 🛠 AVAILABLE AGENT SKILLS INDEX (`.agents/`)

When completing specific subtasks, consult and adhere to the relevant skill file:

- **[django-bolt-core](file:///.agents/django-bolt-core/SKILL.md)**: `BoltAPI` initialization, routing, HTTP verbs, parameter extraction, and response formatting.
- **[django-bolt-schemas-serializers](file:///.agents/django-bolt-schemas-serializers/SKILL.md)**: `msgspec.Struct`, `Serializer` validation, field & model validators.
- **[django-bolt-auth-security](file:///.agents/django-bolt-auth-security/SKILL.md)**: Custom User Model, JWT authentication, permission guards (`@guard`), CORS, rate limiting, and security headers.
- **[django-bolt-async-orm-db](file:///.agents/django-bolt-async-orm-db/SKILL.md)**: Async Django ORM, query optimization (`select_related`), connection pooling, and migrations.
- **[django-bolt-realtime-mcp](file:///.agents/django-bolt-realtime-mcp/SKILL.md)**: SSE, WebSockets, streaming responses, and `bolt-mcp` (Streamable HTTP MCP server).
- **[django-bolt-background-workers](file:///.agents/django-bolt-background-workers/SKILL.md)**: Ultra-high-throughput async queue worker engine (`SAQ` + Redis) with 10,000+ jobs/sec and ~30MB RAM footprint.
- **[django-bolt-testing-observability](file:///.agents/django-bolt-testing-observability/SKILL.md)**: `TestClient` unit tests, `pytest-asyncio`, Scalar OpenAPI docs at `/docs`, timing & logging middleware.
- **[django-bolt-docker](file:///.agents/django-bolt-docker/SKILL.md)**: Multi-stage Docker builds using `uv`, `.dockerignore`, and local multi-service orchestration via `docker-compose.yml`.
- **[django-bolt-kubernetes](file:///.agents/django-bolt-kubernetes/SKILL.md)**: Production Kubernetes manifests in `k8s/` (`deployment.yaml`, `service.yaml`, `ingress.yaml`, `configmap.yaml`, `secret.yaml`, `hpa.yaml`).
- **[django-bolt-fly-io](file:///.agents/django-bolt-fly-io/SKILL.md)**: `fly.toml` configuration, Fly Postgres binding, environment secrets, and deployment.
- **[django-bolt-migration](file:///.agents/django-bolt-migration/SKILL.md)**: Migration guides from FastAPI, DRF, and Django Ninja to `django-bolt`.

---

## 💻 DEVELOPER WORKFLOW COMMANDS (UV EXCLUSIVELY)

This project uses `just` (or `uv`) for all tasks:

- **Build Rust CLI**: `just build-cli` (or `cargo build --manifest-path cli/Cargo.toml --release`)
- **Scaffold New Project (Rust CLI)**: `create-django-bolt new <name> [-p dest]`
- **Scaffold New Project (Script)**: `just new-project <name> [dest]` (or `uv run python scripts/create-project.py <name> [dest]`)
- **Start Local Server**: `just dev` (or `uv run manage.py runbolt --dev`)
- **Start Background Worker**: `just worker` (or `uv run saq app.tasks.settings`)
- **Run Tests**: `just test` (or `uv run pytest -v`)
- **Run Linting**: `just lint` (or `uv run ruff check .`)
- **Format Code**: `just format` (or `uv run ruff format .`)
- **Database Migrations**: `just makemigrations` and `just migrate`
- **Docker Development**: `just docker-up` and `just docker-down`
- **Deploy to Fly.io**: `just deploy-fly`
- **Deploy to Kubernetes**: `just k8s-apply`

---

## 📁 PROJECT DIRECTORY STRUCTURE

```
django-lightning/
├── AGENTS.md                            # Master guidance for AI agents (this file)
├── README.md                            # Project overview & documentation
├── pyproject.toml                       # Dependencies managed by uv (django, django-bolt, bolt-mcp, msgspec, etc.)
├── manage.py                            # Django CLI configured for django-bolt (runbolt)
├── justfile                             # Command shortcuts executing uv
├── Dockerfile                           # Production multi-stage Docker build with uv
├── docker-compose.yml                   # Local dev environment (API, Postgres, Redis)
├── fly.toml                             # Fly.io deployment specification
│
├── cli/                                 # Ultra-fast Rust CLI tool (create-django-bolt)
│   ├── Cargo.toml
│   └── src/main.rs
│
├── .agents/                             # Comprehensive Agent Skills directory
│   ├── django-bolt-core/SKILL.md
│   ├── django-bolt-schemas-serializers/SKILL.md
│   ├── django-bolt-auth-security/SKILL.md
│   ├── django-bolt-async-orm-db/SKILL.md
│   ├── django-bolt-realtime-mcp/SKILL.md
│   ├── django-bolt-background-workers/SKILL.md
│   ├── django-bolt-testing-observability/SKILL.md
│   ├── django-bolt-docker/SKILL.md
│   ├── django-bolt-kubernetes/SKILL.md
│   ├── django-bolt-fly-io/SKILL.md
│   └── django-bolt-migration/SKILL.md
│
├── config/                              # Django settings & ASGI/WSGI entrypoints
│   ├── settings.py                      # Configured with AUTH_USER_MODEL = "app.User"
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── app/                                 # Main application code
│   ├── api.py                           # BoltAPI initialization & route mounting
│   ├── models.py                        # Custom User Model (AbstractUser) out of the box
│   ├── auth.py                          # JWT authentication utilities
│   ├── tasks.py                         # High-performance SAQ background tasks
│   ├── schemas/                         # msgspec Structs and Serializers
│   ├── guards/                          # Custom permission guards
│   ├── routes/                          # API endpoints (health, auth, realtime, mcp)
│   └── tests/                           # Async pytest suite (test_admin, test_auth, test_tasks, test_mcp)
│
├── k8s/                                 # Kubernetes manifests (Deployment, Service, Ingress, HPA)
└── .github/workflows/                   # CI/CD & release automation pipelines
```
