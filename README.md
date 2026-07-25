# ⚡ django-lightning

> **High-Performance Agentic Starter Template for [Django-Bolt](https://github.com/dj-bolt/django-bolt)**

`django-lightning` is a production-ready, agentic starter project designed for rapidly building, testing, and deploying ultra-high performance APIs powered by **Django 5.x**, **Django-Bolt** (a Rust-powered API framework delivering ~60k+ RPS), and **`uv`** exclusively.

Equipped with a **Custom User Model** ready out of the box, a comprehensive set of AI agent skills in `.agents/`, and a master `AGENTS.md` file, this repository enables both human engineers and AI coding assistants to build secure, performant, and scalable applications out of the box with Docker, docker-compose, Kubernetes, and Fly.io.

---

## 🔥 Key Features

- **⚡ Blazing Fast Rust API Engine**: Powered by `django-bolt` (`uv run manage.py runbolt`). No `uvicorn` or external server required!
- **🛠 Django Admin Ready Out-of-the-Box**: Native Django Admin interface at `/admin/` configured with `app.User` custom fields (`bio`, `avatar_url`). Run `uv run manage.py createsuperuser` to create your superuser.
- **👤 Custom User Model & Ready-to-Work Auth**: Includes a production-ready Custom `User` model (`AbstractUser`) configured via `AUTH_USER_MODEL = "app.User"` with JWT auth and profile management out of the box.
- **🚀 `uv` Exclusively**: Managed exclusively with `uv` for ultra-fast environment setup, package management, script execution, and testing.
- **🤖 Built-in MCP Server (`bolt-mcp`)**: Native Streamable HTTP Model Context Protocol server mounted at `/mcp` exposing tools, resources, and prompts to AI clients (Claude Desktop, MCP Inspector, etc.).
- **📦 Ultra-Fast Data Validation**: Uses `msgspec.Struct` (10-20x faster than Pydantic) and `django_bolt.serializers.Serializer`.
- **🔄 Async-First ORM**: Leverages Django's native async ORM (`aget`, `acreate`, `afilter`, `aupdate`, `adelete`).
- **📡 Realtime & Streaming**: Server-Sent Events (SSE) and chunked streaming endpoints.
- **📚 Interactive API Docs**: Built-in Scalar OpenAPI interface rendered at `/docs`.
- **🛠 Comprehensive Developer Experience**: Managed via `justfile` using `uv` shortcuts.
- **🐳 Multi-Stage Docker**: Production-optimized multi-stage Dockerfile using `uv`.
- **☸ Enterprise Kubernetes**: Ready-to-apply K8s manifests in `k8s/` including Deployments, ClusterIP Service, Ingress, Secrets, ConfigMaps, and HPA (HorizontalPodAutoscaler).
- **🚀 Fly.io Ready**: Single-command deployment with `fly.toml`.
- **🧠 11 Dedicated Agent Skills**: Comprehensive modular skills in `.agents/` guiding AI agents across every architectural domain.

## 🦀 Scaffolding a New Project via Rust CLI (`create-django-bolt`)

We built a dedicated Rust CLI tool **`create-django-bolt`** located in `cli/`. It compiles to a single, standalone binary with **zero runtime dependencies** (no Node.js, no Cookiecutter).

### 1. Install the CLI Binary

**Option A: 1-Line Standalone Shell Installer (No Rust required)**
```bash
curl -fsSL https://raw.githubusercontent.com/bmartel/django-lightning/main/scripts/install-cli.sh | sh
```

**Option B: Via Cargo (Rust users)**
```bash
cargo install create-django-bolt
```

**Option C: Build locally from source**
```bash
cargo build --manifest-path cli/Cargo.toml --release
```

### 2. Run the Rust CLI Generator
```bash
# Interactive or command-line usage
create-django-bolt new my-app

# Or specify custom target path
create-django-bolt new my-app -p ~/code/my-app
```

---

## ⚡ Scaffolding via Python Script (Alternative)

To quickly scaffold a brand-new project from this starter template:

```bash
# Using just (shortcut)
just new-project my-app ~/code/my-app

# Or using uv directly
uv run python scripts/create-project.py my-app ~/code/my-app
```

This instantly creates a new project directory with updated package names, clean git history, ready for `uv venv` and `uv run manage.py runbolt --dev`.

---

## 🚀 Quick Start

### 1. Setup Virtual Environment with `uv`
```bash
# Clone the repository
git clone https://github.com/bmartel/django-lightning.git
cd django-lightning

# Create virtual environment & install dependencies using uv
uv venv
uv pip install -e ".[dev]"
```

### 2. Run Database Migrations
```bash
uv run manage.py migrate
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

## 🤖 Agentic Capabilities & Skills

This repository is optimized for autonomous AI agents (such as Antigravity, Claude Code, Cursor, etc.). Refer to **[`AGENTS.md`](file:///Users/brandonmartel/code/django-lightning/AGENTS.md)** for master guidelines.

### Available Agent Skills in `.agents/`:
1. **[`django-bolt-core`](file:///.agents/django-bolt-core/SKILL.md)**: `BoltAPI` configuration, routes, parameter extraction (`Query`, `Path`, `Header`, `Cookie`, `Form`, `File`, `Body`, `Depends`), response types.
2. **[`django-bolt-schemas-serializers`](file:///.agents/django-bolt-schemas-serializers/SKILL.md)**: `msgspec.Struct`, `Serializer` validation, field & model validators.
3. **[`django-bolt-auth-security`](file:///.agents/django-bolt-auth-security/SKILL.md)**: Custom User Model, JWT authentication, permission guards (`@guard`), CORS, rate limiting.
4. **[`django-bolt-async-orm-db`](file:///.agents/django-bolt-async-orm-db/SKILL.md)**: Async Django ORM (`aget`, `acreate`, `afilter`), PostgreSQL connection pooling.
5. **[`django-bolt-realtime-mcp`](file:///.agents/django-bolt-realtime-mcp/SKILL.md)**: SSE streaming, WebSockets, and `bolt-mcp` MCP Server implementation.
6. **[`django-bolt-background-workers`](file:///.agents/django-bolt-background-workers/SKILL.md)**: Ultra-high-throughput async queue worker engine (`SAQ` + Redis) with 10,000+ jobs/sec and ~30MB RAM footprint.
7. **[`django-bolt-testing-observability`](file:///.agents/django-bolt-testing-observability/SKILL.md)**: In-memory `TestClient` tests, `pytest-asyncio`, OpenAPI docs, logging/timing middleware.
8. **[`django-bolt-docker`](file:///.agents/django-bolt-docker/SKILL.md)**: Production `Dockerfile`, `.dockerignore`, and `docker-compose.yml`.
9. **[`django-bolt-kubernetes`](file:///.agents/django-bolt-kubernetes/SKILL.md)**: Production Kubernetes manifests in `k8s/` (Deployment, Service, Ingress, HPA).
10. **[`django-bolt-fly-io`](file:///.agents/django-bolt-fly-io/SKILL.md)**: Fly.io deployment config `fly.toml` & Fly Postgres integration.
11. **[`django-bolt-migration`](file:///.agents/django-bolt-migration/SKILL.md)**: Migration guides from FastAPI, DRF, and Django Ninja to Django-Bolt.

---

## 🧪 Testing & Code Quality

Run tests with `uv`:
```bash
uv run pytest -v
```

Run code formatting and linting with `uv`:
```bash
uv run ruff check .
uv run ruff format .
```

Or using `just`:
```bash
just test
just lint
just format
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
