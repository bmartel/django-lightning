"""
Base Environment Settings Engine & Type-Coercion Machinery.

Provides high-performance msgspec.Struct base class, introspective field resolution,
and automatic string-to-type coercion for environment variable parsing.
"""

from __future__ import annotations

import os
import typing
from pathlib import Path
from typing import Any

import msgspec


def _parse_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return bool(val)
    if isinstance(val, str):
        return val.strip().lower() in ("1", "true", "yes", "on", "t")
    return False


def _parse_csv_list(val: Any) -> list[str]:
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    if isinstance(val, str):
        return [item.strip() for item in val.split(",") if item.strip()]
    return []


def _coerce_field_val(val: Any, target_type: Any) -> Any:
    """Coerce raw string/env inputs into target field type based on msgspec field type hints."""
    if val is None:
        return None

    origin = typing.get_origin(target_type) or target_type

    if origin is bool or target_type is bool:
        return _parse_bool(val)
    if origin is list or target_type is list:
        return _parse_csv_list(val)
    if origin is int or target_type is int:
        try:
            return int(val)
        except (ValueError, TypeError):
            return val
    if origin is float or target_type is float:
        try:
            return float(val)
        except (ValueError, TypeError):
            return val
    if origin is str or target_type is str:
        return str(val)

    return val


class BaseEnvSettings(msgspec.Struct, kw_only=True):
    """
    Base environment settings machinery powered by msgspec.Struct.

    Provides automatic type coercion, introspective field discovery, and .env file resolution.
    Subclasses inherit all parsing machinery and simply define declared setting fields.
    """

    @classmethod
    def load_from_env[T: BaseEnvSettings](
        cls: type[T],
        env_dict: dict[str, str] | None = None,
        dotenv_path: str | Path | None = None,
        base_dir: Path | None = None,
    ) -> T:
        """
        Load, coerce, and validate environment configuration into a type-safe settings struct.

        Automatically introspects declared struct fields for zero-boilerplate expansion.
        """
        source = dict(os.environ) if env_dict is None else dict(env_dict)

        # 1. Parse optional .env file if present
        if dotenv_path is None and base_dir is not None:
            dotenv_path = base_dir / ".env"

        if dotenv_path and Path(dotenv_path).is_file():
            try:
                for line in Path(dotenv_path).read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k not in source:
                        source[k] = v
            except Exception:
                pass

        # 2. Declaratively introspect fields and coerce values
        data: dict[str, Any] = {}
        fields = msgspec.structs.fields(cls)

        for f in fields:
            name = f.name
            target_type = f.type

            if name in source:
                data[name] = _coerce_field_val(source[name], target_type)
            elif name == "DATABASE_URL" and base_dir:
                data[name] = f"sqlite:///{base_dir / 'db.sqlite3'}"

        # 3. Apply critical domain invariants & default overrides
        if "DEBUG" in data:
            raw_debug = _parse_bool(data["DEBUG"])
        else:
            raw_debug = _parse_bool(source.get("DEBUG", "1"))
        data["DEBUG"] = raw_debug

        # MCP server is strictly gated by DEBUG (must be False in production)
        data["ENABLE_MCP_SERVER"] = raw_debug and _parse_bool(source.get("ENABLE_MCP_SERVER", "1"))

        # Redis cache requires both USE_REDIS_CACHE=True and a non-empty REDIS_URL
        redis_url = data.get("REDIS_URL", source.get("REDIS_URL", "redis://localhost:6379/0"))
        data["USE_REDIS_CACHE"] = bool(
            _parse_bool(data.get("USE_REDIS_CACHE", source.get("USE_REDIS_CACHE", "0")))
            and str(redis_url).strip()
        )

        if "ALLOWED_HOSTS" not in data or not data["ALLOWED_HOSTS"]:
            data["ALLOWED_HOSTS"] = ["*"]

        return msgspec.convert(data, cls)
