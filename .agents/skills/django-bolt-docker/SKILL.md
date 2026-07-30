---
name: django-bolt-docker
description: Building multi-stage Docker images and local docker-compose environments for django-bolt projects.
compatibility: Agentic coding assistants building web applications with django-bolt.
metadata:
  category: devops
  tags: [docker, docker-compose, containerization, django-bolt, uv, caddy, letsencrypt, ssl]
---

# Django-Bolt Docker & Containerization

## Critical Docker Guidelines

- **Native Server Execution**: The container `CMD` MUST execute `python manage.py runbolt --host 0.0.0.0 --port 8000 --processes 4`. Do NOT run `uvicorn` or `gunicorn`.
- **Multi-Stage Build**: Use a builder stage with `uv` to compile wheels and resolve virtual environments cleanly.
- **Non-Root Execution**: Run container processes under an unprivileged `django` system user.
- **Reverse Proxy Standard**: Include **Caddy 2** for automated Let's Encrypt / ZeroSSL TLS certificates, HTTP/2 + HTTP/3 support, HTTP -> HTTPS redirects, and unbuffered SSE/WebSocket proxying (`flush_interval -1`).

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

## Production Docker Compose Architecture with Caddy & Let's Encrypt

```yaml
version: "3.8"
services:
  web:
    build:
      context: .
      target: runner
    command: python manage.py runbolt --host 0.0.0.0 --port 8000 --processes 4
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      db: { condition: service_healthy }
      redis: { condition: service_healthy }
    restart: always

  caddy:
    image: caddy:2-alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"
    environment:
      - DOMAIN=${DOMAIN:-localhost}
      - LETSENCRYPT_EMAIL=${LETSENCRYPT_EMAIL:-admin@example.com}
    volumes:
      - ./Caddyfile.prod:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config
    depends_on:
      - web

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-lightning}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-lightningpass}
      POSTGRES_DB: ${POSTGRES_DB:-lightningdb}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-lightning} -d ${POSTGRES_DB:-lightningdb}"]

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]

volumes:
  postgres_data:
  caddy_data:
  caddy_config:
```

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
