"""Repository layer for working with Contact entities."""

from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactCreate, ContactUpdate


class ContactRepository:
    """Provide CRUD operations for contacts using an async database session."""

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(
        self,
        user: User,
        skip: int = 0,
        limit: int = 100,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
    ) -> List[Contact]:
        """Get a list of contacts for a given user with optional filters."""
        stmt = (
            select(Contact).where(Contact.user_id == user.id).offset(skip).limit(limit)
        )

        if first_name:
            stmt = stmt.where(Contact.first_name.ilike(f"%{first_name}%"))
        if last_name:
            stmt = stmt.where(Contact.last_name.ilike(f"%{last_name}%"))
        if email:
            stmt = stmt.where(Contact.email.ilike(f"%{email}%"))

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_contact_by_id(self, user: User, contact_id: int) -> Contact | None:
        """Get a single contact by its ID for the given user."""
        stmt = select(Contact).where(
            Contact.user_id == user.id, Contact.id == contact_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_contact(self, user: User, body: ContactCreate) -> Contact:
        """Create a new contact for the given user."""
        contact_data = body.model_dump(exclude_unset=True)

        contact = Contact(
            **contact_data,
            user_id=user.id,
        )
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return await self.get_contact_by_id(user, contact.id)

    async def remove_contact(self, user: User, contact_id: int) -> Contact | None:
        """Delete a contact by ID for the given user.

        :return: Deleted contact or None if not found.
        """
        contact = await self.get_contact_by_id(user, contact_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, user: User, contact_id: int, body: ContactUpdate
    ) -> Contact | None:
        """Update fields of an existing contact for the given user."""
        contact = await self.get_contact_by_id(user, contact_id)
        if contact:
            for key, value in body.model_dump(exclude_unset=True).items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact

    async def get_all_contacts(self, user: User) -> List[Contact]:
        """Get all contacts belonging to the given user."""
        stmt = select(Contact).where(Contact.user_id == user.id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
