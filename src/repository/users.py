"""Repository layer for working with User entities."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate


class UserRepository:
    """Provide CRUD operations for users using an async database session."""

    def __init__(self, session: AsyncSession):

        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Get a user by its ID."""
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """Get a user by username."""
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """Get a user by email."""
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """Create a new user with optional avatar URL."""
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_avatar_url(self, email: str, url: str) -> User:
        """Update avatar URL for a user by email."""
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: str) -> None:
        """Mark user email as confirmed."""
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()

    async def update_password(self, email: str, hashed_password: str) -> User | None:
        """Update user password and clear refresh token."""
        user = await self.get_user_by_email(email)
        if not user:
            return None

        user.hashed_password = hashed_password

        user.refresh_token = None

        await self.db.commit()
        await self.db.refresh(user)
        return user
