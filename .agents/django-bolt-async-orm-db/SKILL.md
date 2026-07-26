---
name: django-bolt-async-orm-db
description: High-performance async database access using Django's async ORM (aget, acreate, afilter, aupdate, adelete, select_related), connection pooling, PostgreSQL configuration, and migrations.
compatibility: Agentic coding assistants building web applications with django-bolt.
metadata:
  category: database
  tags: [django, django-bolt, async-orm, postgres, database, migrations]
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

