"""Custom Django Migration Operations for Async Migrations.

Allows standard Django migrations (app/migrations/*.py) to trigger or enqueue
asynchronous background data migrations.
"""

from typing import Any

from django.db.migrations.operations.base import Operation


class RunAsyncMigration(Operation):
    """Django migration operation to enqueue or execute an Async Migration.

    Usage in Django migration file:
        from app.async_migrations.operations import RunAsyncMigration

        class Migration(migrations.Migration):
            dependencies = [("app", "0002_asyncmigration")]

            operations = [
                RunAsyncMigration("0001_example_backfill", sync=False),
            ]

    Parameters:
        name: Unique name of the registered async migration class.
        sync: If False (default), registers the async migration as PENDING for
              post-rollout background execution by SAQ workers.
              If True, executes the async migration synchronously during `manage.py migrate`.
    """

    reduces_to_sql = False

    def __init__(self, name: str, sync: bool = False):
        self.name = name
        self.sync = sync

    def deconstruct(self) -> tuple[str, list[Any], dict[str, Any]]:
        kwargs: dict[str, Any] = {"name": self.name}
        if self.sync:
            kwargs["sync"] = self.sync
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}",
            [],
            kwargs,
        )

    def state_forwards(self, app_label: str, state: Any) -> None:
        pass

    def database_forwards(
        self, app_label: str, schema_editor: Any, from_state: Any, to_state: Any
    ) -> None:
        from app.async_migrations.base import (
            discover_async_migrations,
            get_registered_async_migrations,
            run_async_migration_sync,
        )
        from app.models import AsyncMigration

        discover_async_migrations()
        registered = get_registered_async_migrations()

        if self.name not in registered:
            # If migration not found, log warning or raise error depending on context
            raise ValueError(
                f"RunAsyncMigration refers to unregistered async migration '{self.name}'. "
                f"Registered migrations: {list(registered.keys())}"
            )

        if self.sync:
            # Execute synchronously during manage.py migrate
            run_async_migration_sync(self.name)
        else:
            # Register in DB as PENDING for post-rollout background execution
            migration_cls = registered[self.name]
            instance = migration_cls()
            AsyncMigration.objects.get_or_create(
                name=self.name,
                defaults={
                    "status": AsyncMigration.STATUS_PENDING,
                    "batch_size": instance.batch_size,
                },
            )

    def database_backwards(
        self, app_label: str, schema_editor: Any, from_state: Any, to_state: Any
    ) -> None:
        # Reversing an async migration registration is a no-op to preserve data logs
        pass

    def describe(self) -> str:
        mode = "synchronously" if self.sync else "asynchronously via background worker"
        return f"Run Async Migration '{self.name}' ({mode})"
