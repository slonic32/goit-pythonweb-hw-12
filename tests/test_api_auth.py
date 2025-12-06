import pytest

from src.repository.users import UserRepository
from src.schemas import UserCreate
from src.services.auth import create_access_token


from src.services.auth import create_email_token, Hash

import src.services.email as email_module

import src.api.auth as auth_module


@pytest.mark.asyncio
async def test_register_and_login(client, db_session, monkeypatch):

    async def fake_send_email(email, username, host):
        pass

    monkeypatch.setattr(auth_module, "send_email", fake_send_email)

    payload = {
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "password123",
        "role": "admin",
    }
    response = await client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["email"] == "test2@example.com"

    repo = UserRepository(db_session)
    user = await repo.get_user_by_email("test2@example.com")
    user.confirmed = True
    await db_session.commit()
    await db_session.refresh(user)

    form_data = {
        "username": "testuser2",
        "password": "password123",
    }
    response = await client.post(
        "/api/auth/login",
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    response = await client.post(
        "/api/auth/refresh-token",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert response.status_code == 200
    new_tokens = response.json()
    assert "access_token" in new_tokens


@pytest.mark.asyncio
async def test_password_reset_flow(client, db_session):
    repo = UserRepository(db_session)
    body = UserCreate(
        username="reset_user",
        email="reset@example.com",
        password=Hash().get_password_hash("oldpass"),
        role="user",
    )
    user = await repo.create_user(body)
    user.confirmed = True
    await db_session.commit()
    await db_session.refresh(user)

    token = create_email_token({"sub": user.email})

    resp = await client.post(
        f"/api/auth/reset_password?token={token}",
        json={"password": "newpass"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "Password has been successfully reset"


@pytest.mark.asyncio
async def test_request_email_wrong_mail(client, db_session, monkeypatch):
    async def fake_send_email(email, username, host):
        pass

    monkeypatch.setattr(auth_module, "send_email", fake_send_email)

    resp = await client.post(
        "/api/auth/request_email",
        json={"email": "unknown@example.com"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "Wrong mail"


@pytest.mark.asyncio
async def test_request_password_reset_triggers_email(client, db_session, monkeypatch):

    repo = UserRepository(db_session)
    body = UserCreate(
        username="reset_flow_user",
        email="reset_flow@example.com",
        password="pass",
        role="user",
    )
    await repo.create_user(body)
    await db_session.commit()

    called = {"value": False}

    async def fake_send_reset(email, username, host):
        called["value"] = True

    monkeypatch.setattr(auth_module, "send_reset_password_email", fake_send_reset)

    resp = await client.post(
        "/api/auth/request_password_reset",
        json={"email": "reset_flow@example.com"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "reset link" in data["message"].lower()
    assert called["value"] is True


@pytest.mark.asyncio
async def test_confirmed_email_invalid_token(client):

    resp = await client.get("/api/auth/confirmed_email/invalid_token_here")
    assert resp.status_code == 422
    data = resp.json()
    assert "Wrong token" in data["detail"]


@pytest.mark.asyncio
async def test_refresh_token_invalid(client):
    resp = await client.post(
        "/api/auth/refresh-token",
        json={"refresh_token": "totally_invalid"},
    )
    assert resp.status_code == 401
    data = resp.json()
    assert "Invalid or expired refresh token" in data["detail"]
