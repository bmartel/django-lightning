import msgspec


class TenantCreate(msgspec.Struct):
    name: str
    slug: str


class TenantOut(msgspec.Struct):
    id: int
    name: str
    slug: str
    role: str = "OWNER"
