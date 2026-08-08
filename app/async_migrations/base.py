"""Base Async Migration Framework for django-lightning.

Provides abstract base classes, registry auto-discovery, and safe batch runner
for non-blocking background data migrations.
"""

import abc
import importlib
import logging
import pkgutil
import traceback

from django.utils import timezone

from app.models import AsyncMigration

logger = logging.getLogger("django.lightning.async_migrations")

_ASYNC_MIGRATIONS_REGISTRY: dict[str, type["BaseAsyncMigration"]] = {}


def register_async_migration(cls: type["BaseAsyncMigration"]):
    """Decorator to register an async migration class in the central registry."""
    if not cls.name:
        raise ValueError(
            f"Async migration class {cls.__name__} must define a unique 'name' attribute."
        )
    if cls.name in _ASYNC_MIGRATIONS_REGISTRY:
        raise ValueError(f"Async migration with name '{cls.name}' is already registered.")
    _ASYNC_MIGRATIONS_REGISTRY[cls.name] = cls
    return cls


class BaseAsyncMigration(abc.ABC):
    """Abstract base class for all asynchronous background data migrations."""

    name: str = ""
    description: str = ""
    batch_size: int = 1000

    # Migration dependency ordering specification
    # e.g., "app.0003_example_concurrent_idx_and_async_trigger"
    depends_on_django_migration: str | None = None
    depends_on_async_migration: str | None = None  # e.g., "0001_example_backfill"

    @abc.abstractmethod
    async def get_total_count(self) -> int:
        """Return total count of records needing processing."""
        pass

    @abc.abstractmethod
    async def process_batch(self, offset: int, limit: int) -> int:
        """Process a single batch of records.

        Must return the count of records updated in this batch.
        """
        pass

    async def check_dependencies_met(self) -> tuple[bool, str]:
        """Verify all Django schema and async migration dependencies have been applied."""
        from asgiref.sync import sync_to_async

        if self.depends_on_django_migration:
            parts = self.depends_on_django_migration.split(".")
            if len(parts) == 2:
                app_label, migration_name = parts[0], parts[1]
                from django.db import connection
                from django.db.migrations.recorder import MigrationRecorder

                recorder = MigrationRecorder(connection)
                applied = await sync_to_async(recorder.applied_migrations)()
                if (app_label, migration_name) not in applied:
                    msg = (
                        f"Required Django schema migration '{self.depends_on_django_migration}' "
                        "has not been applied yet."
                    )
                    return (False, msg)

        if self.depends_on_async_migration:
            dep_record = await AsyncMigration.objects.filter(
                name=self.depends_on_async_migration
            ).afirst()
            if not dep_record or dep_record.status != AsyncMigration.STATUS_COMPLETED:
                msg = (
                    f"Required Async data migration '{self.depends_on_async_migration}' "
                    "is not completed."
                )
                return (False, msg)

        return (True, "")

    async def run(self, override_batch_size: int | None = None) -> AsyncMigration:
        """Execute the async migration in non-blocking batches.

        Updates database state in `app.models.AsyncMigration` throughout execution.
        """
        effective_batch_size = override_batch_size or self.batch_size

        # Fetch or create tracking model record
        migration_record, _ = await AsyncMigration.objects.aget_or_create(
            name=self.name,
            defaults={
                "status": AsyncMigration.STATUS_PENDING,
                "batch_size": effective_batch_size,
            },
        )

        if migration_record.status == AsyncMigration.STATUS_COMPLETED:
            logger.info(f"Async migration '{self.name}' has already completed. Skipping.")
            return migration_record

        # Check dependencies before starting
        deps_met, dep_reason = await self.check_dependencies_met()
        if not deps_met:
            migration_record.status = AsyncMigration.STATUS_DEFERRED
            migration_record.error_message = dep_reason
            await migration_record.asave(update_fields=["status", "error_message", "updated_at"])
            logger.warning(f"Async migration '{self.name}' deferred: {dep_reason}")
            return migration_record

        # Atomically claim the migration (compare-and-swap): only one worker may transition
        # it to RUNNING, so the 5-minute cron, a manual enqueue, and a direct call cannot
        # process the same migration concurrently and corrupt the checkpoint counter.
        # NOTE: a worker that crashes mid-run leaves the record RUNNING; reset it to FAILED
        # manually (or via the admin) to allow a retry.
        started = timezone.now()
        claimed = await AsyncMigration.objects.filter(
            name=self.name,
            status__in=[
                AsyncMigration.STATUS_PENDING,
                AsyncMigration.STATUS_DEFERRED,
                AsyncMigration.STATUS_FAILED,
            ],
        ).aupdate(
            status=AsyncMigration.STATUS_RUNNING,
            batch_size=effective_batch_size,
            started_at=started,
            error_message="",
        )
        if not claimed:
            current = await AsyncMigration.objects.aget(name=self.name)
            logger.info(
                f"Async migration '{self.name}' is already {current.status}; not re-running."
            )
            return current

        migration_record = await AsyncMigration.objects.aget(name=self.name)
        processed = migration_record.processed_count

        # total_count is an absolute estimate: rows already processed plus rows still
        # remaining. The loop terminates when process_batch reports no more work, so a
        # resumed run can never be marked COMPLETED while unprocessed rows remain.
        remaining = await self.get_total_count()
        migration_record.total_count = processed + remaining
        await migration_record.asave(update_fields=["total_count", "updated_at"])

        try:
            while True:
                count = await self.process_batch(offset=processed, limit=effective_batch_size)

                # No more items to process — the migration is fully drained.
                if count <= 0:
                    break

                processed += count
                migration_record.processed_count = processed
                if processed > migration_record.total_count:
                    migration_record.total_count = processed
                await migration_record.asave(
                    update_fields=["processed_count", "total_count", "updated_at"]
                )

            # Mark COMPLETED
            migration_record.status = AsyncMigration.STATUS_COMPLETED
            migration_record.processed_count = processed
            migration_record.total_count = max(migration_record.total_count, processed)
            migration_record.completed_at = timezone.now()
            await migration_record.asave(
                update_fields=[
                    "status",
                    "processed_count",
                    "total_count",
                    "completed_at",
                    "updated_at",
                ]
            )
            logger.info(
                f"Async migration '{self.name}' completed successfully. "
                f"Processed {migration_record.processed_count} items."
            )

        except Exception as exc:
            err_msg = f"{exc}\n{traceback.format_exc()}"
            migration_record.status = AsyncMigration.STATUS_FAILED
            migration_record.error_message = err_msg
            await migration_record.asave(update_fields=["status", "error_message", "updated_at"])
            logger.error(f"Async migration '{self.name}' failed: {exc}")
            raise

        return migration_record


def get_registered_async_migrations() -> dict[str, type[BaseAsyncMigration]]:
    """Auto-discover and return dictionary of all registered async migrations."""
    discover_async_migrations()
    return dict(_ASYNC_MIGRATIONS_REGISTRY)


def discover_async_migrations():
    """Import all modules inside app.async_migrations to trigger registration."""
    import app.async_migrations as pkg

    for _, module_name, is_pkg in pkgutil.iter_modules(pkg.__path__):
        if not is_pkg and module_name != "base" and module_name != "operations":
            importlib.import_module(f"app.async_migrations.{module_name}")


def run_async_migration_sync(name: str, batch_size: int | None = None) -> AsyncMigration:
    """Synchronously execute a registered async migration.

    Safely handles running inside or outside an active event loop.
    """
    import asyncio
    import concurrent.futures

    discover_async_migrations()
    registered = get_registered_async_migrations()

    if name not in registered:
        raise ValueError(
            f"Async migration '{name}' not found. Registered: {list(registered.keys())}"
        )

    instance = registered[name]()

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(asyncio.run, instance.run(override_batch_size=batch_size))
            return future.result()
    else:
        return asyncio.run(instance.run(override_batch_size=batch_size))
