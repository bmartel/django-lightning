---
name: django-bolt-background-workers
description: High-performance async background tasks, queue worker management, task fan-out for millions of records, and memory optimization powered by SAQ and Redis.
---

# High-Performance Async Background Tasks (`SAQ` + Redis)

This skill guides AI agents on implementing ultra-high-throughput, low-memory background tasks and queue workers in **django-lightning** using **SAQ (Simple Async Queue)** and **Redis**.

---

## 🚀 Why SAQ over Celery / RQ?

| Metric | Celery (Prefork) | SAQ (Asyncio + Redis) |
|---|---|---|
| **Memory Footprint** | ~500MB - 1GB+ per worker pool | **~25 - 35MB total** |
| **Throughput** | ~200 - 500 tasks/sec | **10,000+ tasks/sec** |
| **Async ORM Support** | Sync blocking wrappers (`async_to_sync`) | **Native `async def` & `await`** |
| **Serialization** | Heavy JSON / Pickle | **Fast `msgspec` / JSON** |
| **Queue Engine** | Complex AMQP / Redis polling | **Atomic Redis Lua scripts & Streams** |

---

## 🛠 WORKER ARCHITECTURE (`app/tasks.py`)

### 1. Defining Async Tasks
Tasks are plain `async def` functions receiving a context dictionary `ctx`:

```python
# app/tasks.py
import os
from django.conf import settings as django_settings
from saq import CronJob, Queue

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
queue = Queue.from_url(REDIS_URL, name="lightning_jobs")


async def process_user_report(ctx, user_id: int):
    """Async background task using Django 5.x Async ORM."""
    from app.models import User

    user = await User.objects.filter(id=user_id).afirst()
    if not user:
        return {"status": "error", "message": "User not found"}

    # Perform heavy async calculation or API call
    return {"status": "success", "user_id": user.id}


async def hourly_cleanup(ctx):
    """Periodic cron task."""
    return {"status": "cleaned"}


# SAQ Worker Configuration settings
settings = {
    "queue": queue,
    "functions": [process_user_report],
    "cron": [
        CronJob(hourly_cleanup, cron="0 * * * *"),
    ],
    "concurrency": 100,  # 100 concurrent async tasks per worker process
}
```

---

## ⚡ PROCESSING MILLIONS OF RECORDS (TASK FAN-OUT PATTERN)

When processing millions of records, **never load all records into memory in a single task**. Instead, use the **Producer-Worker Fan-Out Pattern**:

1. **Producer Task**: Enqueues sub-tasks split by primary key ID ranges (`start_id` to `end_id`).
2. **Worker Tasks**: Process each 10,000-record chunk in parallel using `.values()` and keyset pagination.

```python
# 1. Producer Task: Splits 1M records into 100 tasks of 10,000 records each
async def fanout_million_records_job(ctx):
    from app.models import User
    from django.db import models

    min_id = await User.objects.aaggregate(models.Min("id"))["id__min"] or 0
    max_id = await User.objects.aaggregate(models.Max("id"))["id__max"] or 0

    chunk_size = 10000
    for start_id in range(min_id, max_id + 1, chunk_size):
        end_id = start_id + chunk_size
        await queue.enqueue("process_id_range_batch", start_id=start_id, end_id=end_id)

    return {"status": "enqueued_chunks", "min_id": min_id, "max_id": max_id}


# 2. Worker Task: Processes a single ID range with zero RAM ballooning
async def process_id_range_batch(ctx, start_id: int, end_id: int):
    from app.models import User

    # Use .values() to bypass Model instance allocation and .aiterator() to stream
    query = User.objects.filter(id__gte=start_id, id__lt=end_id, is_active=True).values("id", "email")

    async for user_data in query.aiterator(chunk_size=1000):
        await send_notification(user_data["id"], user_data["email"])

    return {"status": "completed", "range": f"{start_id}-{end_id}"}
```

### PgBouncer Safety in Workers
When running workers against PostgreSQL behind PgBouncer in **Transaction Pooling Mode**:
- Use **Keyset Pagination** (`id > last_id`) or explicit `async with transaction.aatomic():` inside worker tasks so named server-side cursors do not fail with `cursor does not exist`.
- Alternatively, configure workers to use a direct connection (`WORKER_DATABASE_URL`) on PostgreSQL port 5432.

---

## 📤 ENQUEUING TASKS IN API ROUTES

Enqueuing a task is non-blocking and completes in < 1 millisecond:

```python
from app.tasks import queue


@api.post("/reports")
async def generate_report(request: Request, user_id: int):
    # Enqueue task for background worker
    job = await queue.enqueue("process_user_report", user_id=user_id)
    return {"status": "enqueued", "job_id": job.id}
```

---

## 🏃 RUNNING THE WORKER PROCESS

### Local Development
```bash
just worker
# or: uv run saq app.tasks.settings
```

### Docker Compose
```yaml
worker:
  build:
    context: .
    target: dev
  command: uv run saq app.tasks.settings
  environment:
    - REDIS_URL=redis://redis:6379/0
  depends_on:
    - redis
    - db
```

---

## 🛡 WORKER CODE READINESS & DEFERRED ASYNC MIGRATIONS

During zero-downtime rolling deployments, background workers may be executing tasks mid-rollout while running older code versions:

1. **Code Readiness Guard**: `run_async_migration_task` checks if the target `BaseAsyncMigration` class is present in Python runtime. If absent (old worker image), it defers execution (`STATUS_DEFERRED`) without raising fatal exceptions or marking tasks as `FAILED`.
2. **Periodic Auto-Discovery**: `process_pending_async_migrations` runs every 5 minutes (or on worker startup) to automatically pick up `STATUS_PENDING` and `STATUS_DEFERRED` migrations once new worker pods finish deploying.
3. **Dependency Ordering**: `BaseAsyncMigration.check_dependencies_met()` verifies that prerequisite Django schema migrations and prior async migrations are applied before processing batches.
