import pytest

from src.repository.users import UserRepository
from src.schemas import UserCreate
from src.services.auth import create_access_token

import cloudinary.uploader


from datetime import timedelta


@pytest.mark.asyncio
async def test_only_admin_can_change_avatar(client, db_session, monkeypatch):

    def fake_upload(file, **kwargs):
        return {"version": 1}

    monkeypatch.setattr(cloudinary.uploader, "upload", fake_upload)

    user_repo = UserRepository(db_session)

    admin_body = UserCreate(
        username="admin_user",
        email="admin@example.com",
        password="pass",
        role="admin",
    )
    admin = await user_repo.create_user(admin_body)
    admin.confirmed = True
    await db_session.commit()
    await db_session.refresh(admin)

    admin_token = await create_access_token({"sub": admin.username})

    user_body = UserCreate(
        username="simple_user",
        email="user@example.com",
        password="pass",
        role="user",
    )
    simple_user = await user_repo.create_user(user_body)
    simple_user.confirmed = True
    await db_session.commit()
    await db_session.refresh(simple_user)

    user_token = await create_access_token({"sub": simple_user.username})

    resp = await client.patch(
        "/api/users/avatar",
        headers={"Authorization": f"Bearer {user_token}"},
        files={"file": ("avatar.png", b"fake image", "image/png")},
    )
    assert resp.status_code == 403

    resp = await client.patch(
        "/api/users/avatar",
        headers={"Authorization": f"Bearer {admin_token}"},
        files={"file": ("avatar.png", b"fake image", "image/png")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["avatar"] is not None


@pytest.mark.asyncio
async def test_me_endpoint_returns_current_user(client, db_session):
    user_repo = UserRepository(db_session)

    body = UserCreate(
        username="me_user",
        email="me@example.com",
        password="pass",
        role="user",
    )
    user = await user_repo.create_user(body)
    user.confirmed = True
    await db_session.commit()
    await db_session.refresh(user)

    token = await create_access_token({"sub": user.username})
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/users/me", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "me_user"
    assert data["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_me_endpoint_returns_current_user(client, db_session):
    user_repo = UserRepository(db_session)

    body = UserCreate(
        username="me_user",
        email="me@example.com",
        password="pass",
        role="user",
    )
    user = await user_repo.create_user(body)
    user.confirmed = True
    await db_session.commit()
    await db_session.refresh(user)

    token = await create_access_token({"sub": user.username})
    headers = {"Authorization": f"Bearer {token}"}

    resp1 = await client.get("/api/users/me", headers=headers)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["username"] == "me_user"

    resp2 = await client.get("/api/users/me", headers=headers)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["username"] == "me_user"
