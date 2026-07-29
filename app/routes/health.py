import msgspec
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django_bolt import BoltAPI

User = get_user_model()


class HealthCheckOut(msgspec.Struct):
    status: str
    database: str
    cache: str
    version: str = "0.1.0"


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
            await User.objects.acount()
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
