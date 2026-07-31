import uuid

from django.db import models

from app.fields import UUID7Field, gen_uuid7


class DummyUUID7Model(models.Model):
    id = UUID7Field(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "app"


def test_gen_uuid7_generator():
    val1 = gen_uuid7()
    val2 = gen_uuid7()
    assert isinstance(val1, uuid.UUID)
    assert isinstance(val2, uuid.UUID)
    assert val1.version == 7
    assert val2.version == 7


def test_gen_uuid7_pure_python_fallback_path(monkeypatch):
    if hasattr(uuid, "uuid7"):
        monkeypatch.delattr(uuid, "uuid7")
    val1 = gen_uuid7()
    val2 = gen_uuid7()
    assert isinstance(val1, uuid.UUID)
    assert isinstance(val2, uuid.UUID)
    assert val1.version == 7
    assert val2.version == 7


def test_uuid7_field_instantiation():
    field = UUID7Field(primary_key=True)
    assert field.primary_key is True
    assert field.editable is False
    assert callable(field.default)
    generated_val = field.default()
    assert isinstance(generated_val, uuid.UUID)
    assert generated_val.version == 7
