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
```
