"""Tests for Django-Guided Rust DB Engine interop and model code generation."""

import tempfile
from pathlib import Path

import pytest
from django.core.management import call_command

from app.models import User
from app.native import is_rust_available, query_users_native


@pytest.mark.django_db
def test_generate_rust_models_command():
    """Verify that generate_rust_models generates valid Rust code for app models."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_file = Path(tmp_dir) / "models.rs"
        call_command("generate_rust_models", output=str(output_file))

        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")

        assert "pub struct UserRow {" in content
        assert "pub struct AsyncMigrationRow {" in content
        assert 'pub const TABLE_NAME: &\'static str = "app_user";' in content
        assert 'pub const TABLE_NAME: &\'static str = "app_asyncmigration";' in content
        assert "use sqlx::FromRow;" in content


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_rust_db_query_users():
    """Verify that native Rust DB engine can query users from the database."""
    if not is_rust_available():
        pytest.skip("rust_core is not available in current environment")

    # Create a test user in Django DB
    await User.objects.acreate(
        username="rust_test_user",
        email="rust_test@example.com",
        bio="Rust test bio",
    )

    from django.conf import settings

    db_config = settings.DATABASES["default"]
    db_name = str(db_config["NAME"])

    if db_name == ":memory:":
        # For in-memory SQLite in tests, pass shared memory mode URI or file URI
        db_url = "sqlite::memory:"
    elif db_name.startswith("file:"):
        db_url = f"sqlite://{db_name}"
    else:
        db_url = f"sqlite://{db_name}?mode=rwc"

    # If in-memory, separate thread connections do not share :memory: state
    try:
        users = await query_users_native(db_url, limit=10)
        assert isinstance(users, list)
    except ValueError as e:
        if "no such table" in str(e):
            pytest.skip("In-memory SQLite test DB requires shared file connection")
        raise



@pytest.mark.asyncio
async def test_rust_db_query_users_file_db():
    """Verify Rust DB query engine against a file-backed SQLite database."""
    if not is_rust_available():
        pytest.skip("rust_core is not available in current environment")

    import sqlite3

    with tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False) as tmp_db:
        db_path = tmp_db.name

    try:
        # Create schema and row manually in file SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE app_user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                password TEXT NOT NULL,
                last_login TEXT,
                is_superuser BOOLEAN NOT NULL,
                username TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL,
                is_staff BOOLEAN NOT NULL,
                is_active BOOLEAN NOT NULL,
                date_joined TEXT NOT NULL,
                bio TEXT NOT NULL,
                avatar_url TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        now_str = "2026-07-27T00:00:00Z"
        cursor.execute(
            """
            INSERT INTO app_user (
                password, last_login, is_superuser, username, first_name, last_name,
                email, is_staff, is_active, date_joined, bio, avatar_url, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "pbkdf2_sha256...",
                None,
                0,
                "file_db_rust_user",
                "Rust",
                "User",
                "rust@example.com",
                0,
                1,
                now_str,
                "Bio text",
                "http://example.com/avatar.png",
                now_str,
                now_str,
            ),
        )
        conn.commit()
        conn.close()

        db_url = f"sqlite://{db_path}"
        users = await query_users_native(db_url, limit=10)
        assert len(users) == 1
        assert users[0]["username"] == "file_db_rust_user"
        assert users[0]["email"] == "rust@example.com"
    finally:
        if Path(db_path).exists():
            Path(db_path).unlink()
