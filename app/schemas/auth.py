import re

import msgspec
from django_bolt.serializers import Serializer, field_validator

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
USERNAME_REGEX = re.compile(r"^[\w.@+-]+$")


class LoginIn(Serializer):
    username: str
    password: str

    @field_validator("username")
    def validate_username(self, value: str) -> str:
        clean_val = value.strip()
        if not clean_val:
            raise ValueError("Username cannot be empty")
        return clean_val

    @field_validator("password")
    def validate_password(self, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Password cannot be empty")
        return value


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


class UserUpdateIn(Serializer):
    bio: str | None = None
    avatar_url: str | None = None

    @field_validator("bio")
    def validate_bio(self, value: str | None) -> str | None:
        if value is None:
            return None
        if len(value) > 500:
            raise ValueError("Bio cannot exceed 500 characters")
        return value.strip()

    @field_validator("avatar_url")
    def validate_avatar_url(self, value: str | None) -> str | None:
        if value is None or value.strip() == "":
            return ""
        clean_val = value.strip()
        if not (clean_val.startswith("http://") or clean_val.startswith("https://")):
            raise ValueError("Avatar URL must start with http:// or https://")
        if len(clean_val) > 2048:
            raise ValueError("Avatar URL cannot exceed 2048 characters")
        return clean_val


class UserCreate(Serializer):
    username: str
    email: str
    password: str
    bio: str = ""
    avatar_url: str = ""

    @field_validator("username")
    def validate_username(self, value: str) -> str:
        clean_val = value.strip()
        if not clean_val:
            raise ValueError("Username cannot be empty")
        if len(clean_val) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if len(clean_val) > 150:
            raise ValueError("Username cannot exceed 150 characters")
        if not USERNAME_REGEX.match(clean_val):
            raise ValueError("Username contains invalid characters")
        return clean_val

    @field_validator("email")
    def validate_email(self, value: str) -> str:
        clean_val = value.strip().lower()
        if not clean_val:
            raise ValueError("Email address cannot be empty")
        if not EMAIL_REGEX.match(clean_val):
            raise ValueError("Invalid email address format")
        return clean_val

    @field_validator("password")
    def validate_password(self, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Password cannot be empty or whitespace only")
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if len(value) > 128:
            raise ValueError("Password cannot exceed 128 characters")
        return value

    @field_validator("bio")
    def validate_bio(self, value: str) -> str:
        if len(value) > 500:
            raise ValueError("Bio cannot exceed 500 characters")
        return value.strip()

    @field_validator("avatar_url")
    def validate_avatar_url(self, value: str) -> str:
        if not value or not value.strip():
            return ""
        clean_val = value.strip()
        if not (clean_val.startswith("http://") or clean_val.startswith("https://")):
            raise ValueError("Avatar URL must start with http:// or https://")
        if len(clean_val) > 2048:
            raise ValueError("Avatar URL cannot exceed 2048 characters")
        return clean_val
