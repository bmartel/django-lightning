import pytest

from app.cache import ainvalidate_cache_key, cache_response, generate_cache_key


@pytest.mark.asyncio
async def test_generate_cache_key():
    key1 = generate_cache_key("test", "my_func", (), {"a": 1, "b": "hello"})
    key2 = generate_cache_key("test", "my_func", (), {"b": "hello", "a": 1})
    assert key1 == key2
    assert key1.startswith("test:my_func:")


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_cache_response_decorator():
    call_count = 0

    @cache_response(ttl=60, key_prefix="test_counter")
    async def get_data(category_id: int):
        nonlocal call_count
        call_count += 1
        return {"category_id": category_id, "count": call_count}

    # First call: cache miss
    res1 = await get_data(category_id=42)
    assert res1 == {"category_id": 42, "count": 1}
    assert call_count == 1

    # Second call with same parameter: cache hit!
    res2 = await get_data(category_id=42)
    assert res2 == {"category_id": 42, "count": 1}
    assert call_count == 1  # Function not executed again

    # Call with different parameter: cache miss
    res3 = await get_data(category_id=99)
    assert res3 == {"category_id": 99, "count": 2}
    assert call_count == 2


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_cache_invalidation():
    custom_key = "custom_product_key_123"

    @cache_response(ttl=300, key_builder=lambda id: f"custom_product_key_{id}")
    async def fetch_product(id: int):
        return {"id": id, "name": "Lightning Widget"}

    # Populate cache
    val1 = await fetch_product(123)
    assert val1["name"] == "Lightning Widget"

    # Invalidate cache
    success = await ainvalidate_cache_key(custom_key)
    assert success is True
