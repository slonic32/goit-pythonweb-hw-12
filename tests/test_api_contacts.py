import pytest

from src.repository.users import UserRepository
from src.schemas import UserCreate
from src.services.auth import create_access_token

from datetime import date, timedelta


@pytest.mark.asyncio
async def test_contacts_crud(client, db_session):

    user_repo = UserRepository(db_session)
    user_body = UserCreate(
        username="contacts_owner",
        email="contacts_owner@example.com",
        password="pass",
        role="user",
    )
    user = await user_repo.create_user(user_body)
    user.confirmed = True
    await db_session.commit()
    await db_session.refresh(user)

    token = await create_access_token({"sub": user.username})
    headers = {"Authorization": f"Bearer {token}"}

    contact_payload = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice@example.com",
        "phone": "+380123456789",
        "birthday": "1995-05-05",
        "extra_info": "colleague",
    }

    response = await client.post(
        "/api/contacts/", json=contact_payload, headers=headers
    )
    assert response.status_code == 201
    contact = response.json()
    contact_id = contact["id"]

    response = await client.get("/api/contacts/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1

    response = await client.patch(
        f"/api/contacts/{contact_id}",
        json={"first_name": "Alicia"},
        headers=headers,
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["first_name"] == "Alicia"

    response = await client.delete(f"/api/contacts/{contact_id}", headers=headers)
    assert response.status_code == 200

    response = await client.get("/api/contacts/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 0


@pytest.mark.asyncio
async def test_upcoming_birthdays(client, db_session):
    user_repo = UserRepository(db_session)
    user_body = UserCreate(
        username="bday_user",
        email="bday@example.com",
        password="pass",
        role="user",
    )
    user = await user_repo.create_user(user_body)
    user.confirmed = True
    await db_session.commit()
    await db_session.refresh(user)

    token = await create_access_token({"sub": user.username})
    headers = {"Authorization": f"Bearer {token}"}

    today = date.today()
    near = today
    far = today + timedelta(days=30)

    contact1 = {
        "first_name": "Near",
        "last_name": "Birthday",
        "email": "near@example.com",
        "phone": "+380123456789",
        "birthday": near.isoformat(),
        "extra_info": "near",
    }

    contact2 = {
        "first_name": "Far",
        "last_name": "Birthday",
        "email": "far@example.com",
        "phone": "+380987654321",
        "birthday": far.isoformat(),
        "extra_info": "far",
    }

    await client.post("/api/contacts/", json=contact1, headers=headers)
    await client.post("/api/contacts/", json=contact2, headers=headers)

    resp = await client.get("/api/contacts/birthdays/next7", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    assert len(data["data"]) == 1
    assert data["data"][0]["email"] == "near@example.com"
