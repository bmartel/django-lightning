import pytest

from app.storage import AsyncStorageEngine


@pytest.mark.asyncio
async def test_async_storage_operations(tmp_path):
    engine = AsyncStorageEngine(media_root=tmp_path)

    # Store file
    res = await engine.astore_file("test.txt", b"Hello lightning storage")
    assert res["filename"] == "test.txt"
    assert res["size_bytes"] == 23

    # Generate presigned URL
    url = await engine.agenerate_presigned_url("test.txt")
    assert "presigned/upload/test.txt" in url

    # Delete file
    deleted = await engine.adelete_file("test.txt")
    assert deleted is True
