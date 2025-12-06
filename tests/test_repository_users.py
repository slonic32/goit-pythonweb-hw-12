import pytest

from src.repository.users import UserRepository
from src.schemas import UserCreate
from src.database.models import User


@pytest.mark.asyncio
async def test_create_and_get_user(db_session):
    repo = UserRepository(db_session)

    body = UserCreate(
        username="testuser",
        email="test@example.com",
        password="hashedpass",
        role="user",
    )

    user = await repo.create_user(body, avatar="http://example.com/avatar.png")

    assert isinstance(user, User)
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.avatar is not None

    user_by_id = await repo.get_user_by_id(user.id)
    assert user_by_id is not None
    assert user_by_id.username == "testuser"

    user_by_email = await repo.get_user_by_email("test@example.com")
    assert user_by_email is not None
    assert user_by_email.id == user.id
