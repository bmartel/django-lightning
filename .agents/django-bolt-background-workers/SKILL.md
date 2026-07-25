---
name: django-bolt-background-workers
description: High-performance async background tasks & queue worker management powered by SAQ and Redis.
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
from saq import Queue, CronJob
from django.conf import settings as django_settings
import os

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
  build: .
  command: uv run saq app.tasks.settings
  environment:
    - REDIS_URL=redis://redis:6379/0
  depends_on:
    - redis
    - db
```
