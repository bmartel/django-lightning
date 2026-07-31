"""Django Management Command to scaffold new high-performance Bolt async resources.

Generates msgspec Struct schemas, async CRUD route handlers, and scalability pytest suites.

Usage:
    uv run manage.py generate_resource Product --fields "name:str,price:float,in_stock:bool"
"""

import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError


def camel_to_snake(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


class Command(BaseCommand):
    help = "Scaffold a new Django-Bolt async API resource (schemas, routes, and tests)"

    def add_arguments(self, parser):
        parser.add_argument(
            "resource_name", help="Resource name in PascalCase (e.g. Product, Project)"
        )
        parser.add_argument(
            "--fields",
            type=str,
            default="name:str,description:str,is_active:bool",
            help=(
                "Comma-separated field definitions in name:type format "
                "(default: 'name:str,description:str,is_active:bool')"
            ),
        )

    def handle(self, *args, **options):
        resource_name = options["resource_name"].strip()
        fields_str = options["fields"].strip()

        if not resource_name.isalnum():
            raise CommandError("Resource name must be alphanumeric PascalCase (e.g. Product).")

        snake_name = camel_to_snake(resource_name)
        fields = []
        for pair in fields_str.split(","):
            if ":" in pair:
                fname, ftype = pair.split(":", 1)
                fields.append((fname.strip(), ftype.strip()))
            else:
                fields.append((pair.strip(), "str"))

        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        app_dir = base_dir / "app"

        schemas_dir = app_dir / "schemas"
        routes_dir = app_dir / "routes"
        tests_dir = app_dir / "tests"

        schemas_dir.mkdir(parents=True, exist_ok=True)
        routes_dir.mkdir(parents=True, exist_ok=True)
        tests_dir.mkdir(parents=True, exist_ok=True)

        schema_path = schemas_dir / f"{snake_name}.py"
        route_path = routes_dir / f"{snake_name}.py"
        test_path = tests_dir / f"test_{snake_name}.py"

        # 1. Generate msgspec Schemas
        struct_fields = []
        out_fields = ["    id: int"]

        for fname, ftype in fields:
            py_type = "str"
            if ftype in ("int", "integer"):
                py_type = "int"
            elif ftype in ("float", "decimal", "number"):
                py_type = "float"
            elif ftype in ("bool", "boolean"):
                py_type = "bool"

            struct_fields.append(f"    {fname}: {py_type}")
            out_fields.append(f"    {fname}: {py_type}")

        update_fields = []
        for f in struct_fields:
            fname, py_type = f.strip().split(":")
            update_fields.append(f"    {fname.strip()}: {py_type.strip()} | None = None")

        schema_code = f"""import msgspec


class {resource_name}Create(msgspec.Struct):
{"\n".join(struct_fields)}


class {resource_name}UpdateIn(msgspec.Struct):
{"\n".join(update_fields)}


class {resource_name}Out(msgspec.Struct):
{"\n".join(out_fields)}
"""

        schema_path.write_text(schema_code, encoding="utf-8")
        self.stdout.write(
            self.style.SUCCESS(f"  [OK] Created schema: {schema_path.relative_to(base_dir)}")
        )

        # 2. Generate Route Handlers
        route_code = f"""from django_bolt import BoltAPI
from django_bolt.exceptions import HTTPException
from django_bolt.param_functions import Query

from app.schemas.{snake_name} import (
    {resource_name}Create,
    {resource_name}Out,
    {resource_name}UpdateIn,
)




def register_{snake_name}_routes(api: BoltAPI):
    @api.get(
        "/api/{snake_name}s",
        response_model=list[{resource_name}Out],
        tags=["{resource_name}"],
        summary="List {snake_name}s",
    )
    async def list_{snake_name}s(limit: int = Query(default=20, ge=1, le=100)):
        # Placeholder endpoint logic - replace with model QuerySet when model is migrated
        return []

    @api.post(
        "/api/{snake_name}s",
        response_model={resource_name}Out,
        status_code=201,
        tags=["{resource_name}"],
        summary="Create new {snake_name}",
    )
    async def create_{snake_name}(payload: {resource_name}Create):
        # Placeholder endpoint logic
        data = {{"id": 1}}
        for field in payload.__struct_fields__:
            data[field] = getattr(payload, field)
        return data
"""
        route_path.write_text(route_code, encoding="utf-8")
        self.stdout.write(
            self.style.SUCCESS(f"  [OK] Created route handler: {route_path.relative_to(base_dir)}")
        )

        # 3. Generate Unit Test File
        test_code = f"""import pytest
from django_bolt.testing import TestClient
from django_bolt import BoltAPI

from app.routes.{snake_name} import register_{snake_name}_routes


@pytest.fixture
def client():
    api = BoltAPI()
    register_{snake_name}_routes(api)
    return TestClient(api)


def test_list_{snake_name}s(client):
    resp = client.get("/api/{snake_name}s")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
"""
        test_path.write_text(test_code, encoding="utf-8")
        self.stdout.write(
            self.style.SUCCESS(f"  [OK] Created test suite: {test_path.relative_to(base_dir)}")
        )

        self.stdout.write(
            self.style.NOTICE(f"\n[SUCCESS] Resource '{resource_name}' generated successfully!")
        )
        self.stdout.write("Register routes in app/api.py by adding:")
        self.stdout.write(
            self.style.WARNING(
                f"  from app.routes.{snake_name} import register_{snake_name}_routes"
            )
        )
        self.stdout.write(self.style.WARNING(f"  register_{snake_name}_routes(api)"))
