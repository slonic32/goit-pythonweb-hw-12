import pytest

from src.repository.contacts import ContactRepository
from src.repository.users import UserRepository
from src.schemas import ContactCreate, UserCreate


@pytest.mark.asyncio
async def test_create_and_get_contact(db_session):
    user_repo = UserRepository(db_session)
    contact_repo = ContactRepository(db_session)

    user_body = UserCreate(
        username="owner",
        email="owner@example.com",
        password="pass",
        role="user",
    )
    user = await user_repo.create_user(user_body)

    contact_body = ContactCreate(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="+123456789",
        birthday="1990-01-01",
        extra_info="Friend",
    )

    contact = await contact_repo.create_contact(user, contact_body)

    assert contact.id is not None
    assert contact.first_name == "John"

    contacts = await contact_repo.get_contacts(user=user)
    assert len(contacts) == 1
    assert contacts[0].email == "john@example.com"
