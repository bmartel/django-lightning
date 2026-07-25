---
name: django-bolt-schemas-serializers
description: Data validation and serialization in django-bolt using msgspec.Struct and Serializers, field validators, model validators, and read/write rules.
compatibility: Agentic coding assistants building web applications with django-bolt.
metadata:
  category: validation
  tags: [django-bolt, msgspec, serializers, validation, structs]
---

# Django-Bolt Schemas & Serializers

## `msgspec.Struct` vs `Serializer`

| Feature | `msgspec.Struct` | `Serializer` |
| --- | --- | --- |
| Best Used For | Simple input/output DTOs | Complex domain validation & business logic |
| Performance | Ultra-fast C/Rust engine | High speed with custom Python validators |
| Validation | Built-in type checking & Meta constraints | Field validators (`@field_validator`) & model validators (`@model_validator`) |

## Using `msgspec.Struct`

```python
import msgspec
from typing import Annotated


class UserDTO(msgspec.Struct):
    id: int
    username: Annotated[str, msgspec.Meta(min_length=3, max_length=50)]
    email: str
    tags: list[str] = []
```

## Using `django_bolt.serializers.Serializer`

```python
from typing import Annotated
import msgspec
from django_bolt.serializers import Serializer, field_validator, model_validator


class UserCreateSerializer(Serializer):
    username: str
    email: str
    password: Annotated[str, msgspec.Meta(min_length=8)]
    confirm_password: str

    class Config:
        write_only = {"password", "confirm_password"}

    @field_validator("email")
    def validate_email(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("Email must contain '@'")
        return value.lower().strip()

    @model_validator
    def validate_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self
```
