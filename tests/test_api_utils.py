import pytest


@pytest.mark.asyncio
async def test_healthchecker_ok(client):
    response = await client.get("/api/healthchecker")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to FastAPI!"
