---
name: django-bolt-docker
description: Building multi-stage Docker images and local docker-compose environments for django-bolt projects.
compatibility: Agentic coding assistants building web applications with django-bolt.
metadata:
  category: devops
  tags: [docker, docker-compose, containerization, django-bolt, uv]
---

# Django-Bolt Docker & Containerization

## Critical Docker Guidelines

- **Native Server Execution**: The container `CMD` MUST execute `python manage.py runbolt --host 0.0.0.0 --port 8000 --processes 4`. Do NOT run `uvicorn` or `gunicorn`.
- **Multi-Stage Build**: Use a builder stage with `uv` to compile wheels and resolve virtual environments cleanly.
- **Non-Root Execution**: Run container processes under an unprivileged `django` system user.

## Production `Dockerfile` Pattern

```dockerfile
FROM python:3.12-slim-bookworm AS builder
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev curl && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml .
RUN uv venv /app/.venv && . /app/.venv/bin/activate && uv pip install .

FROM python:3.12-slim-bookworm AS runner
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl && rm -rf /var/lib/apt/lists/*
RUN groupadd -r django && useradd -r -g django django
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . /app
RUN chown -R django:django /app
USER django
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1 DJANGO_SETTINGS_MODULE=config.settings
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s CMD curl -f http://localhost:8000/health || exit 1
CMD ["python", "manage.py", "runbolt", "--host", "0.0.0.0", "--port", "8000", "--processes", "4"]
```

## `docker-compose.yml` Architecture

```yaml
version: "3.8"
services:
  web:
    build: .
    command: python manage.py runbolt --host 0.0.0.0 --port 8000 --dev
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgres://lightning:lightningpass@db:5432/lightningdb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      db: { condition: service_healthy }
      redis: { condition: service_healthy }

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: lightning
      POSTGRES_PASSWORD: lightningpass
      POSTGRES_DB: lightningdb
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U lightning -d lightningdb"]

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]

## Migration Service Pattern

To run database migrations cleanly prior to launching services in Docker Compose:
```yaml
  migrate:
    build: .
    command: uv run manage.py migrate --noinput
    environment:
      - DATABASE_URL=postgres://lightning:lightningpass@db:5432/lightningdb
    depends_on:
      db:
        condition: service_healthy
```
Run pre-start migrations with `docker compose run --rm migrate` or `docker compose up --build`.

```
