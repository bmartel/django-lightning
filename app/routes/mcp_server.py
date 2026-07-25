"""
MCP Server integration for django-lightning using bolt-mcp.
Exposes tools, resources, and prompts over Streamable HTTP transport at /mcp.
"""

from bolt_mcp import MCP
from django.contrib.auth import get_user_model

User = get_user_model()


def setup_mcp_server(api):
    mcp = MCP("django-lightning-mcp", "1.0.0")

    @mcp.tool(
        name="count_users",
        description="Return total count of registered users in the database using Django async ORM",
    )
    async def count_users() -> dict:
        count = await User.objects.acount()
        return {"count": count}

    @mcp.resource("config://app-info", name="app-info", mime_type="application/json")
    async def app_info() -> str:
        return '{"app": "django-lightning", "framework": "django-bolt", "mcp": "streamable-http"}'

    @mcp.prompt
    async def welcome_user(username: str) -> str:
        """Prompt generating a personalized welcome message for a user."""
        return f"Write a warm 2-sentence welcome message for a new user named '{username}'."

    api.mount_mcp(mcp)
    return mcp
