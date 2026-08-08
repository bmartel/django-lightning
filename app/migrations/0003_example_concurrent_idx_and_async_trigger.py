"""Example Django Migration demonstrating non-atomic migrations and Async Migration triggers.

This migration illustrates:
1. `atomic = False`: required so a data-migration trigger can run outside a single
   transaction, and a prerequisite for CREATE INDEX CONCURRENTLY on PostgreSQL.
2. `RunAsyncMigration`: enqueues an Async Background Data Migration for post-rollout execution.

NOTE on index creation: this uses the portable `migrations.AddIndex` so the template's
default SQLite dev/test database keeps working. On a large PostgreSQL table, swap it for
`django.contrib.postgres.operations.AddIndexConcurrently` (Postgres-only) to build the
index without taking an exclusive table lock.
"""

from django.db import migrations, models

from app.async_migrations.operations import RunAsyncMigration


class Migration(migrations.Migration):
    # Non-atomic execution is required for the async trigger (and for Postgres concurrent indexes)
    atomic = False

    dependencies = [
        ("app", "0002_asyncmigration"),
    ]

    operations = [
        # Portable index creation (works on SQLite and PostgreSQL). See module docstring
        # for the AddIndexConcurrently alternative on large Postgres tables.
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["created_at"], name="user_created_at_idx"),
        ),
        # Async Data Migration Trigger: Enqueues background backfill for post-rollout worker execution
        RunAsyncMigration("0001_example_backfill", sync=False),
    ]
