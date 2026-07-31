---
name: django-bolt-async-orm-db
description: High-performance async database access using Django's async ORM (aget, acreate, afilter, aupdate, adelete, select_related, prefetch_related, only, defer, values), query optimization, indexing strategies, PgBouncer compatibility, and zero-downtime migrations.
compatibility: Agentic coding assistants building web applications with django-bolt.
metadata:
  category: database
  tags: [django, django-bolt, async-orm, postgres, pgbouncer, database, query-optimization, indexing, n-plus-one, migrations]
---

# Django-Bolt Async ORM & Database Access

## Dual Database Query Engine Paradigm

`django-lightning` supports two database access mechanisms:
1. **Django Async ORM (`app/models.py`)**: Standard, primary database interface for REST APIs, CRUD, Auth, Admin, and business logic.
2. **High-Performance Rust DB Engine (`rust_core::db` + `sqlx`)**: Optional high-throughput query engine for sub-millisecond API endpoints (>50k RPS), vector searches, bulk transformations, and streaming aggregations. Synchronized with Django models via `just rust-codegen` (`generate_rust_models`).

## ⚡ Native Time-Ordered UUIDv7 Primary Keys (`UUID7Field`)

`django-lightning` provides native time-ordered 128-bit **UUIDv7** primary key support in `app.fields.UUID7Field`:

- **B-Tree Index Friendly**: Unlike random UUIDv4 (which causes severe B-Tree index fragmentation and cache misses on insertion), UUIDv7 embeds a 48-bit millisecond timestamp at the beginning of the UUID bytes. New records append sequentially to the rightmost index page in PostgreSQL (identical B-Tree locality to `BigAutoField`).
- **PostgreSQL 128-Bit Native Storage**: Stored in PostgreSQL's native 16-byte `uuid` column type.
- **Python 3.13+ & Rust Native Speed**: Generates time-ordered UUIDv7 via standard library `uuid.uuid7()` or PyO3 Rust extension fallback (`gen_uuid7()`).

```python
from django.db import models
from app.fields import UUID7Field

class Organization(models.Model):
    id = UUID7Field(primary_key=True)
    name = models.CharField(max_length=255)
```

---

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

---

## ⚡ High-Performance Query Optimization Rules

To guarantee high throughput and low latency (~60k+ RPS), all database queries must avoid common ORM pitfalls: **N+1 queries**, **field overfetching**, **missing database indexes**, and **unoptimized SQL joins**.

### 1. Eliminating N+1 Queries (`select_related` & `prefetch_related`)

An N+1 query bug occurs when code iterates over $N$ parent objects and accesses a related object on each iteration, causing $1 + N$ separate database round-trips.

#### ❌ POOR PERFORMANCE (N+1 Queries):
```python
# Triggers 1 query for orders + N queries for user on each iteration!
orders = [order async for order in Order.objects.filter(status="paid")[:100]]
for order in orders:
    print(order.user.username)  # 💥 Separate DB query per order!
```

#### ✅ OPTIMAL PERFORMANCE (`select_related` for ForeignKeys / OneToOne):
`select_related` performs an SQL `JOIN` in a single query.

```python
# Executes 1 single SQL query with JOIN
orders = [order async for order in Order.objects.select_related("user").filter(status="paid")[:100]]
for order in orders:
    print(order.user.username)  # Zero extra DB queries!
```

#### ✅ OPTIMAL PERFORMANCE (`prefetch_related` for ManyToMany / Reverse ForeignKeys):
`prefetch_related` executes 2 queries (parent records + batch child records via SQL `IN (...)`).

```python
from django.db.models import Prefetch
from app.models import Category, Item

# Fetch categories and prefetch active items in 2 queries total
categories = [
    cat
    async for cat in Category.objects.prefetch_related(
        Prefetch(
            "items", queryset=Item.objects.filter(is_active=True).only("id", "name", "category_id")
        )
    )
]
```

---

### 2. Preventing Field Overfetching (`.only()`, `.defer()`, `.values()`)

By default, Django SELECTs all columns (`SELECT *`). Fetching unneeded `TEXT`, `JSONB`, or `BYTEA` columns increases database disk I/O, network latency, and Python memory overhead.

#### ❌ POOR PERFORMANCE (Overfetching large fields):
```python
# SELECT * fetches heavy `audit_log_json`, `raw_payload`, `avatar_blob` even if unused!
users = [user async for user in User.objects.filter(is_active=True)[:100]]
```

#### ✅ OPTIMAL PERFORMANCE (`.only()` for specific Model fields):
```python
# SELECTs ONLY `id`, `username`, `email`
users = [
    user async for user in User.objects.only("id", "username", "email").filter(is_active=True)[:100]
]
```

#### ✅ OPTIMAL PERFORMANCE (`.defer()` to omit specific heavy columns):
```python
# SELECTs all columns EXCEPT `raw_payload` and `avatar_blob`
users = [
    user
    async for user in User.objects.defer("raw_payload", "avatar_blob").filter(is_active=True)[:100]
]
```

#### ✅ OPTIMAL PERFORMANCE (`.values()` / `.values_list()` for primitives):
Bypasses Model object creation entirely, returning plain Python dicts/tuples (80%+ memory reduction):

```python
# Returns list of primitive dicts: [{'id': 1, 'email': 'user@example.com'}]
user_dicts = [row async for row in User.objects.filter(is_active=True).values("id", "email")[:100]]
```

---

### 3. Database Indexing Guidelines & Best Practices

Queries filtering or sorting on unindexed columns force PostgreSQL to perform full table scans (`Seq Scan`), causing query duration to grow linearly $O(N)$ with table size.

#### Single & Composite B-Tree Indexes
- **Single-Column Indexes**: Add `db_index=True` for foreign keys, status flags, or lookup fields searched individually (`User.email`, `Order.status`).
- **Composite Indexes (Leftmost Prefix Rule)**: Place fields filtered/sorted together into a multi-column `models.Index`. Order matters: column with highest selectivity or `WHERE` equality should be first, followed by range/sort columns.

```python
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            # Supports queries like: WHERE user_id = X AND status = Y ORDER BY created_at DESC
            models.Index(
                fields=["user", "status", "-created_at"], name="order_user_status_created_idx"
            ),
        ]
```

#### PostgreSQL Special Indexes (GIN & Trigram)
- **JSONB / Array Fields**: Use `GinIndex` for efficient JSON key lookups and array containment (`@>`).
- **Wildcard Search (`icontains`)**: Unindexed `icontains` performs `LIKE '%search%'` requiring full table scans. Use PostgreSQL `gin_trgm_ops` trigram index for fast wildcard searches.

```python
from django.contrib.postgres.indexes import GinIndex, OpClass
from django.db import models


class Article(models.Model):
    title = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict)

    class Meta:
        indexes = [
            # GIN index for fast JSONB querying
            GinIndex(fields=["metadata"], name="article_metadata_gin"),
            # Trigram GIN index for fast title__icontains searches
            GinIndex(
                OpClass("title", name="gin_trgm_ops"),
                name="article_title_trgm_idx",
            ),
        ]
```

#### Concurrent Indexing for Existing Large Tables
When adding indexes to large existing production tables, use `AddIndexConcurrently` in Django migrations with `atomic = False` to prevent blocking WRITE locks on the table:

```python
from django.db import migrations, models
from django.contrib.postgres.operations import AddIndexConcurrently


class Migration(migrations.Migration):
    atomic = False  # Mandatory for concurrent index creation

    dependencies = [("app", "0005_previous")]

    operations = [
        AddIndexConcurrently(
            model_name="order",
            index=models.Index(fields=["created_at"], name="order_created_at_concurrent_idx"),
        ),
    ]
```

---

### 4. Efficient Joins, Subqueries & Aggregations

#### Avoid Massive `IN (...)` Lists with `Exists()` / `Subquery()`
Passing large lists of IDs into `filter(id__in=huge_id_list)` generates bloated SQL queries and consumes excessive RAM. Use `Exists()` or `Subquery()` instead.

#### ❌ POOR PERFORMANCE (In-memory ID list evaluation):
```python
paid_user_ids = [u["id"] async for u in User.objects.filter(is_paid=True).values("id")]
orders = [order async for order in Order.objects.filter(user_id__in=paid_user_ids)]
```

#### ✅ OPTIMAL PERFORMANCE (`Exists()` subquery in single SQL execution):
```python
from django.db.models import Exists, OuterRef

paid_users = User.objects.filter(id=OuterRef("user_id"), is_paid=True)
orders = [
    order
    async for order in Order.objects.annotate(has_paid_user=Exists(paid_users)).filter(
        has_paid_user=True
    )
]
```

---

### 5. Surgical Query Scalability Profiling & Small-Dataset Index Testing

> [!WARNING]
> **Small-Dataset Optimizer Illusion**: On small test tables (e.g. 5–10 rows in test DBs), database query planners choose `Seq Scan` over `Index Scan` because reading 1 page is faster than index lookup overhead. This falsely hides missing indexes in test environments, leading to production latency explosions on large tables!

#### Forcing Index-Path Evaluation (`SET LOCAL enable_seqscan = OFF;`)
The surgical solution is `app.profiling.assert_scalable_query(queryset)`. It executes `EXPLAIN (FORMAT JSON)` under `SET LOCAL enable_seqscan = OFF;` (or parses query plans for SQLite) to force the query planner to evaluate index paths. If no index exists, it instantly catches unindexed table scans, unindexed sorts, and cartesian joins regardless of dataset size!

```python
import pytest
from app.models import Order
from app.profiling import assert_scalable_query, UnscalableQueryError


@pytest.mark.django_db(transaction=True)
async def test_order_search_query_scalability():
    # Query building
    queryset = Order.objects.filter(user_id=123, status="paid").order_by("-created_at")

    # Surgically assert that index paths exist for filters and sorting
    report = await assert_scalable_query(queryset)
    assert report.is_scalable is True
```

To inspect executed SQL queries and timing during development:

```python
from django.db import connection

# Reset query log and count executed queries in async code
connection.queries_log.clear()
users = [u async for u in User.objects.select_related("profile").filter(is_active=True)[:10]]
print(f"Executed queries: {len(connection.queries)}")
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

---

## Standard Django App Creation & Model Codegen

### 1. Generating & Registering New Apps
Create domain apps using standard Django conventions:
```bash
uv run manage.py startapp <app_name>
```
Register the app in `INSTALLED_APPS` inside `config/settings.py`:
```python
INSTALLED_APPS = [
    ...,
    "<app_name>.apps.<AppConfigClassName>",
]
```

### 2. Automatic Tooling & Rust Codegen Introspection
- **Migrations**: `uv run manage.py makemigrations` and `uv run manage.py migrate` manage models across all installed apps.
- **Rust Struct Codegen**: Run `uv run manage.py generate_rust_models` to update PyO3/Rust struct definitions for models in all installed Django apps.
- **MCP Database Introspection**: The `inspect_db_schema` MCP tool automatically introspects models from all installed apps without manual configuration.
