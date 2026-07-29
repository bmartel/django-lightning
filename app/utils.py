"""General application utility functions and high-performance database helpers."""

from collections.abc import AsyncGenerator, Sequence
from typing import Any

from django.db.models import Model, QuerySet


async def akeyset_chunker[T: Model](
    queryset: QuerySet[T],
    chunk_size: int = 2000,
    pk_field: str = "id",
    use_values: bool = True,
    fields: Sequence[str] | None = None,
) -> AsyncGenerator[list[dict[str, Any]] | list[T], None]:
    """Yields chunks of records from a Django QuerySet using indexed keyset pagination.

    Designed for processing massive datasets (1M+ records) with flat memory usage,
    no SQL OFFSET performance degradation, and 100% PgBouncer Transaction Mode safety.

    Args:
        queryset: Base Django QuerySet.
        chunk_size: Number of records per chunk/batch.
        pk_field: Primary key field name used for keyset comparison (default: "id").
        use_values: If True, returns lightweight raw dicts (80%+ lower RAM footprint).
        fields: Specific field names to select when use_values is True (None selects all).

    Yields:
        Lists of raw dicts (if use_values=True) or lists of Model instances.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer greater than 0")

    last_pk: Any = None
    gt_filter = f"{pk_field}__gt"

    base_qs: Any = queryset.order_by(pk_field)
    if use_values:
        if fields:
            base_qs = base_qs.values(*fields)
        else:
            base_qs = base_qs.values()

    while True:
        chunk_qs = base_qs
        if last_pk is not None:
            chunk_qs = chunk_qs.filter(**{gt_filter: last_pk})

        chunk_qs = chunk_qs[:chunk_size]
        items = [item async for item in chunk_qs]
        if not items:
            break

        yield items

        last_item = items[-1]
        if isinstance(last_item, dict):
            last_pk = last_item[pk_field]
        else:
            last_pk = getattr(last_item, pk_field)
