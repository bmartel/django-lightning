import msgspec
import pytest

from app.native import (
    get_rust_core_version,
    is_rust_available,
    native_async,
    native_json,
    run_native,
)

try:
    from app import rust_core
except ImportError:
    rust_core = None


class SamplePayload(msgspec.Struct):
    name: str
    count: int


@pytest.mark.asyncio
async def test_native_interop_helpers():
    avail = is_rust_available()
    version = get_rust_core_version()

    if avail:
        assert isinstance(version, str)
        assert version == "0.1.0"
    else:
        assert version is None


@pytest.mark.asyncio
async def test_run_native_executor():
    def sample_func(a: int, b: int) -> int:
        return a + b

    result = await run_native(sample_func, 10, 20)
    assert result == 30


@pytest.mark.asyncio
async def test_native_async_decorator():
    def add_numbers(x: int, y: int) -> int:
        return x + y

    async_add = native_async(add_numbers)
    result = await async_add(15, 25)
    assert result == 40


@pytest.mark.asyncio
async def test_native_json_decorator():
    def echo_json_bytes(raw_json: bytes) -> bytes:
        return raw_json

    echo_payload = native_json(echo_json_bytes, response_type=SamplePayload)
    payload = SamplePayload(name="bolt", count=100)

    decoded = await echo_payload(payload)
    assert decoded.name == "bolt"
    assert decoded.count == 100


@pytest.mark.asyncio
async def test_zero_copy_raw_bytes_transfer():
    if not is_rust_available() or rust_core is None:
        pytest.skip("rust_core module not compiled")

    async_process_bytes = native_async(rust_core.process_raw_bytes)
    input_data = b"hello django-lightning native rust"
    output_data = await async_process_bytes(input_data)
    assert output_data == input_data
