"""
Application Environment Configuration.

Defines all type-safe environment settings fields for the project.
Inherits environment resolution and type-coercion machinery from BaseEnvSettings.
"""

from __future__ import annotations

import msgspec

from app.env import BaseEnvSettings


class EnvSettings(BaseEnvSettings, kw_only=True):
    """
    Project environment configuration struct.

    To add new environment settings as your project grows, simply add typed fields below.
    """

    SECRET_KEY: str = "django-insecure-change-this-secret-key-in-production-1234567890!"
    DEBUG: bool = True
    ENABLE_MCP_SERVER: bool = True
    ALLOWED_HOSTS: list[str] = msgspec.field(default_factory=lambda: ["*"])
    DATABASE_URL: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_REDIS_CACHE: bool = False
    CORS_ALLOWED_ORIGINS: list[str] = msgspec.field(default_factory=list)
    PORT: int = 8000
    HOST: str = "0.0.0.0"
