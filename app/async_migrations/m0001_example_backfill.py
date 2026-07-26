"""Example Async Background Data Migration.

Demonstrates non-blocking data backfills using Django 5 async ORM in configurable batches.
"""

from app.async_migrations.base import BaseAsyncMigration, register_async_migration
from app.models import User


@register_async_migration
class BackfillUserMetadataMigration(BaseAsyncMigration):
    """Backfills default bio or metadata for legacy users asynchronously."""

    name = "0001_example_backfill"
    description = "Backfill default bio and metadata for existing user accounts."
    batch_size = 500

    async def get_total_count(self) -> int:
        """Count total user accounts where bio is empty or default."""
        return await User.objects.filter(bio="").acount()

    async def process_batch(self, offset: int, limit: int) -> int:
        """Fetch a batch of users and update bio asynchronously without locking tables."""
        user_ids = []
        async for user in User.objects.filter(bio="").only("id")[:limit]:
            user_ids.append(user.id)

        if not user_ids:
            return 0

        # Perform atomic batch update asynchronously
        updated_count = await User.objects.filter(id__in=user_ids).aupdate(
            bio="Standard Lightning Account"
        )
        return updated_count
