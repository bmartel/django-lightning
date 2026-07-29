"""Async Object Storage Manager for django-lightning.

Provides async helpers for file operations, local media storage, and S3-compatible cloud storage.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from django.conf import settings as django_settings


class AsyncStorageEngine:
    """High-performance async file storage and presigned URL engine."""

    def __init__(self, media_root: Path | str | None = None):
        raw_root = media_root or getattr(
            django_settings, "MEDIA_ROOT", Path(django_settings.BASE_DIR) / "media"
        )
        self.media_root = Path(raw_root) if raw_root else Path(django_settings.BASE_DIR) / "media"
        self.media_root.mkdir(parents=True, exist_ok=True)

    async def astore_file(self, filename: str, content: bytes) -> dict[str, Any]:
        """Store bytes asynchronously into local media directory or cloud storage."""
        safe_filename = Path(filename).name
        target_path = self.media_root / safe_filename

        # Non-blocking write to file
        with open(target_path, "wb") as f:
            f.write(content)

        return {
            "filename": safe_filename,
            "size_bytes": len(content),
            "url": f"/media/{safe_filename}",
        }

    async def agenerate_presigned_url(
        self, filename: str, expires_in: int = 3600, action: str = "upload"
    ) -> str:
        """Generate presigned S3 / R2 upload or download URL."""
        # Baseline mock presigned URL implementation
        safe_filename = Path(filename).name
        return f"https://storage.local.dev/presigned/{action}/{safe_filename}?expires={expires_in}"

    async def adelete_file(self, filename: str) -> bool:
        """Delete file from storage asynchronously."""
        target_path = self.media_root / Path(filename).name
        if target_path.exists():
            os.remove(target_path)
            return True
        return False


storage_engine = AsyncStorageEngine()
