"""High-Performance Async Caching Layer for Django-Bolt applications.

Provides ultra-fast async response caching decorators (@cache_response) powered by
Django's async cache backend (Redis / In-Memory) and msgspec binary JSON serialization.
"""

from __future__ import annotations

import functools
import hashlib
from collections.abc import Callable
from typing import Any

import msgspec
from django.core.cache import cache
from django_bolt import Request


def generate_cache_key(
    prefix: str,
    func_name: str,
    args: tuple,
    kwargs: dict[str, Any],
) -> str:
    """Generate a unique cache key based on function name, parameters, and query args."""
    key_parts = [prefix, func_name]

    # Inspect request object if present in args/kwargs
    request_obj = None
    for arg in args:
        if isinstance(arg, Request):
            request_obj = arg
            break
    if not request_obj:
        for val in kwargs.values():
            if isinstance(val, Request):
                request_obj = val
                break

    if request_obj:
        key_parts.append(request_obj.method)
        key_parts.append(request_obj.path)
        if request_obj.query_params:
            sorted_params = sorted(request_obj.query_params.items())
            key_parts.append(str(sorted_params))

    # Hash extra args/kwargs
    clean_kwargs = {k: v for k, v in kwargs.items() if not isinstance(v, Request)}
    if clean_kwargs or args:
        payload_hash = hashlib.sha256(
            str((args, sorted(clean_kwargs.items()))).encode()
        ).hexdigest()[:12]
        key_parts.append(payload_hash)

    return ":".join(key_parts)


def cache_response(
    ttl: int = 60,
    key_prefix: str = "bolt_cache",
    key_builder: Callable[..., str] | None = None,
):
    """Decorator for caching async django-bolt endpoint handler responses.

    Serializes responses via msgspec for zero-overhead JSON memory caching.

    Args:
        ttl: Time-To-Live in seconds (default 60s).
        key_prefix: Prefix string for generated cache keys.
        key_builder: Optional custom function to construct cache keys.

    Usage:
        @api.get("/api/products")
        @cache_response(ttl=300, key_prefix="products_list")
        async def list_products():
            return {"products": [...]}
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = generate_cache_key(key_prefix, func.__name__, args, kwargs)

            # Attempt cache lookup
            try:
                cached_bytes = await cache.aget(cache_key)
                if cached_bytes is not None:
                    if isinstance(cached_bytes, bytes):
                        return msgspec.json.decode(cached_bytes)
                    return cached_bytes
            except Exception:
                pass  # Fallback to direct execution on cache backend error

            # Execute underlying async handler
            result = await func(*args, **kwargs)

            # Store result in cache
            try:
                encoded_bytes = msgspec.json.encode(result)
                await cache.aset(cache_key, encoded_bytes, timeout=ttl)
            except Exception:
                pass

            return result

        return wrapper

    return decorator


async def ainvalidate_cache_key(cache_key: str) -> bool:
    """Async helper to invalidate a specific cache key."""
    try:
        await cache.adelete(cache_key)
        return True
    except Exception:
        return False
