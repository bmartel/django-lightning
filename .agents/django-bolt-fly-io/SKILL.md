---
name: django-bolt-fly-io
description: Fly.io deployment, fly.toml setup, Fly Postgres database bindings, environment secrets management, and automated release.
compatibility: Agentic coding assistants building web applications with django-bolt.
metadata:
  category: deployment
  tags: [fly.io, deployment, fly.toml, postgres, secrets, django-bolt]
---

# Django-Bolt Fly.io Deployment

## `fly.toml` Configuration

```toml
app = "django-lightning"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  DJANGO_SETTINGS_MODULE = "config.settings"
  ALLOWED_HOSTS = ".fly.dev"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = "stop"
  auto_start_machines = true
  min_machines_running = 1
  processes = ["app"]

[[http_service.checks]]
  grace_period = "10s"
  interval = "15s"
  method = "GET"
  path = "/health"
  timeout = "2s"
```

## Deployment Commands

```bash
# Attach Fly Postgres database
fly postgres attach --app django-lightning my-postgres-db

# Set production environment secrets
fly secrets set SECRET_KEY="your-production-secret-key" REDIS_URL="redis://..."

# Deploy application
fly deploy
```
