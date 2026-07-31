import uuid

from django.db import models

from app.fields import UUID7Field, gen_uuid7


class DummyUUID7Model(models.Model):
    id = UUID7Field(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "app"


def test_gen_uuid7_generator():
    val = gen_uuid7()
    assert isinstance(val, uuid.UUID)
    assert val.version == 7


def test_uuid7_field_instantiation():
    field = UUID7Field(primary_key=True)
    assert field.primary_key is True
    assert field.editable is False
    assert callable(field.default)
