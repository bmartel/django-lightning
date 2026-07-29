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
