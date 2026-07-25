import msgspec
from django_bolt.serializers import Serializer, field_validator


class LoginIn(msgspec.Struct):
    username: str
    password: str


class TokenOut(msgspec.Struct):
    access_token: str
    token_type: str = "bearer"


class UserOut(msgspec.Struct):
    id: int
    username: str
    email: str
    bio: str = ""
    avatar_url: str = ""
    is_staff: bool = False


class UserUpdateIn(msgspec.Struct):
    bio: str | None = None
    avatar_url: str | None = None


class UserCreate(Serializer):
    username: str
    email: str
    password: str
    bio: str = ""
    avatar_url: str = ""

    @classmethod
    @field_validator("email")
    def validate_email(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("Invalid email address format")
        return value.lower().strip()

    @classmethod
    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value
