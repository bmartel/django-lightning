"""
Native High-Performance UUIDv7 Field for Django + PostgreSQL.

Provides time-ordered, B-Tree index-friendly 128-bit UUIDv7 primary keys natively out of the box.
"""

from __future__ import annotations

import os
import time
import uuid
from typing import Any

from django.db import models


def gen_uuid7() -> uuid.UUID:
    """
    Generate time-ordered UUIDv7
    (standard library in Python 3.13+, Rust extension, or pure Python RFC 9562).
    """
    if hasattr(uuid, "uuid7"):
        return uuid.uuid7()

    try:
        from app.native import is_rust_available

        if is_rust_available():
            from app import rust_core

            if hasattr(rust_core, "generate_uuid7"):
                return uuid.UUID(rust_core.generate_uuid7())
    except Exception:
        pass

    # Pure Python RFC 9562 UUIDv7 generator fallback
    ts_ms = int(time.time() * 1000) & 0xFFFFFFFFFFFF
    rand_a = int.from_bytes(os.urandom(2), "big") & 0x0FFF
    rand_b = int.from_bytes(os.urandom(8), "big") & 0x3FFFFFFFFFFFFFFF
    high = (ts_ms << 16) | (0x7 << 12) | rand_a
    low = (0x2 << 62) | rand_b
    return uuid.UUID(int=(high << 64) | low)


class UUID7Field(models.UUIDField):
    """
    High-performance UUIDv7 field delivering native time-ordered 128-bit keys.

    Prevents B-Tree index fragmentation in PostgreSQL while enabling distributed,
    chronologically sortable primary keys out of the box.
    """

    description = "Time-ordered UUIDv7"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("default", gen_uuid7)
        kwargs.setdefault("editable", False)
        super().__init__(*args, **kwargs)
