import pytest

from app.models import User
from app.tasks import send_welcome_email


@pytest.mark.asyncio
async def test_send_welcome_email_task(db):
    user = await User.objects.acreate(
        username="taskuser",
        email="taskuser@example.com",
    )
    user.set_password("taskpass123")
    await user.asave()

    result = await send_welcome_email(ctx={}, user_id=user.id)
    assert result["status"] == "success"
    assert result["user_id"] == user.id
    assert result["email"] == "taskuser@example.com"


@pytest.mark.asyncio
async def test_send_welcome_email_nonexistent_user(db):
    result = await send_welcome_email(ctx={}, user_id=99999)
    assert result["status"] == "error"
    assert "not found" in result["message"]
