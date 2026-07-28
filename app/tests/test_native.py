import pytest

from app.native import get_rust_core_version, is_rust_available, run_native


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
