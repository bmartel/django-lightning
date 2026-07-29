import msgspec


class OrganizationCreate(msgspec.Struct):
    name: str
    slug: str


class OrganizationOut(msgspec.Struct):
    id: int
    name: str
    slug: str
    role: str = "OWNER"
