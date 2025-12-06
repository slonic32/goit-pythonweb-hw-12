"""Service layer for business logic related to contacts."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas import ContactCreate, ContactUpdate

from datetime import date
from src.database.models import User


class ContactService:
    """High-level service for working with contacts via ContactRepository."""

    def __init__(self, db: AsyncSession):
        self.contact_repository = ContactRepository(db)

    async def create_contact(self, user: User, body: ContactCreate):
        """Create a new contact for a user."""
        return await self.contact_repository.create_contact(user, body)

    async def get_contacts(
        self,
        user: User,
        skip: int = 0,
        limit: int = 100,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
    ):
        """Get contacts with filters and pagination."""
        return await self.contact_repository.get_contacts(
            user=user,
            skip=skip,
            limit=limit,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

    async def get_contact(self, user: User, contact_id: int):
        """Get single contact by ID."""
        return await self.contact_repository.get_contact_by_id(user, contact_id)

    async def update_contact(self, user: User, contact_id: int, body: ContactUpdate):
        """Update contact by ID."""
        return await self.contact_repository.update_contact(user, contact_id, body)

    async def remove_contact(self, user: User, contact_id: int):
        """Delete contact by ID."""
        return await self.contact_repository.remove_contact(user, contact_id)

    async def get_upcoming_birthdays(self, user: User, days: int = 7):
        """Return contacts with birthdays in the next N days."""

        today = date.today()
        contacts = await self.contact_repository.get_all_contacts(user)

        upcoming = []
        for contact in contacts:
            if contact.birthday is None:
                continue

            bday_this_year = date(
                year=today.year,
                month=contact.birthday.month,
                day=contact.birthday.day,
            )

            if bday_this_year < today:
                bday_this_year = date(
                    year=today.year + 1,
                    month=contact.birthday.month,
                    day=contact.birthday.day,
                )

            delta = (bday_this_year - today).days
            if 0 <= delta <= days:
                upcoming.append(contact)

        return upcoming
