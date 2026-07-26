"""Django Management Command to inspect, run, or enqueue async background data migrations.

Usage:
    python manage.py async_migrate --list
    python manage.py async_migrate --run 0001_example_backfill
    python manage.py async_migrate --enqueue 0001_example_backfill
    python manage.py async_migrate --all
"""

import asyncio
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from app.async_migrations.base import (
    discover_async_migrations,
    get_registered_async_migrations,
)
from app.models import AsyncMigration


class Command(BaseCommand):
    help = "Manage and execute non-blocking asynchronous background data migrations."

    def add_arguments(self, parser):
        parser.add_argument(
            "--list",
            action="store_true",
            help="List all registered async migrations and their current execution status.",
        )
        parser.add_argument(
            "--run",
            type=str,
            metavar="MIGRATION_NAME",
            help="Execute the specified async migration synchronously in this process.",
        )
        parser.add_argument(
            "--enqueue",
            type=str,
            metavar="MIGRATION_NAME",
            help="Enqueue the specified async migration for background execution via SAQ worker.",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Run all registered pending async migrations sequentially.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=None,
            help="Override default batch size for processing records.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        discover_async_migrations()
        registered = get_registered_async_migrations()

        if options["list"]:
            self._execute_async(self._list_migrations(registered))
            return

        if options["enqueue"]:
            migration_name = options["enqueue"]
            if migration_name not in registered:
                available = list(registered.keys())
                raise CommandError(
                    f"Async migration '{migration_name}' not found. Registered: {available}"
                )
            self._execute_async(self._enqueue_migration(migration_name, options["batch_size"]))
            return

        if options["run"]:
            migration_name = options["run"]
            if migration_name not in registered:
                available = list(registered.keys())
                raise CommandError(
                    f"Async migration '{migration_name}' not found. Registered: {available}"
                )
            self._execute_async(
                self._run_single_migration(registered[migration_name], options["batch_size"])
            )
            return

        if options["all"]:
            self._execute_async(self._run_all_migrations(registered, options["batch_size"]))
            return

        # Default action: show list
        self._execute_async(self._list_migrations(registered))

    def _execute_async(self, coro):
        """Helper to run async coroutines safely whether inside or outside an active loop."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # If called inside an active loop (e.g. async test runner), run in worker thread
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return asyncio.run(coro)

    async def _list_migrations(self, registered: dict) -> None:
        self.stdout.write(self.style.MIGRATE_HEADING("Registered Async Background Migrations:"))
        self.stdout.write("-" * 80)
        self.stdout.write(
            f"{'Name':<30} {'Status':<12} {'Progress':<15} {'Batch':<8} {'Description'}"
        )
        self.stdout.write("-" * 80)

        # Get DB records asynchronously
        records = {m.name: m async for m in AsyncMigration.objects.all()}

        for name, cls in registered.items():
            db_record = records.get(name)
            status = db_record.status if db_record else AsyncMigration.STATUS_PENDING
            proc = db_record.processed_count if db_record else 0
            tot = db_record.total_count if db_record else 0
            progress = f"{proc}/{tot}"
            batch = db_record.batch_size if db_record else cls.batch_size
            desc = cls.description or cls.__doc__ or ""

            if status == AsyncMigration.STATUS_COMPLETED:
                status_style = self.style.SUCCESS(status)
            elif status == AsyncMigration.STATUS_RUNNING:
                status_style = self.style.WARNING(status)
            elif status == AsyncMigration.STATUS_FAILED:
                status_style = self.style.ERROR(status)
            else:
                status_style = self.style.NOTICE(status)

            self.stdout.write(f"{name:<30} {status_style:<20} {progress:<15} {batch:<8} {desc}")
        self.stdout.write("-" * 80)

    async def _run_single_migration(
        self, migration_cls: type, batch_size: int | None = None
    ) -> None:
        instance = migration_cls()
        self.stdout.write(self.style.NOTICE(f"Starting async migration '{instance.name}'..."))
        result = await instance.run(override_batch_size=batch_size)
        if result.status == AsyncMigration.STATUS_COMPLETED:
            msg = (
                f"✓ Async migration '{instance.name}' completed "
                f"({result.processed_count}/{result.total_count} processed)."
            )
            self.stdout.write(self.style.SUCCESS(msg))
        else:
            msg = f"✗ Async migration '{instance.name}' failed: {result.error_message}"
            self.stdout.write(self.style.ERROR(msg))

    async def _enqueue_migration(self, name: str, batch_size: int | None = None) -> None:
        from app.tasks import queue, run_async_migration_task

        job = await queue.enqueue(
            run_async_migration_task.__name__,
            migration_name=name,
            batch_size=batch_size,
        )
        job_id = job.id if job else "queued"
        msg = f"✓ Enqueued async migration '{name}' to SAQ worker (Job ID: {job_id})."
        self.stdout.write(self.style.SUCCESS(msg))

    async def _run_all_migrations(self, registered: dict, batch_size: int | None = None) -> None:
        for name, cls in registered.items():
            db_record = await AsyncMigration.objects.filter(name=name).afirst()
            if db_record and db_record.status == AsyncMigration.STATUS_COMPLETED:
                self.stdout.write(
                    self.style.SUCCESS(f"Skipping already completed migration '{name}'.")
                )
                continue

            instance = cls()
            self.stdout.write(self.style.NOTICE(f"Executing pending migration '{name}'..."))
            result = await instance.run(override_batch_size=batch_size)
            if result.status == AsyncMigration.STATUS_FAILED:
                self.stdout.write(self.style.ERROR(f"Stopping execution due to error in '{name}'."))
                break
