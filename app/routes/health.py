import msgspec
from django.contrib.auth import get_user_model
from django_bolt import BoltAPI

User = get_user_model()


class HealthCheckOut(msgspec.Struct):
    status: str
    database: str
    version: str = "0.1.0"


def register_health_routes(api: BoltAPI):
    @api.get(
        "/health",
        response_model=HealthCheckOut,
        tags=["Health"],
        summary="Health check endpoint",
        description="Verify service availability and database connectivity.",
    )
    async def health_check():
        db_ok = True
        try:
            await User.objects.acount()
        except Exception:
            db_ok = False

        return {
            "status": "ok" if db_ok else "degraded",
            "database": "connected" if db_ok else "disconnected",
            "version": "0.1.0",
        }
