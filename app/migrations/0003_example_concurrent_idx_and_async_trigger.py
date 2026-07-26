"""Example Django Migration demonstrating non-atomic concurrent index creation and Async Migration triggers.

This migration illustrates:
1. `atomic = False`: Required by PostgreSQL for CREATE INDEX CONCURRENTLY (non-blocking).
2. `AddIndexConcurrently`: Builds index without taking exclusive table locks on large datasets.
3. `RunAsyncMigration`: Enqueues an Async Background Data Migration to be executed post-rollout.
"""

from django.db import migrations, models

from app.async_migrations.operations import RunAsyncMigration


class Migration(migrations.Migration):
    # Non-atomic execution is mandatory for PostgreSQL concurrent index operations
    atomic = False

    dependencies = [
        ("app", "0002_asyncmigration"),
    ]

    operations = [
        # Standard schema operation: Add database index
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["created_at"], name="user_created_at_idx"),
        ),
        # Async Data Migration Trigger: Enqueues background backfill for post-rollout worker execution
        RunAsyncMigration("0001_example_backfill", sync=False),
    ]
