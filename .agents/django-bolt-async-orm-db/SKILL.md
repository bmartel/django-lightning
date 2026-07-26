---
name: django-bolt-async-orm-db
description: High-performance async database access using Django's async ORM (aget, acreate, afilter, aupdate, adelete, select_related), connection pooling, PostgreSQL configuration, PgBouncer compatibility, and migrations.
compatibility: Agentic coding assistants building web applications with django-bolt.
metadata:
  category: database
  tags: [django, django-bolt, async-orm, postgres, pgbouncer, database, migrations]
---

# Django-Bolt Async ORM & Database Access

## Mandatory Async ORM Patterns

In `django-bolt` async route handlers, **never call blocking sync ORM methods** (`filter()`, `get()`, `create()`, `save()`, `delete()`). Always use the `a` prefixed async methods!

```python
from app.models import Item

# Async Get / Filter
item = await Item.objects.filter(id=item_id).afirst()
exists = await Item.objects.filter(name=name).aexists()
count = await Item.objects.filter(is_active=True).acount()

# Async Create / Update / Delete
new_item = await Item.objects.acreate(name="Widget", price=19.99)
await Item.objects.filter(is_active=False).aupdate(price=0.0)
await item.adelete()

# Async Iteration
async for item in Item.objects.filter(is_active=True)[:50]:
    print(item.name)
```

## Optimizing Related Objects (`select_related` / `prefetch_related`)

```python
# Use select_related before async iteration to prevent N+1 query overhead
qs = Item.objects.select_related("created_by").filter(is_active=True)
async for item in qs:
    print(item.name, item.created_by.username)
```

---

## High-Volume Data Processing & Memory Optimization (1M+ Records)

Django `Model` instances carry Python heap overhead (`__dict__`, signals, metadata). Loading 1,000,000 model objects into memory at once can balloon RAM usage to gigabytes and cause Out-Of-Memory (OOM) crashes.

### 1. Bypass Model Instantiation (`.values()` / `.values_list()`)
When you don't need `.save()` method overhead, fetch raw primitive `dict` or `tuple` rows. This reduces memory footprint by **80%+** and improves query speed by **5x-10x**.

```python
# Fetches lightweight dicts: {'id': 101, 'email': 'alex@example.com'}
query = User.objects.filter(status="pending").values("id", "email")
async for row in query.aiterator(chunk_size=5000):
    await send_webhook(row["id"], row["email"])
```

### 2. Async Cursor Streaming (`aiterator(chunk_size=...)`)
Stream DB cursor rows lazily in chunks instead of fetching all records at once into Python memory:

```python
async for record in MyModel.objects.filter(is_processed=False).aiterator(chunk_size=2000):
    await process_record(record)
```

### 3. Keyset Pagination (ID Chunking)
Avoid SQL `OFFSET` on large tables (which degrades to $O(N)$ query time). Filter by indexed primary key `id > last_seen_id`:

```python
from app.utils import akeyset_chunker

# Use ready-to-go akeyset_chunker helper for zero-memory degradation and PgBouncer safety
async for chunk in akeyset_chunker(User.objects.filter(is_active=True), chunk_size=2000):
    for row in chunk:
        await process_user(row["id"], row["email"])
```

### 4. Set-Based Bulk Operations (`abulk_create` & `abulk_update`)
Perform updates in single batch SQL queries instead of per-row `save()` loops:

```python
# Update 1,000 records in a single database round-trip
await User.objects.filter(id__in=batch_ids).aupdate(status="processed")
```

---

## PgBouncer Connection Pooling Compatibility

In **PgBouncer Transaction Pooling Mode** (`pool_mode = transaction`), PgBouncer assigns PostgreSQL server connections for the duration of a single transaction/query. Standard Django `aiterator()` uses PostgreSQL **Named Server-Side Cursors** (`DECLARE cursor_name CURSOR FOR ...`), which can fail with `ERROR: cursor does not exist` if subsequent `FETCH` calls are routed to a different connection.

### Production Solutions for PgBouncer

1. **Keyset Pagination (`id > last_id`) — Recommended**: Does not use server-side cursors. Each batch is a self-contained 2ms query that grabs and immediately releases its connection back to the pool.
2. **Transaction Pinning (`transaction.aatomic()`)**: Wrapping `aiterator()` inside `async with transaction.aatomic()` pins the PgBouncer server connection to the client for the duration of the transaction block.
3. **Separate Worker Connection Pool**: Configure background queue workers (`saq`, `async_migrate`) to connect via PostgreSQL direct port 5432 or PgBouncer Session Pool mode, while web API routes (`runbolt`) connect via transaction-pooled port 6432.
4. **`DISABLE_SERVER_SIDE_CURSORS = True`**: Set in `DATABASES['default']['OPTIONS']` to disable named server-side cursors globally in Django.

---

## Migration Strategy Decision Matrix

| Requirement / Scenario | Recommended Tool | `atomic` Setting | Execution Phase |
| --- | --- | --- | --- |
| **Fast Structural DDL** (add nullable column, new model) | Standard Django Migration (`AddField`, `CreateModel`) | `atomic = True` | Pre-rollout (K8s Job / Fly `release_command`) |
| **PostgreSQL Concurrent Index** (index large existing table) | `AddIndexConcurrently` | `atomic = False` | Pre-rollout (K8s Job / Fly `release_command`) |
| **Heavy Data Backfill / Transformation** | `BaseAsyncMigration` + `RunAsyncMigration("name")` | N/A (Chunked async ORM) | Post-rollout (SAQ Worker / `async_migrate`) |
| **3-Phase Expand/Contract Schema Change** | Phase 1 DDL -> Phase 2 DML -> Phase 3 DDL | Phase 1/3: DDL, Phase 2: DML | Pre-rollout 1 -> Post-rollout -> Pre-rollout 2 |

---

## Triggering Async Migrations in Standard Django Migrations

Use `RunAsyncMigration` inside `app/migrations/*.py` to link async backfills directly to Django migration steps:

```python
from django.db import migrations, models
from app.async_migrations.operations import RunAsyncMigration

class Migration(migrations.Migration):
    # Set atomic = False if using AddIndexConcurrently or non-atomic operations
    atomic = False

    dependencies = [
        ("app", "0002_asyncmigration"),
    ]

    operations = [
        # 1. Non-blocking PostgreSQL index creation
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["created_at"], name="user_created_at_idx"),
        ),
        # 2. Register/Enqueue Async Background Data Backfill for post-rollout worker execution
        RunAsyncMigration("0001_example_backfill", sync=False),
    ]
```

- `sync=False` (default): Registers the async migration in `PENDING` state for SAQ worker execution post-rollout without holding up container startup.
- `sync=True`: Executes the async migration inline during `uv run manage.py migrate`.
