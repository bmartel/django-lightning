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

### 4. Async First Handlers, Query Performance & Database Access
- **Always write async handlers** (`async def`).
- **Always use async ORM methods**:
  - `await Model.objects.filter(...).afirst()`
  - `await Model.objects.acreate(...)`
  - `await Model.objects.filter(...).acount()`
  - `await Model.objects.filter(...).aexists()`
  - `await Model.objects.filter(...).aupdate(...)`
  - `await instance.adelete()`
- **High-Performance Query Rules & Anti-Pattern Prevention**:
  - **N+1 Query Prevention**: Mandatory use of `select_related` (for ForeignKeys & OneToOneFields) and `prefetch_related` or `Prefetch()` (for ManyToManyFields & reverse ForeignKeys) before accessing related model attributes in loops or serializing response payloads.
  - **Prevent Overfetching Fields**: Never fetch unused columns (especially large `TEXT`, `JSONB`, or `BYTEA` fields). Use `.only(...)` / `.defer(...)` when returning model instances, or `.values(...)` / `.values_list(...)` when returning raw dictionaries or tuples to reduce memory footprint and database network payload size.
  - **Database Indexing Requirements**: Enforce proper indexes (`db_index=True`, `models.Index`, composite indexes for multi-column conditions, or `GinIndex` for JSONB/array fields) on all query filter columns, join keys, and `order_by` fields. Avoid unindexed case-insensitive wildcard searches (`icontains`) on large tables.
  - **Join & Subquery Optimization**: Avoid multi-table cartesian products and redundant joins. Use selective filtering, `Exists()`, `Subquery()`, or `Prefetch(..., queryset=...)` with filtered child querysets instead of loading raw lists in Python memory.
  - **Strict < 100ms Response Latency Budget**: All API endpoints MUST respond under **100ms** total latency regardless of table sizes or feature complexity. Use `LatencyBudgetMiddleware` to track and enforce request processing times. Exceeding 100ms triggers performance warnings and blocks scalability verification.
  - **Surgical Query Profiling & Small-Dataset Index Guard**: Never rely on standard EXPLAIN against small test tables (where DB optimizers falsely hide missing indexes via temporary Seq Scans). Use `app.profiling.assert_scalable_query(queryset)` in tests to force index-path evaluation (`SET LOCAL enable_seqscan = OFF;`) and automatically fail tests on unindexed table scans, unindexed sorts, or cartesian joins.
  - **Keyset Pagination over OFFSET**: Always use keyset pagination (`id > last_seen_id`) or `app.utils.akeyset_chunker` instead of SQL `OFFSET` on large datasets to avoid $O(N)$ query degradation.
- **High-Volume Data Processing (1M+ Records)**:
  - **Memory Optimization**: Use `.values()` / `.values_list()` to bypass Model instance creation, reducing RAM usage by 80%+. Use `aiterator(chunk_size=...)` for streaming.
  - **Keyset Pagination**: Use `app.utils.akeyset_chunker` or indexed ID chunking (`id > last_id`) instead of SQL `OFFSET` to prevent $O(N)$ query degradation.
  - **PgBouncer Safety**: In PgBouncer Transaction Mode (`pool_mode = transaction`), use keyset pagination or wrap `aiterator()` in `async with transaction.aatomic():` so server-side cursors do not fail with `cursor does not exist`.
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

## 🛠 AVAILABLE AGENT SKILLS INDEX (`.agents/skills/`)

When completing specific subtasks, consult and adhere to the relevant skill file:

- **[django-bolt-core](file:///.agents/skills/django-bolt-core/SKILL.md)**: `BoltAPI` initialization, routing, HTTP verbs, parameter extraction, and response formatting.
- **[django-bolt-schemas-serializers](file:///.agents/skills/django-bolt-schemas-serializers/SKILL.md)**: `msgspec.Struct`, `Serializer` validation, field & model validators.
- **[django-bolt-auth-security](file:///.agents/skills/django-bolt-auth-security/SKILL.md)**: Custom User Model, JWT authentication, permission guards (`@guard`), CORS, rate limiting, and security headers.
- **[django-bolt-async-orm-db](file:///.agents/skills/django-bolt-async-orm-db/SKILL.md)**: Async Django ORM, query optimization (`select_related`), connection pooling, and migrations.
- **[django-bolt-realtime-mcp](file:///.agents/skills/django-bolt-realtime-mcp/SKILL.md)**: SSE, WebSockets, streaming responses, and `bolt-mcp` (Streamable HTTP MCP server).
- **[django-bolt-background-workers](file:///.agents/skills/django-bolt-background-workers/SKILL.md)**: Ultra-high-throughput async queue worker engine (`SAQ` + Redis) with 10,000+ jobs/sec and ~30MB RAM footprint.
- **[django-bolt-testing-observability](file:///.agents/skills/django-bolt-testing-observability/SKILL.md)**: `TestClient` unit tests, `pytest-asyncio`, Scalar OpenAPI docs at `/docs`, timing & logging middleware.
- **[django-bolt-docker](file:///.agents/skills/django-bolt-docker/SKILL.md)**: Multi-stage Docker builds using `uv`, `.dockerignore`, and local multi-service orchestration via `docker-compose.yml`.
- **[django-bolt-kubernetes](file:///.agents/skills/django-bolt-kubernetes/SKILL.md)**: Production Kubernetes manifests in `k8s/` (`deployment.yaml`, `service.yaml`, `ingress.yaml`, `configmap.yaml`, `secret.yaml`, `hpa.yaml`).
- **[django-bolt-fly-io](file:///.agents/skills/django-bolt-fly-io/SKILL.md)**: `fly.toml` configuration, Fly Postgres binding, environment secrets, and deployment.
- **[django-bolt-migration](file:///.agents/skills/django-bolt-migration/SKILL.md)**: Migration guides from FastAPI, DRF, and Django Ninja to `django-bolt`.
- **[django-bolt-rust-interop](file:///.agents/skills/django-bolt-rust-interop/SKILL.md)**: Native Rust core extension integration (`rust_core`), PyO3 bindings, GIL releasing (`py.allow_threads`), Rayon parallel processing, optional scaffolding, and packaging best practices.
- **[agentic-task-orchestration](file:///.agents/skills/agentic-task-orchestration/SKILL.md)**: Autonomous worktree creation, task implementation, CI pipeline monitoring, automated PR creation, review, and safe backlog merging.


---

## 💻 DEVELOPER WORKFLOW COMMANDS (UV EXCLUSIVELY)

This project uses `just` (or `uv`) for all tasks:

- **Build Rust CLI**: `just build-cli` (or `cargo build --manifest-path cli/Cargo.toml --release`)
- **Scaffold New Project (Rust CLI)**: `create-django-bolt new <name> [-p dest]`
- **Scaffold New Project (Script)**: `just new-project <name> [dest]` (or `uv run python scripts/create-project.py <name> [dest]`)
- **Start Local Server**: `just dev` (or `uv run manage.py runbolt --dev`)
- **Start All Local Services**: `just dev-all` (concurrently starts API dev server + SAQ worker)
- **Scaffold Resource Domain**: `uv run manage.py generate_resource <ModelName> --fields "..."`
- **Seed Synthetic Data**: `just seed count=100` (or `uv run manage.py seed_db --users 100`)
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
├── .agents/                             # Comprehensive Agent Skills & Tasks directory
│   ├── skills/                          # Modular agent skills
│   │   ├── django-bolt-core/SKILL.md
│   │   ├── django-bolt-schemas-serializers/SKILL.md
│   │   ├── django-bolt-auth-security/SKILL.md
│   │   ├── django-bolt-async-orm-db/SKILL.md
│   │   ├── django-bolt-realtime-mcp/SKILL.md
│   │   ├── django-bolt-background-workers/SKILL.md
│   │   ├── django-bolt-testing-observability/SKILL.md
│   │   ├── django-bolt-docker/SKILL.md
│   │   ├── django-bolt-kubernetes/SKILL.md
│   │   ├── django-bolt-fly-io/SKILL.md
│   │   └── django-bolt-migration/SKILL.md
│   └── tasks/                           # Project task tracking backlog
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
