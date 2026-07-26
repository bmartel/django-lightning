import pytest
from django.contrib.auth import get_user_model

from app.utils import akeyset_chunker

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_akeyset_chunker_basic_dict_chunks():
    # Create 5 test users
    for i in range(1, 6):
        await User.objects.acreate(
            username=f"user_{i}",
            email=f"user_{i}@example.com",
        )

    # Chunk with batch size 2 (expecting chunks of 2, 2, 1)
    chunks = []
    qs = User.objects.filter(username__startswith="user_")
    async for chunk in akeyset_chunker(qs, chunk_size=2):
        chunks.append(chunk)

    assert len(chunks) == 3
    assert len(chunks[0]) == 2
    assert len(chunks[1]) == 2
    assert len(chunks[2]) == 1

    # Check dict structure
    assert isinstance(chunks[0][0], dict)
    assert chunks[0][0]["username"] == "user_1"
    assert chunks[2][0]["username"] == "user_5"


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_akeyset_chunker_model_instances():
    await User.objects.acreate(username="model_user_1", email="m1@example.com")
    await User.objects.acreate(username="model_user_2", email="m2@example.com")

    chunks = []
    async for chunk in akeyset_chunker(
        User.objects.filter(username__startswith="model_user_"),
        chunk_size=1,
        use_values=False,
    ):
        chunks.append(chunk)

    assert len(chunks) == 2
    assert isinstance(chunks[0][0], User)
    assert chunks[0][0].username == "model_user_1"
    assert chunks[1][0].username == "model_user_2"


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_akeyset_chunker_specific_fields():
    await User.objects.acreate(username="field_user", email="field@example.com")

    chunks = []
    async for chunk in akeyset_chunker(
        User.objects.filter(username="field_user"),
        chunk_size=10,
        fields=["id", "username"],
    ):
        chunks.append(chunk)

    assert len(chunks) == 1
    assert set(chunks[0][0].keys()) == {"id", "username"}


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_akeyset_chunker_empty_queryset():
    chunks = []
    async for chunk in akeyset_chunker(
        User.objects.filter(username="non_existent_user_xyz"),
        chunk_size=10,
    ):
        chunks.append(chunk)

    assert len(chunks) == 0


@pytest.mark.asyncio
async def test_akeyset_chunker_invalid_chunk_size():
    with pytest.raises(ValueError, match="chunk_size must be a positive integer"):
        async for _ in akeyset_chunker(User.objects.all(), chunk_size=0):
            pass
