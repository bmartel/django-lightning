"""Native Rust fast-path collection routes.

These endpoints bypass the Django ORM and all Python serialization entirely:
Rust (sqlx + serde) executes the query against a warm connection pool and
returns pre-serialized JSON bytes, which are passed straight through to the
HTTP response body with zero Python re-encoding.

Registering a fast path for any Django model (including models in your own
apps) takes one line once `manage.py generate_rust_models` has been run:

    register_native_collection(api, path="/api/native/orders", model="order")

Sensitive columns (password hashes, key hashes, secrets, tokens) are stripped
at the Rust serialization layer by codegen, so they can never leak from these
endpoints. Endpoints require authentication by default; pass
``require_auth=False`` only for genuinely public datasets.
"""

from django_bolt import BoltAPI, Depends

from app.auth import get_current_user
from app.native import fetch_model_page_response, is_rust_available

DEFAULT_LIMIT = 100
MAX_LIMIT = 1000


def register_native_collection(
    api: BoltAPI,
    path: str,
    model: str,
    *,
    require_auth: bool = True,
    default_limit: int = DEFAULT_LIMIT,
    max_limit: int = MAX_LIMIT,
    tags: list[str] | None = None,
    summary: str | None = None,
) -> None:
    """Register a keyset-paginated, Rust-native JSON collection endpoint.

    Query parameters:
        limit: page size (clamped to ``max_limit``).
        after_id: keyset cursor; returns rows with primary key greater than this.
    """
    route_tags = tags or ["Native"]
    route_summary = summary or f"Native Rust fast-path listing for model '{model}'"

    if require_auth:

        @api.get(path, tags=route_tags, summary=route_summary)
        async def native_collection(
            limit: int = default_limit,
            after_id: int | None = None,
            current_user: dict = Depends(get_current_user),
        ):
            return await fetch_model_page_response(
                model, limit=limit, after_id=after_id, max_limit=max_limit
            )

    else:

        @api.get(path, tags=route_tags, summary=route_summary)
        async def native_collection_public(
            limit: int = default_limit,
            after_id: int | None = None,
        ):
            return await fetch_model_page_response(
                model, limit=limit, after_id=after_id, max_limit=max_limit
            )


def register_native_routes(api: BoltAPI) -> None:
    """Register the default native fast-path collections for this project."""
    if not is_rust_available():
        return

    register_native_collection(api, "/api/native/users", "user")
    register_native_collection(api, "/api/native/tenants", "tenant")
