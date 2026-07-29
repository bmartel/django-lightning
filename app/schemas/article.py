import msgspec


class ArticleCreate(msgspec.Struct):
    title: str
    content: str
    published: bool


class ArticleUpdateIn(msgspec.Struct):
    title: str | None = None
    content: str | None = None
    published: bool | None = None


class ArticleOut(msgspec.Struct):
    id: int
    title: str
    content: str
    published: bool
