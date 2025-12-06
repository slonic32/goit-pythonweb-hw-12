import sys
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import AsyncClient
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from main import app
from src.database.models import Base
from src.database.db import get_db
from src.services import auth as auth_service


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_DATABASE_URL, future=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine_test,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def override_get_db():
    async with AsyncSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


class DummyRedis:
    def __init__(self):
        self.store = {}

    def get(self, key: str):
        return self.store.get(key)

    def set(self, key: str, value: str):
        self.store[key] = value

    def expire(self, key: str, seconds: int):

        pass


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    auth_service.redis_client = DummyRedis()

    yield

    await engine_test.dispose()


@pytest_asyncio.fixture
async def db_session():

    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client():

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
