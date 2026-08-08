"""Tests for the native Rust fast-path collection endpoints and tooling."""

import msgspec
import pytest
from django.contrib.auth import get_user_model
from django_bolt import BoltAPI
from django_bolt.testing import TestClient

from app.auth import create_token
from app.native import (
    db_registered_models,
    is_rust_available,
    native_db_url,
    raw_json_response,
)
from app.routes.native import register_native_collection, register_native_routes

User = get_user_model()


def test_native_db_url_sqlite(settings):
    settings.DATABASES = {
        "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "/tmp/db.sqlite3"}
    }
    assert native_db_url() == "sqlite:///tmp/db.sqlite3"


def test_native_db_url_postgres(settings):
    settings.DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "appdb",
            "USER": "app",
            "PASSWORD": "p@ss/word",
            "HOST": "db.internal",
            "PORT": 5433,
        }
    }
    assert native_db_url() == "postgres://app:p%40ss%2Fword@db.internal:5433/appdb"


def test_raw_json_response_zero_reserialization():
    raw = b'[{"id":1,"username":"bolt"}]'
    resp = raw_json_response(raw)
    assert resp.to_bytes() == raw
    assert resp.headers["content-type"] == "application/json"


def test_db_registered_models_contains_generated_models():
    if not is_rust_available():
        pytest.skip("rust_core module not compiled")
    models = db_registered_models()
    assert "user" in models
    assert "tenant" in models


@pytest.mark.django_db(transaction=True)
def test_native_collection_requires_auth():
    if not is_rust_available():
        pytest.skip("rust_core module not compiled")

    api = BoltAPI()
    register_native_routes(api)
    client = TestClient(api)

    resp = client.get("/api/native/users")
    assert resp.status_code == 401


@pytest.mark.django_db(transaction=True)
def test_native_collection_lists_users_without_sensitive_fields():
    if not is_rust_available():
        pytest.skip("rust_core module not compiled")

    from django.conf import settings as dj_settings

    db_name = str(dj_settings.DATABASES["default"]["NAME"])
    if db_name == ":memory:" or "memory" in db_name:
        pytest.skip("In-memory SQLite test DB is not shared with native threads")

    user = User.objects.create_user(
        username="native_route_user", password="password123", email="native@example.com"
    )
    token = create_token(user)

    api = BoltAPI()
    register_native_routes(api)
    client = TestClient(api)

    resp = client.get(
        "/api/native/users", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/json")

    rows = msgspec.json.decode(resp.content)
    usernames = {row["username"] for row in rows}
    assert "native_route_user" in usernames
    for row in rows:
        assert "password" not in row


@pytest.mark.django_db(transaction=True)
def test_native_collection_keyset_pagination():
    if not is_rust_available():
        pytest.skip("rust_core module not compiled")

    from django.conf import settings as dj_settings

    db_name = str(dj_settings.DATABASES["default"]["NAME"])
    if db_name == ":memory:" or "memory" in db_name:
        pytest.skip("In-memory SQLite test DB is not shared with native threads")

    users = [
        User.objects.create_user(username=f"keyset_user_{i}", password="password123")
        for i in range(3)
    ]
    token = create_token(users[0])

    api = BoltAPI()
    register_native_collection(api, "/api/native/keyset-users", "user")
    client = TestClient(api)
    headers = {"Authorization": f"Bearer {token}"}

    first = msgspec.json.decode(
        client.get("/api/native/keyset-users?limit=2", headers=headers).content
    )
    assert len(first) == 2

    after_id = first[-1]["id"]
    second = msgspec.json.decode(
        client.get(
            f"/api/native/keyset-users?limit=2&after_id={after_id}", headers=headers
        ).content
    )
    assert all(row["id"] > after_id for row in second)
