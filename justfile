# django-lightning developer workflow tasks using uv exclusively

default:
    @just --list

# Scaffold a new project from this starter template
new-project name dest="":
    uv run python scripts/create-project.py {{name}} {{dest}}

# Build the Rust CLI tool (create-django-bolt)
build-cli:
    cargo build --manifest-path cli/Cargo.toml --release

# Generate Rust struct definitions from Django models
rust-codegen:
    uv run manage.py generate_rust_models

# Compile Rust core in debug mode for local development
rust-dev: rust-codegen
    uv run maturin develop


# Compile Rust core in release mode for maximum production performance
rust-build:
    uv run maturin build --release --manifest-path rust_core/Cargo.toml --out target/wheels && uv pip install target/wheels/*.whl


# Run unit tests for Rust native core crate
rust-test:
    cargo test --manifest-path rust_core/Cargo.toml


# Run local development server using django-bolt (runbolt) via uv
dev:
    uv run manage.py runbolt --dev

# Run high-performance SAQ background job worker process
worker:
    uv run saq app.tasks.settings

# Run database migrations via uv
migrate:
    uv run manage.py migrate

# Create new database migration via uv
makemigrations:
    uv run manage.py makemigrations

# List status of all registered async background data migrations
list-async-migrations:
    uv run manage.py async_migrate --list

# Run or enqueue an async background data migration
async-migrate name="":
    {{ if name == "" { "uv run manage.py async_migrate --all" } else { "uv run manage.py async_migrate --run " + name } }}

# Create a Django Admin superuser via uv
createsuperuser:
    uv run manage.py createsuperuser

# Collect static files (e.g. for Django Admin) via uv
collectstatic:
    uv run manage.py collectstatic --noinput

# Run automated tests with pytest via uv
test:
    uv run pytest -v

# Run linting with ruff via uv
lint:
    uv run ruff check .

# Fix linting errors via uv
format:
    uv run ruff format .

# Start local dev services with docker-compose
docker-dev:
    docker compose up --build

# Start production stack locally with docker-compose.prod.yml
docker-prod:
    docker compose -f docker-compose.prod.yml up --build

# Stop local docker services
docker-down:
    docker compose down -v

# Build production docker image locally (target: runner)
docker-build:
    docker build --target runner -t django-lightning:latest .

# Build development docker image locally (target: dev)
docker-build-dev:
    docker build --target dev -t django-lightning:dev .

# Deploy to Fly.io
deploy-fly:
    fly deploy

# Apply production Kubernetes manifests
k8s-apply:
    kubectl apply -f k8s/

# Apply local development Kubernetes manifests
k8s-dev:
    kubectl apply -k k8s/dev

# Run Kubernetes pre-rollout schema migration job
k8s-migrate:
    kubectl apply -f k8s/job-migration.yaml

# Delete Kubernetes manifests
k8s-delete:
    kubectl delete -f k8s/
