import msgspec
from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.db import connection
from django_bolt import BoltAPI


class HealthCheckOut(msgspec.Struct):
    status: str
    database: str
    cache: str
    version: str = "0.1.0"


def _ping_db() -> None:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()


def register_health_routes(api: BoltAPI):
    @api.get(
        "/health",
        response_model=HealthCheckOut,
        tags=["Health"],
        summary="Health check endpoint",
        description="Verify service availability, database connectivity, and cache readiness.",
    )
    async def health_check():
        db_ok = True
        try:
            # Cheap connectivity probe (SELECT 1) — never scans a table, so the check
            # stays O(1) regardless of how many rows the database holds.
            await sync_to_async(_ping_db)()
        except Exception:
            db_ok = False

        cache_ok = True
        try:
            await cache.aset("health_ping", "ok", timeout=5)
        except Exception:
            cache_ok = False

        overall_status = "ok" if (db_ok and cache_ok) else ("degraded" if db_ok else "down")

        return {
            "status": overall_status,
            "database": "connected" if db_ok else "disconnected",
            "cache": "connected" if cache_ok else "disconnected",
            "version": "0.1.0",
        }
