"""Service layer for business logic related to users."""

from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas import UserCreate


class UserService:
    """High-level service for working with users via UserRepository."""

    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """Create user and try to generate a Gravatar avatar."""
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """Simple getter."""
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """Simple getter."""
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """Simple getter."""
        return await self.repository.get_user_by_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """Update avatar URL in DB."""
        return await self.repository.update_avatar_url(email, url)

    async def confirmed_email(self, email: str):
        """Mark email as confirmed."""
        return await self.repository.confirmed_email(email)

    async def update_password(self, email: str, hashed_password: str):
        """Update password and clear refresh token."""
        return await self.repository.update_password(email, hashed_password)
