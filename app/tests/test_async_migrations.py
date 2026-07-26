import pytest
from django.core.management import call_command
from django.utils import timezone

from app.async_migrations.base import (
    BaseAsyncMigration,
    discover_async_migrations,
    get_registered_async_migrations,
    register_async_migration,
)
from app.models import AsyncMigration, User
from app.tasks import run_async_migration_task


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_async_migration_model_crud():
    """Test AsyncMigration model creation, status tracking, and __str__ output."""
    record = await AsyncMigration.objects.acreate(
        name="test_migration_01",
        status=AsyncMigration.STATUS_RUNNING,
        batch_size=200,
        total_count=1000,
        processed_count=500,
        started_at=timezone.now(),
    )

    assert record.id is not None
    assert record.status == AsyncMigration.STATUS_RUNNING
    assert "test_migration_01 [RUNNING] (500/1000)" in str(record)

    record.status = AsyncMigration.STATUS_COMPLETED
    record.processed_count = 1000
    record.completed_at = timezone.now()
    await record.asave()

    fetched = await AsyncMigration.objects.filter(name="test_migration_01").afirst()
    assert fetched is not None
    assert fetched.status == AsyncMigration.STATUS_COMPLETED
    assert fetched.processed_count == 1000


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_example_async_migration_run():
    """Test running 0001_example_backfill async migration on user records."""
    # Create test users with empty bio
    user1 = await User.objects.acreate(username="test_user1", email="user1@example.com", bio="")
    user2 = await User.objects.acreate(username="test_user2", email="user2@example.com", bio="")

    discover_async_migrations()
    registered = get_registered_async_migrations()
    assert "0001_example_backfill" in registered

    migration_cls = registered["0001_example_backfill"]
    instance = migration_cls()

    # Execute async migration
    record = await instance.run(override_batch_size=10)

    assert record.status == AsyncMigration.STATUS_COMPLETED
    assert record.processed_count >= 2

    # Verify user bios were updated
    u1 = await User.objects.filter(id=user1.id).afirst()
    u2 = await User.objects.filter(id=user2.id).afirst()
    assert u1.bio == "Standard Lightning Account"
    assert u2.bio == "Standard Lightning Account"


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_async_migration_failure_handling():
    """Test that exceptions during batch processing are caught and recorded properly."""

    @register_async_migration
    class FailingMigration(BaseAsyncMigration):
        name = "test_failing_migration"
        description = "Intentionally fails"

        async def get_total_count(self) -> int:
            return 100

        async def process_batch(self, offset: int, limit: int) -> int:
            raise RuntimeError("Database timeout during backfill")

    instance = FailingMigration()

    with pytest.raises(RuntimeError, match="Database timeout during backfill"):
        await instance.run()

    record = await AsyncMigration.objects.filter(name="test_failing_migration").afirst()
    assert record is not None
    assert record.status == AsyncMigration.STATUS_FAILED
    assert "Database timeout during backfill" in record.error_message


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_async_migrate_management_command(capsys):
    """Test running python manage.py async_migrate with --list and --run."""
    await User.objects.acreate(username="cmd_user", email="cmd@example.com", bio="")

    # Call management command --list
    call_command("async_migrate", list=True)
    captured = capsys.readouterr()
    assert "0001_example_backfill" in captured.out

    # Call management command --run
    call_command("async_migrate", run="0001_example_backfill")

    record = await AsyncMigration.objects.filter(name="0001_example_backfill").afirst()
    assert record is not None
    assert record.status == AsyncMigration.STATUS_COMPLETED


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_run_async_migration_task_saq():
    """Test executing run_async_migration_task function directly."""
    await User.objects.acreate(username="task_user", email="task@example.com", bio="")

    result = await run_async_migration_task(None, "0001_example_backfill")
    assert result["status"] == AsyncMigration.STATUS_COMPLETED
    assert result["name"] == "0001_example_backfill"
    assert result["processed_count"] >= 1


@pytest.mark.django_db(transaction=True)
def test_run_async_migration_operation():
    """Test RunAsyncMigration Django migration operation."""
    from app.async_migrations.operations import RunAsyncMigration

    op = RunAsyncMigration("0001_example_backfill", sync=False)
    assert op.name == "0001_example_backfill"
    assert op.sync is False

    # Test deconstruct for Django migration serialization
    path, args, kwargs = op.deconstruct()
    assert "RunAsyncMigration" in path
    assert kwargs["name"] == "0001_example_backfill"

    # Test database_forwards registers PENDING migration in DB
    op.database_forwards("app", None, None, None)
    record = AsyncMigration.objects.filter(name="0001_example_backfill").first()
    assert record is not None
    assert record.status in [AsyncMigration.STATUS_PENDING, AsyncMigration.STATUS_COMPLETED]


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_run_async_migration_sync_helper():
    """Test run_async_migration_sync helper function."""
    from app.async_migrations.base import run_async_migration_sync

    await User.objects.acreate(username="sync_user", email="sync@example.com", bio="")
    record = run_async_migration_sync("0001_example_backfill")
    assert record.status == AsyncMigration.STATUS_COMPLETED


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_async_migration_dependencies():
    """Test that missing dependencies defer execution safely."""

    @register_async_migration
    class DependentMigration(BaseAsyncMigration):
        name = "test_dependent_migration"
        description = "Requires unapplied Django migration"
        depends_on_django_migration = "app.9999_nonexistent_migration"

        async def get_total_count(self) -> int:
            return 10

        async def process_batch(self, offset: int, limit: int) -> int:
            return 10

    instance = DependentMigration()
    record = await instance.run()

    assert record.status == AsyncMigration.STATUS_DEFERRED
    assert "9999_nonexistent_migration" in record.error_message


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_worker_code_readiness_guard():
    """Test worker code readiness guard when worker encounters unknown migration."""
    result = await run_async_migration_task(None, "9999_future_migration_not_yet_in_code")
    assert result["status"] == "deferred"
    assert "older code version" in result["message"]
