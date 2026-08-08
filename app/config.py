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

    SECRET_KEY: str = ""
    DEBUG: bool = False
    ENABLE_MCP_SERVER: bool = False
    ALLOWED_HOSTS: list[str] = msgspec.field(default_factory=list)
    DATABASE_URL: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_REDIS_CACHE: bool = False
    CORS_ALLOWED_ORIGINS: list[str] = msgspec.field(default_factory=list)
    CSRF_TRUSTED_ORIGINS: list[str] = msgspec.field(default_factory=list)
    SECURE_SSL_REDIRECT: bool = True
    SECURE_HSTS_SECONDS: int = 3600
    PORT: int = 8000
    HOST: str = "0.0.0.0"
