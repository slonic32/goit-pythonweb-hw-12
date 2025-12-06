"""Pydantic settings model for application configuration.

Values are loaded from the .env file and environment variables.
"""

import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.config import settings


class DatabaseSessionManager:
    """Manage the asynchronous SQLAlchemy engine and session factory.

    :param url: Database connection URL.
    """

    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """Provide an asynchronous database session context manager.

        Rolls back the transaction on SQLAlchemy errors and always closes the session.
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise  # Re-raise the original error
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(settings.DB_URL)


async def get_db():
    """FastAPI dependency that yields an async database session."""
    async with sessionmanager.session() as session:
        yield session
