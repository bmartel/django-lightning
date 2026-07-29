from django_bolt import BoltAPI
from django_bolt.param_functions import Query

from app.schemas.article import ArticleCreate, ArticleOut


def register_article_routes(api: BoltAPI):
    @api.get(
        "/api/articles",
        response_model=list[ArticleOut],
        tags=["Article"],
        summary="List articles",
    )
    async def list_articles(limit: int = Query(default=20, ge=1, le=100)):
        # Placeholder endpoint logic - replace with model QuerySet when model is migrated
        return []

    @api.post(
        "/api/articles",
        response_model=ArticleOut,
        status_code=201,
        tags=["Article"],
        summary="Create new article",
    )
    async def create_article(payload: ArticleCreate):
        # Placeholder endpoint logic
        data = {"id": 1}
        for field in payload.__struct_fields__:
            data[field] = getattr(payload, field)
        return data

    @api.get(
        "/api/native/version",
        tags=["Native Rust"],
        summary="Get PyO3 Rust extension version",
    )
    async def get_native_version():
        from app.native import get_rust_core_version, is_rust_available

        return {
            "rust_available": is_rust_available(),
            "version": get_rust_core_version(),
        }
