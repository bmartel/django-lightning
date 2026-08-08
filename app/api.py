from django.conf import settings
from django_bolt import (
    BoltAPI,
    CompressionConfig,
    LoggingMiddleware,
    OpenAPIConfig,
    ScalarRenderPlugin,
    TimingMiddleware,
)

from app.middleware import LatencyBudgetMiddleware
from app.routes.auth import register_auth_routes
from app.routes.health import register_health_routes
from app.routes.mcp_server import setup_mcp_server
from app.routes.native import register_native_routes
from app.routes.realtime import register_realtime_routes
from app.routes.tenants import register_tenant_routes

DEBUG = getattr(settings, "DEBUG", False)

# Initialize high-performance BoltAPI instance.
# Response validation and verbose timing/logging middleware are development
# diagnostics: they add per-request cost, so they are enabled only in DEBUG.
api = BoltAPI(
    prefix="",
    trailing_slash="strip",
    validate_response=DEBUG,
    compression=CompressionConfig(),
    enable_logging=DEBUG,
    middleware=[
        LatencyBudgetMiddleware,
        *([TimingMiddleware, LoggingMiddleware] if DEBUG else []),
    ],
    openapi_config=OpenAPIConfig(
        title="Django Lightning API",
        version="1.0.0",
        description=(
            "High-performance Django-Bolt API with WebSockets, SSE, MCP server, "
            "and Native Rust interop"
        ),
        path="/docs",
        render_plugins=[ScalarRenderPlugin()],
        enabled=getattr(settings, "DEBUG", False),
    ),
)

# Register route modules
register_health_routes(api)
register_auth_routes(api)
register_tenant_routes(api)
register_realtime_routes(api)
register_native_routes(api)


# Mount MCP (Model Context Protocol) Server at /mcp ONLY in development (DEBUG=True)
if getattr(settings, "ENABLE_MCP_SERVER", False):
    setup_mcp_server(api)
