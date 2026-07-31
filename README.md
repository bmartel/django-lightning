# django-lightning

> Production-grade, high-performance starter project built on **Django 5.x** and **[django-bolt](https://github.com/dj-bolt/django-bolt)**.

`django-lightning` combines **Django 5.x**, **Django-Bolt** (a Rust-powered Tokio application server), in-process **PyO3 Rust extension interop (`rust_core`)**, and an integrated **AI agent skill framework** in `.agents/`.

Equipped with a custom user model, ready-to-use JWT authentication, Django Admin integration, async background job queues, and Model Context Protocol (MCP) server endpoints out of the box, `django-lightning` provides a complete foundation for building ultra-low latency, scalable web APIs.

---

## Real-World Benchmarks & Performance Profile

Synthetic 1% microbenchmarks (such as bare zero-middleware echo endpoints claiming 60,000–188,000+ RPS) do not reflect actual application performance in production. `django-lightning` focuses on **reproducible, median real-world performance** across typical production workloads:

| Workload Type | Median Latency (p50) | p95 Latency | p99 Latency | Real-World Median RPS | Notes / Conditions |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **JSON & In-Memory APIs** | `~2.0 – 5.0 ms` | `< 12.0 ms` | `< 25.0 ms` | **15,000 – 35,000+ RPS** | `django-bolt` Tokio engine + `msgspec` binary JSON |
| **Async ORM DB Queries** | `~8.0 – 18.0 ms` | `< 35.0 ms` | `< 55.0 ms` | **3,000 – 8,000+ RPS** | PostgreSQL connection pool, async ORM, indexed filters |
| **Native PyO3 Rust Core** | `~1.5 – 3.5 ms` | `< 8.0 ms` | `< 15.0 ms` | **20,000 – 50,000+ RPS** | In-process GIL-releasing Rust extensions (`rust_core`) |
| *Synthetic Peak Limit* | *< 0.5 ms* | *< 2.0 ms* | *< 5.0 ms* | *~60,000 – 188,000 RPS* | *Raw zero-middleware echo benchmark upper bound* |

### Reproduce Benchmarks Locally

Run the included high-throughput asynchronous benchmark tool against your local server instance:

```bash
# 1. Start the Django-Bolt server
uv run manage.py runbolt --port 8000 --processes 4

# 2. Run the benchmark tool (10,000 requests across 50 concurrent connections)
uv run python scripts/benchmark.py --host 127.0.0.1 --port 8000 --path /health -n 10000 -c 50
```

---

## Key Capabilities

- **Rust-Powered Application Engine**: Driven directly by `django-bolt` (`uv run manage.py runbolt`). Eliminates the need for Uvicorn, Gunicorn, or Daphne.
- **Native PyO3 Rust Core (`rust_core`)**: In-process Rust compilation via PyO3 and Maturin. Release the Python GIL (`py.allow_threads`) to execute heavy CPU tasks, cryptography, or dataset processing across all hardware cores with Rayon parallelism.
- **Custom User Model & Out-of-the-Box Auth**: Configured with `AUTH_USER_MODEL = "app.User"`, custom profile fields (`bio`, `avatar_url`), JWT authentication utilities, permission guards (`@guard`), and Django Admin registered at `/admin/`.
- **Async-First Django 5.x ORM**: Full support for native async ORM methods (`aget`, `acreate`, `afilter`, `aupdate`, `adelete`). Strict latency enforcement (<100ms budget middleware) and surgical small-dataset index assertions (`assert_scalable_query`).
- **Built-in Agentic MCP Suite (`bolt-mcp`)**: Streamable HTTP Model Context Protocol server mounted at `/mcp` providing AI coding assistants with live schema introspection, SQL `EXPLAIN` execution, migration tracking, and latency metrics.
- **2-Phase Async Data Migrations**: Decouples schema changes (DDL) from long-running data backfills (DML) using `BaseAsyncMigration` and SAQ background job workers for zero-downtime rolling deployments.
- **High-Speed Serialization**: Powered by `msgspec.Struct` (10–20x faster than Pydantic) and custom `django_bolt` serializers.
- **Managed Exclusively with `uv`**: Ultra-fast environment setup, package locking, script execution, linting, formatting, and test runner execution via `uv`.
- **Resource CLI Scaffolding**: Generate models, serializers, async handlers, and tests in seconds using `uv run manage.py generate_resource <ModelName> --fields "..."`.
- **Standard Django App Conventions**: Create domain apps using standard `uv run manage.py startapp <app_name>`. All models (`models.py`), migrations (`migrations/`), admin classes (`admin.py`), and AppConfigs (`apps.py`) work natively out of the box.
- **Strictly Minimal Foundation**: Zero placeholder domain entities (no dummy `article` or `product` cruft). Only production-essential functional building blocks exist (Auth, Tenancy, Health, Realtime/MCP infra).
- **Containerization & Cloud Infrastructure**: Production multi-stage `Dockerfile`, multi-service `docker-compose.yml`, Kubernetes manifests (`k8s/`), and Fly.io deployment setup (`fly.toml`).

---

## PyO3 Rust Core Interop (`rust_core`)

When tasks require computational speed beyond Python's Global Interpreter Lock (GIL), `django-lightning` includes a PyO3 native extension in `rust_core/`.

### 1. Writing GIL-Releasing Rust Functions

Release Python's GIL (`py.allow_threads`) so Rayon parallel loops execute across all CPU cores without blocking the async event loop:

```rust
use pyo3::prelude::*;
use rayon::prelude::*;

#[pyfunction]
fn process_dataset_batch(py: Python<'_>, records: Vec<String>) -> PyResult<Vec<String>> {
    // Release Python GIL: runs across all CPU cores in parallel
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

Expose native functions in Python using `@native_async` or `@native_json` for type safety and automatic non-blocking threadpool execution:

```python
from app.native import native_async, native_json
from app import rust_core

process_batch = native_async(rust_core.process_batch)
process_payload = native_json(rust_core.process_payload, response_type=MyResponseStruct)
```

### 3. Invoking Native Code in API Routes

Call native functions directly inside async handlers with complete IDE autocomplete and non-blocking execution:

```python
@api.post("/api/v1/process-batch")
async def handle_process_batch(payload: BatchPayloadReq) -> BatchPayloadOut:
    results = await process_batch(payload.records)
    return BatchPayloadOut(results=results)
```

### 4. Optional Rust Scaffolding (`--no-rust`)

Rust integration is opt-in. If your application does not require Rust extensions, scaffold without Rust support:

```bash
create-django-bolt new my-app --no-rust
```

---

## Scaffolding a New Project

### Standalone Rust CLI (`create-django-bolt`)

The standalone Rust CLI in `cli/` compiles to a single binary with zero runtime dependencies:

```bash
# Install standalone CLI binary (macOS / Linux / Windows PowerShell)
curl -fsSL https://raw.githubusercontent.com/bmartel/django-lightning/main/scripts/install-cli.sh | sh

# Scaffold a new project
create-django-bolt new my-app
create-django-bolt new my-app --no-rust -p ~/code/my-app
```

### Python Generator Script

```bash
# Scaffold via just task runner
just new-project my-app ~/code/my-app

# Or directly using uv
uv run python scripts/create-project.py my-app ~/code/my-app
```

---

## Quick Start

### 1. Set Up Environment with `uv`

```bash
# Clone repository
git clone https://github.com/bmartel/django-lightning.git
cd django-lightning

# Initialize virtual environment and install dependencies
uv venv
uv pip install -e ".[dev]"
```

### 2. Run Database Migrations

```bash
uv run manage.py migrate
uv run manage.py collectstatic --noinput
```

### 3. Start the Development Server

```bash
uv run manage.py runbolt --dev
```

Default access endpoints:
- **API Base**: `http://localhost:8000`
- **Scalar OpenAPI Docs**: `http://localhost:8000/docs`
- **MCP Endpoint**: `http://localhost:8000/mcp`
- **Health Check**: `http://localhost:8000/health`

---

## High-Performance Database Query Guidance

To maintain low latency (<10ms median), enforce the following query practices:

1. **N+1 Query Prevention**: Use `select_related` for ForeignKeys/OneToOne relationships (1 SQL JOIN), and `prefetch_related` or `Prefetch()` for ManyToMany/reverse ForeignKeys.
2. **Prevent Field Overfetching**: Use `.only()` / `.defer()` for model instances, or `.values()` / `.values_list()` for dictionary outputs. Avoid fetching large unused `TEXT` or `JSONB` columns.
3. **Database Indexing**: Ensure all `filter()`, `order_by()`, and join columns have single or composite B-Tree indexes (`db_index=True`, `models.Index`). Use GIN indexes for JSONB fields.
4. **Keyset Pagination**: Use indexed ID filtering (`id > last_seen_id`) or `app.utils.akeyset_chunker` instead of SQL `OFFSET` on large tables.
5. **Latency Budget Enforcement**: `LatencyBudgetMiddleware` tracks request processing times and reports telemetry headers (`X-Response-Time-Ms`, `X-Latency-Budget-Passed`).
6. **Scalability Profiling in Tests**: Use `app.profiling.assert_scalable_query(queryset)` in tests to force index-path evaluation (`SET LOCAL enable_seqscan = OFF;`) and prevent unindexed table scans from reaching production.

---

## 2-Phase Async Data Migrations

To avoid table locks during rolling deployments, `django-lightning` decouples schema migrations (DDL) from long-running data backfills (DML):

1. **Pre-Rollout Schema DDL**: Executed synchronously before pod deployment via `k8s/job-migration.yaml` or Fly `release_command`.
2. **Rolling Deployment**: Updates application pods without downtime (`maxUnavailable: 0`).
3. **Post-Rollout Async DML**: Long-running data backfills execute non-blockingly via `BaseAsyncMigration` and SAQ background workers.

```bash
# List registered async background data migrations
uv run manage.py async_migrate --list

# Execute an async migration in the foreground
uv run manage.py async_migrate --run 0001_example_backfill

# Enqueue an async migration to SAQ background workers
uv run manage.py async_migrate --enqueue 0001_example_backfill
```

---

## AI Agent Capabilities & Skills Index

This repository is designed for pair programming with autonomous AI coding agents (such as Antigravity, Claude Code, Cursor, etc.). Master guidelines are defined in **[`AGENTS.md`](file:///e:/code/django-lightning/AGENTS.md)**.

### Available Agent Skills in `.agents/skills/`:

- **[`django-bolt-core`](file:///.agents/skills/django-bolt-core/SKILL.md)**: `BoltAPI` initialization, routing, HTTP verbs, parameter extraction, and response formatting.
- **[`django-bolt-schemas-serializers`](file:///.agents/skills/django-bolt-schemas-serializers/SKILL.md)**: `msgspec.Struct`, `Serializer` validation, field & model validators.
- **[`django-bolt-auth-security`](file:///.agents/skills/django-bolt-auth-security/SKILL.md)**: Custom User Model, JWT authentication, permission guards (`@guard`), CORS, and rate limiting.
- **[`django-bolt-async-orm-db`](file:///.agents/skills/django-bolt-async-orm-db/SKILL.md)**: Async Django ORM (`aget`, `acreate`, `afilter`), query optimization, and connection pooling.
- **[`django-bolt-rust-interop`](file:///.agents/skills/django-bolt-rust-interop/SKILL.md)**: PyO3 Rust extension development, GIL releasing (`py.allow_threads`), Rayon multithreading, zero-copy byte buffers, and msgspec JSON FFI.
- **[`django-bolt-realtime-mcp`](file:///.agents/skills/django-bolt-realtime-mcp/SKILL.md)**: SSE streaming, WebSockets, and `bolt-mcp` MCP server implementation.
- **[`django-bolt-background-workers`](file:///.agents/skills/django-bolt-background-workers/SKILL.md)**: Ultra-high-throughput async queue worker engine (`SAQ` + Redis).
- **[`django-bolt-testing-observability`](file:///.agents/skills/django-bolt-testing-observability/SKILL.md)**: `TestClient` tests, `pytest-asyncio`, Scalar OpenAPI docs, logging/timing middleware.
- **[`django-bolt-docker`](file:///.agents/skills/django-bolt-docker/SKILL.md)**: Multi-stage Docker builds and `docker-compose.yml`.
- **[`django-bolt-kubernetes`](file:///.agents/skills/django-bolt-kubernetes/SKILL.md)**: Enterprise Kubernetes manifests in `k8s/` (Deployment, Service, Ingress, HPA).
- **[`django-bolt-fly-io`](file:///.agents/skills/django-bolt-fly-io/SKILL.md)**: Fly.io deployment configuration `fly.toml` & Fly Postgres integration.
- **[`django-bolt-migration`](file:///.agents/skills/django-bolt-migration/SKILL.md)**: Migration guides from FastAPI, DRF, and Django Ninja to Django-Bolt.
- **[`agentic-task-orchestration`](file:///.agents/skills/agentic-task-orchestration/SKILL.md)**: Worktree creation, task execution, CI pipeline monitoring, automated PR creation, and safe backlog merging.

---

## Testing & Quality Control

Run the automated test suite:

```bash
uv run pytest -v
```

Run code formatting and linting checks:

```bash
uv run ruff check .
uv run ruff format .
```

Or using `just` shortcuts:

```bash
just test
just lint
just format
```

---

## Deployment & Container Orchestration

### Local Docker Stack (Development Reverse Proxy)

Start PostgreSQL, Redis, Django-Bolt, and Caddy reverse proxy locally on port 80:

```bash
docker compose up --build
```

### Production Docker Stack (Automated Let's Encrypt SSL)

Spin up production containers with **Caddy 2** handling automatic Let's Encrypt TLS certificate provisioning, HTTP -> HTTPS redirection, and security hardening headers:

```bash
# Production stack using domain and email for Let's Encrypt ACME registration
DOMAIN=api.example.com LETSENCRYPT_EMAIL=admin@example.com docker compose -f docker-compose.prod.yml up --build -d

# Or via just shortcut:
just docker-prod domain="api.example.com" email="admin@example.com"
```

### Kubernetes (Production SSL via Cert-Manager or Caddy)

1. **Standard Ingress with Cert-Manager (Let's Encrypt)**:
   ```bash
   kubectl apply -f k8s/cert-manager-issuer.yaml
   kubectl apply -f k8s/
   ```

2. **Standalone Caddy Gateway Ingress**:
   ```bash
   kubectl apply -f k8s/caddy-ingress.yaml
   kubectl apply -f k8s/
   ```

3. **Local Development Cluster**:
   ```bash
   kubectl apply -k k8s/dev
   ```

### Fly.io

Deploy to Fly.io:

```bash
fly deploy
```

---

## License

MIT License. Free for open source and commercial use.
