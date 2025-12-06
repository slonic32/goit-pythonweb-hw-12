import pytest

import src.services.email as email_module


@pytest.mark.asyncio
async def test_send_email_handles_connection_error(monkeypatch):

    class FakeFM:
        def __init__(self, conf):
            pass

        async def send_message(self, *args, **kwargs):

            raise email_module.ConnectionErrors("fail")

    monkeypatch.setattr(email_module, "FastMail", FakeFM)

    await email_module.send_email("test@example.com", "user", "http://host/")


@pytest.mark.asyncio
async def test_send_reset_password_email_handles_connection_error(monkeypatch):

    class FakeFM:
        def __init__(self, conf):
            pass

        async def send_message(self, *args, **kwargs):
            raise email_module.ConnectionErrors("fail")

    monkeypatch.setattr(email_module, "FastMail", FakeFM)

    await email_module.send_reset_password_email(
        "test@example.com",
        "user",
        "http://host/",
    )
