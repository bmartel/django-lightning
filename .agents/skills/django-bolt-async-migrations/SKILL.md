---
name: django-bolt-async-migrations
description: 2-Phase Zero-Downtime Async Background Data Migration Framework for django-lightning powered by BaseAsyncMigration and SAQ workers.
---

# 🚀 2-Phase Zero-Downtime Async Data Migration Framework

When building high-performance, high-availability Django applications, running heavy database data backfills inside standard `python manage.py migrate` DDL commands causes:
- ❌ Long database lockouts and table locks.
- ❌ Deployment timeouts during container initialization.
- ❌ Production downtime during zero-downtime rolling updates.

`django-lightning` provides a **2-Phase Zero-Downtime Async Migration Engine** located in `app/async_migrations/`.

---

## 📐 The 2-Phase Migration Paradigm

### Phase 1: Pre-Rollout Schema DDL (Instant & Non-Blocking)
Run standard schema migrations before rolling out new code:
```bash
uv run manage.py makemigrations
uv run manage.py migrate
```
- Only add nullable columns, new tables, or new indexes.
- **Never** perform data transformation loops or bulk updates in Phase 1.

### Phase 2: Post-Rollout Async DML Data Backfill (Background Worker)
Execute data backfills asynchronously using `BaseAsyncMigration` and SAQ workers:
```bash
# List all registered async migrations
uv run manage.py async_migrate --list

# Run specific async migration
uv run manage.py async_migrate --run m0001_example_backfill
```

---

## 🛠 Creating a New Async Data Migration

Create a python module in `app/async_migrations/` (e.g. `app/async_migrations/m0002_backfill_user_avatars.py`):

```python
from app.async_migrations.base import BaseAsyncMigration
from app.models import User
from app.utils import akeyset_chunker


class Migration(BaseAsyncMigration):
    name = "m0002_backfill_user_avatars"
    description = "Backfill default avatar URLs for legacy user accounts"
    batch_size = 1000

    async def get_total_count(self) -> int:
        return await User.objects.filter(avatar_url="").acount()

    async def process_batch(self, batch_size: int) -> int:
        # Select batch using lightweight values dicts for minimal memory footprint
        users = await User.objects.filter(avatar_url="").values("id")[:batch_size]
        user_ids = [u["id"] async for u in users]
        if not user_ids:
            return 0

        # Perform bulk update
        updated_count = await User.objects.filter(id__in=user_ids).aupdate(
            avatar_url="https://static.example.com/default-avatar.png"
        )
        return updated_count
```

---

## 🔄 Code Readiness & Rolling Deploy Safety

If a background worker picks up a migration before the new code version has rolled out across all pods:
1. `run_async_migration_task` checks `get_registered_async_migrations()`.
2. If the migration class is not yet loaded on that pod, it marks the task status as **`DEFERRED`** cleanly without error.
3. The cron job `process_pending_async_migrations` re-evaluates deferred tasks every 5 minutes until all pods run the updated code version.

---

## 🧪 Testing Async Migrations

Always test async background migrations using `pytest-asyncio`:

```python
import pytest
from app.async_migrations.m0002_backfill_user_avatars import Migration
from app.models import AsyncMigration, User


@pytest.mark.django_db
async def test_avatar_backfill_migration():
    await User.objects.acreate(username="legacy1", avatar_url="")
    migration = Migration()
    result = await migration.run()

    assert result.status == AsyncMigration.STATUS_COMPLETED
    assert result.processed_count == 1

    updated_user = await User.objects.aget(username="legacy1")
    assert updated_user.avatar_url != ""
```
