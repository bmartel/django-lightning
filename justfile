# django-lightning developer workflow tasks using uv exclusively

default:
    @just --list

# Scaffold a new project from this starter template
new-project name dest="":
    uv run python scripts/create-project.py {{name}} {{dest}}

# Build the Rust CLI tool (create-django-bolt)
build-cli:
    cargo build --manifest-path cli/Cargo.toml --release

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

# Start local services with docker-compose
docker-up:
    docker compose up --build -d

# Stop local docker services
docker-down:
    docker compose down -v

# Build docker image locally
docker-build:
    docker build -t django-lightning:latest .

# Deploy to Fly.io
deploy-fly:
    fly deploy

# Apply Kubernetes manifests
k8s-apply:
    kubectl apply -f k8s/

# Run Kubernetes pre-rollout schema migration job
k8s-migrate:
    kubectl apply -f k8s/job-migration.yaml

# Delete Kubernetes manifests
k8s-delete:
    kubectl delete -f k8s/

