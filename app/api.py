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
from app.routes.realtime import register_realtime_routes

# Initialize high-performance BoltAPI instance
api = BoltAPI(
    prefix="",
    trailing_slash="strip",
    validate_response=True,
    compression=CompressionConfig(),
    enable_logging=True,
    middleware=[
        LatencyBudgetMiddleware,
        TimingMiddleware,
        LoggingMiddleware,
    ],
    openapi_config=OpenAPIConfig(
        title="Django Lightning API",
        version="1.0.0",
        description=(
            "High-performance Django-Bolt API with WebSockets, SSE, and MCP server capabilities"
        ),
        path="/docs",
        render_plugins=[ScalarRenderPlugin()],
        enabled=True,
    ),
)

# Register route modules
register_health_routes(api)
register_auth_routes(api)
register_realtime_routes(api)

# Mount MCP (Model Context Protocol) Server at /mcp
setup_mcp_server(api)
