from typing import Any

from bolt_mcp import MCP
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model

from app.middleware import LATENCY_TRACKER
from app.models import AsyncMigration
from app.profiling import QueryScalabilityProfiler
from app.tasks import queue

User = get_user_model()


def setup_mcp_server(api):
    if not getattr(settings, "ENABLE_MCP_SERVER", False):
        return None

    mcp = MCP("django-lightning-mcp", "1.0.0")

    @mcp.tool(
        name="count_users",
        description="Return total count of registered users in the database using Django async ORM",
    )
    async def count_users() -> dict[str, Any]:
        count = await User.objects.acount()
        return {"count": count}

    @mcp.tool(
        name="inspect_db_schema",
        description=(
            "Introspect installed Django models, database tables, fields, types, and indexes."
        ),
    )
    async def inspect_db_schema() -> dict[str, Any]:

        models_info = []
        for model in apps.get_models():
            opts = model._meta
            if opts.app_label in ("admin", "auth", "contenttypes", "sessions"):
                continue

            fields = []
            for field in opts.get_fields():
                if field.is_relation and field.many_to_many:
                    continue
                fields.append(
                    {
                        "name": field.name,
                        "type": field.get_internal_type()
                        if hasattr(field, "get_internal_type")
                        else "Unknown",
                        "primary_key": getattr(field, "primary_key", False),
                        "db_index": getattr(field, "db_index", False),
                        "nullable": getattr(field, "null", False),
                    }
                )

            indexes = [{"name": idx.name, "fields": idx.fields} for idx in opts.indexes]

            models_info.append(
                {
                    "app_label": opts.app_label,
                    "model_name": opts.model_name,
                    "db_table": opts.db_table,
                    "fields": fields,
                    "indexes": indexes,
                }
            )

        return {"models": models_info}

    @mcp.tool(
        name="run_query_explain",
        description=(
            "Run query execution plan analysis (EXPLAIN) on a raw SQL string to detect unindexed "
            "table scans or unindexed sorts."
        ),
    )
    async def run_query_explain(sql: str) -> dict[str, Any]:
        report = QueryScalabilityProfiler._analyze_generic(sql, (), False)
        return {
            "is_scalable": report.is_scalable,
            "detected_issues": report.detected_issues,
            "suggested_fixes": report.suggested_fixes,
            "sql_query": report.sql_query,
        }

    @mcp.tool(
        name="get_async_migration_status",
        description=(
            "Query registered 2-phase background AsyncMigration progress and status records."
        ),
    )
    async def get_async_migration_status() -> dict[str, Any]:
        migrations = []
        async for m in AsyncMigration.objects.all():
            migrations.append(
                {
                    "id": m.id,
                    "name": m.name,
                    "status": m.status,
                    "processed_count": m.processed_count,
                    "total_count": m.total_count,
                    "error_message": m.error_message,
                    "started_at": m.started_at.isoformat() if m.started_at else None,
                    "completed_at": m.completed_at.isoformat() if m.completed_at else None,
                }
            )
        return {"migrations": migrations}

    @mcp.tool(
        name="enqueue_saq_job",
        description="Enqueue a background SAQ worker job by function name.",
    )
    async def enqueue_saq_job(
        function_name: str, kwargs: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        job_kwargs = kwargs or {}
        job = await queue.enqueue(function_name, **job_kwargs)
        return {
            "status": "enqueued",
            "job_id": job.id if job else None,
            "function": function_name,
            "kwargs": job_kwargs,
        }

    @mcp.tool(
        name="get_latency_metrics",
        description=(
            "Retrieve real-time API request latency telemetry and performance budget "
            "compliance statistics."
        ),
    )
    async def get_latency_metrics() -> dict[str, Any]:
        return LATENCY_TRACKER.get_stats()

    @mcp.resource("config://app-info", name="app-info", mime_type="application/json")
    async def app_info() -> str:
        return '{"app": "django-lightning", "framework": "django-bolt", "mcp": "streamable-http"}'

    @mcp.prompt
    async def welcome_user(username: str) -> str:
        """Prompt generating a personalized welcome message for a user."""
        return f"Write a warm 2-sentence welcome message for a new user named '{username}'."

    api.mount_mcp(mcp)
    return mcp
