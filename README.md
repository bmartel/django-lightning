# ⚡ django-lightning

> **High-Performance Agentic Starter Template for [Django-Bolt](https://github.com/dj-bolt/django-bolt)**

`django-lightning` is a production-ready, agentic starter project designed for rapidly building, testing, and deploying ultra-high performance APIs powered by **Django 5.x**, **Django-Bolt** (a Rust-powered API framework delivering ~60k+ RPS), **Native PyO3 Rust Extensions**, and **`uv`** exclusively.

Equipped with a **Custom User Model** ready out of the box, in-process **Native Rust Extension Interop (`rust_core`)**, a comprehensive set of AI agent skills in `.agents/`, and a master `AGENTS.md` file, this repository enables both human engineers and AI coding assistants to build secure, performant, and scalable applications out of the box with Docker, docker-compose, Kubernetes, and Fly.io.

---

## 🔥 Key Features

- **⚡ Blazing Fast Rust API Engine**: Powered by `django-bolt` (`uv run manage.py runbolt`). No `uvicorn` or external server required!
- **🦀 Native PyO3 Rust Core Interop (`rust_core`)**: In-process Rust acceleration for low-level CPU computations, cryptography, media processing, or heavy data transformations with zero Python GIL overhead.
- **🛡 100% Type-Safe Async Native Functions (`@native_async` & `@native_json`)**: Pre-wrapped Rust functions offering 100% exact type hints, IDE autocomplete, and automatic background thread pool execution.
- **🚀 Ultra-Fast Zero-Copy & Msgspec JSON Bytes FFI**: Pass raw zero-copy byte buffers (`&[u8]`) or UTF-8 JSON byte payloads across C-FFI to bypass Python `PyObject` allocation overhead for **10x–50x speedups**.
- **🛠 Django Admin Ready Out-of-the-Box**: Native Django Admin interface at `/admin/` configured with `app.User` custom fields (`bio`, `avatar_url`). Run `uv run manage.py createsuperuser` to create your superuser.
- **👤 Custom User Model & Ready-to-Work Auth**: Includes a production-ready Custom `User` model (`AbstractUser`) configured via `AUTH_USER_MODEL = "app.User"` with JWT auth and profile management out of the box.
- **🚀 `uv` Exclusively**: Managed exclusively with `uv` for ultra-fast environment setup, package management, script execution, and testing.
- **🤖 Built-in MCP Server (`bolt-mcp`)**: Native Streamable HTTP Model Context Protocol server mounted at `/mcp` exposing tools, resources, and prompts to AI clients (Claude Desktop, MCP Inspector, etc.).
- **📦 Ultra-Fast Data Validation**: Uses `msgspec.Struct` (10-20x faster than Pydantic) and `django_bolt.serializers.Serializer`.
- **🔄 Async-First ORM**: Leverages Django's native async ORM (`aget`, `acreate`, `afilter`, `aupdate`, `adelete`).
- **🔀 Built-in Async Migrations**: Native background data backfill framework (`BaseAsyncMigration`, `python manage.py async_migrate`, and SAQ worker integration) for zero-downtime rolling deployments.
- **📊 High-Volume Batch Processing & PgBouncer Ready**: Zero-memory ballooning patterns (`.values()`, `aiterator()`, keyset pagination) and PgBouncer transaction pooling safety for processing millions of records.
- **📡 Realtime & Streaming**: Server-Sent Events (SSE) and chunked streaming endpoints.
- **📚 Interactive API Docs**: Built-in Scalar OpenAPI interface rendered at `/docs`.
- **🐳 Docker Compose & Multi-Stage Docker**: Containerized dev environment with sub-second Cargo build volume caching (`cargo_cache`, `cargo_target`) and multi-stage production builds.
- **☸ Enterprise Kubernetes**: Ready-to-apply K8s manifests in `k8s/` including Deployments, ClusterIP Service, Ingress, Secrets, ConfigMaps, and HPA.
- **🧠 13 Dedicated Agent Skills**: Comprehensive modular skills in `.agents/` guiding AI agents across every architectural domain.

---

## 🦀 Native PyO3 Rust Interop (`rust_core`)

When CPU-bound, low-level, or high-throughput tasks require speed beyond Python's Global Interpreter Lock (GIL), `django-lightning` provides an in-process **PyO3 + Maturin Native Extension Architecture** in `rust_core/`.

### 1. Writing Rust Functions with GIL Releasing
Always release Python's GIL (`py.allow_threads`) so Rayon multithreaded parallel loops run across all CPU cores without blocking `django-bolt`'s async event loop:

```rust
use pyo3::prelude::*;
use rayon::prelude::*;

#[pyfunction]
fn process_dataset_batch(py: Python<'_>, records: Vec<String>) -> PyResult<Vec<String>> {
    // Release Python GIL: Runs across all CPU cores in parallel
    let results = py.allow_threads(|| {
        records
            .into_par_iter()
            .map(|s| s.trim().to_uppercase())
            .collect()
    });

    Ok(results)
}
```

### 2. Type-Safe Python Wrappers (`app/native.py`)
Expose native functions in Python using `@native_async` or `@native_json` for 100% type safety and automatic non-blocking threadpool execution:

```python
from app.native import native_async, native_json
from app import rust_core

# Pre-wrapped 100% type-safe async native functions
process_batch = native_async(rust_core.process_batch)
process_payload = native_json(rust_core.process_payload, response_type=MyResponseStruct)
```

### 3. Invocation in API Routes & Worker Jobs
Call native functions directly with full IDE autocompletion and non-blocking async execution:

```python
@api.post("/api/v1/process-batch")
async def handle_process_batch(payload: BatchPayloadReq) -> BatchPayloadOut:
    # Direct, type-safe, non-blocking async execution!
    results = await process_batch(payload.records)
    return BatchPayloadOut(results=results)
```

### 4. Optional Rust Scaffolding (`--no-rust`)
Rust integration is completely optional. If a project does not require Rust, pass `--no-rust` when scaffolding:
```bash
create-django-bolt new my-app --no-rust
```
The resulting project is generated as a pure Python project stripped of `rust_core/`, `maturin`, and Cargo build steps.

---

## 🛠 Scaffolding a New Project

### Via Rust CLI (`create-django-bolt`)
Our dedicated Rust CLI tool **`create-django-bolt`** located in `cli/` compiles to a single standalone binary with zero runtime dependencies.

```bash
# Install standalone CLI binary (macOS / Linux)
curl -fsSL https://raw.githubusercontent.com/bmartel/django-lightning/main/scripts/install-cli.sh | sh

# Scaffold new project (with interactive prompt or --no-rust flag)
create-django-bolt new my-app
create-django-bolt new my-app --no-rust -p ~/code/my-app
```

### Via Python Generator Script
```bash
# Scaffold via just shortcut
just new-project my-app ~/code/my-app

# Or using uv directly
uv run python scripts/create-project.py my-app ~/code/my-app
```

---

## 🚀 Quick Start

### 1. Setup Virtual Environment with `uv`
```bash
# Clone the repository
git clone https://github.com/bmartel/django-lightning.git
cd django-lightning

# Create virtual environment & install dependencies
uv venv
uv pip install maturin
uv run maturin develop
uv pip install -e ".[dev]"
```

### 2. Run Database Migrations
```bash
uv run manage.py migrate
uv run manage.py collectstatic --noinput
```

### 3. Start the Django-Bolt Development Server
```bash
uv run manage.py runbolt --dev
```

Access the application:
- **API Base**: `http://localhost:8000`
- **Scalar OpenAPI Docs**: `http://localhost:8000/docs`
- **MCP Endpoint**: `http://localhost:8000/mcp`
- **Health Check**: `http://localhost:8000/health`

---

## 🔀 Async Migration Management & Zero-Downtime Rollouts

In high-availability production environments, long-running data backfills cause table locks or deployment timeouts when executed inside pod init containers or release hooks.

`django-lightning` decouples schema migrations (DDL) from data migrations (DML):

1. **Pre-rollout Schema DDL**: Executed synchronously before pod updates via `k8s/job-migration.yaml` or Fly `release_command`.
2. **Rolling Deployment**: Updates application pods without downtime (`maxUnavailable: 0`).
3. **Post-rollout Async DML**: Long-running data backfills run non-blockingly via `BaseAsyncMigration` and SAQ workers.

```bash
# List all registered async background data migrations
uv run manage.py async_migrate --list

# Run an async data migration in the foreground
uv run manage.py async_migrate --run 0001_example_backfill

# Enqueue an async data migration to the SAQ background worker process
uv run manage.py async_migrate --enqueue 0001_example_backfill
```

---

## ⚡ High-Performance Database Query Guidance

To ensure APIs operate at peak performance (~60k+ RPS), all developers and AI agents must follow mandatory query rules:

1. **N+1 Query Prevention**: Always use `select_related` for ForeignKeys & OneToOne relationships (1 SQL `JOIN`), and `prefetch_related` or `Prefetch()` for ManyToMany & reverse relationships (2 batched SQL queries with `IN (...)`).
2. **Prevent Field Overfetching**: Use `.only("field1", "field2")` or `.defer("heavy_blob")` for model queries, or `.values()` / `.values_list()` for primitive dictionary output. Never fetch unused `TEXT`, `JSONB`, or `BYTEA` columns.
3. **Proper Indexing**: Ensure all `filter()`, `order_by()`, and join fields are backed by single or composite B-Tree indexes (`db_index=True`, `models.Index`). Use GIN indexes for JSONB and `gin_trgm_ops` for wildcard searches (`icontains`).
4. **Keyset Pagination**: Use indexed ID filtering (`id > last_seen_id`) or `app.utils.akeyset_chunker` instead of SQL `OFFSET` on large datasets to avoid $O(N)$ query degradation.
5. **Subqueries over In-Memory Lists**: Use `Exists()` and `Subquery()` instead of loading arrays into Python memory and building massive `filter(id__in=[...])` queries.
6. **Strict < 100ms Response Latency Budget**: Enforces a strict **100ms** latency target across all endpoints via `LatencyBudgetMiddleware`. Response telemetry headers (`X-Response-Time-Ms`, `X-Latency-Budget-Passed`) track performance on every request.
7. **Surgical Small-Dataset Scalability Profiling**: Prevents small-dataset query planner illusions (where tiny test tables hide missing indexes). Use `app.profiling.assert_scalable_query(queryset)` in tests to force index-path evaluation (`SET LOCAL enable_seqscan = OFF;`) and catch unindexed table scans, unindexed sorts, and cartesian joins before code hits production.

---

## 🤖 Agentic Capabilities & Skills

This repository is optimized for autonomous AI agents (such as Antigravity, Claude Code, Cursor, etc.). Refer to **[`AGENTS.md`](file:///Users/brandonmartel/code/django-lightning/AGENTS.md)** for master guidelines.

### Available Agent Skills in `.agents/skills/`:
1. **[`django-bolt-core`](file:///.agents/skills/django-bolt-core/SKILL.md)**: `BoltAPI` configuration, routes, parameter extraction (`Query`, `Path`, `Header`, `Cookie`, `Form`, `File`, `Body`, `Depends`), response types.
2. **[`django-bolt-schemas-serializers`](file:///.agents/skills/django-bolt-schemas-serializers/SKILL.md)**: `msgspec.Struct`, `Serializer` validation, field & model validators.
3. **[`django-bolt-auth-security`](file:///.agents/skills/django-bolt-auth-security/SKILL.md)**: Custom User Model, JWT authentication, permission guards (`@guard`), CORS, rate limiting.
4. **[`django-bolt-async-orm-db`](file:///.agents/skills/django-bolt-async-orm-db/SKILL.md)**: Async Django ORM (`aget`, `acreate`, `afilter`), PostgreSQL connection pooling.
5. **[`django-bolt-rust-interop`](file:///.agents/skills/django-bolt-rust-interop/SKILL.md)**: PyO3 Rust extension development, GIL releasing (`py.allow_threads`), Rayon multithreading, zero-copy byte buffers, and msgspec JSON FFI.
6. **[`django-bolt-realtime-mcp`](file:///.agents/skills/django-bolt-realtime-mcp/SKILL.md)**: SSE streaming, WebSockets, and `bolt-mcp` MCP Server implementation.
7. **[`django-bolt-background-workers`](file:///.agents/skills/django-bolt-background-workers/SKILL.md)**: Ultra-high-throughput async queue worker engine (`SAQ` + Redis) with 10,000+ jobs/sec and ~30MB RAM footprint.
8. **[`django-bolt-testing-observability`](file:///.agents/skills/django-bolt-testing-observability/SKILL.md)**: In-memory `TestClient` tests, `pytest-asyncio`, OpenAPI docs, logging/timing middleware.
9. **[`django-bolt-docker`](file:///.agents/skills/django-bolt-docker/SKILL.md)**: Production `Dockerfile`, `.dockerignore`, and `docker-compose.yml`.
10. **[`django-bolt-kubernetes`](file:///.agents/skills/django-bolt-kubernetes/SKILL.md)**: Production Kubernetes manifests in `k8s/` (Deployment, Service, Ingress, HPA).
11. **[`django-bolt-fly-io`](file:///.agents/skills/django-bolt-fly-io/SKILL.md)**: Fly.io deployment config `fly.toml` & Fly Postgres integration.
12. **[`django-bolt-migration`](file:///.agents/skills/django-bolt-migration/SKILL.md)**: Migration guides from FastAPI, DRF, and Django Ninja to Django-Bolt.
13. **[`agentic-task-orchestration`](file:///.agents/skills/agentic-task-orchestration/SKILL.md)**: Autonomous worktree creation, task implementation, CI pipeline monitoring, automated PR creation, review, and safe backlog merging.

---

## 🧪 Testing & Code Quality

Run tests with `uv`:
```bash
uv run pytest -v
```

Run code formatting and linting:
```bash
uv run ruff check .
uv run ruff format .
```

Or using `just` shortcuts:
```bash
just test
just lint
just format
just rust-dev
just rust-build
just rust-test
```

---

## 🐳 Docker & Local Orchestration

Start local multi-container development environment (PostgreSQL + Redis + Django-Bolt):
```bash
docker compose up --build
```

---

## ☸ Deploying to Kubernetes

Apply all Kubernetes manifests:
```bash
kubectl apply -f k8s/
```

---

## 🚀 Deploying to Fly.io

Deploy with a single command:
```bash
fly deploy
```

---

## 📜 License

MIT License. Free for open source and commercial use.
