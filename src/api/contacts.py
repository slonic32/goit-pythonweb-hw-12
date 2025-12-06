"""Contacts API routes.

Provides CRUD operations for contacts and an endpoint to get upcoming birthdays.
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import ContactCreate, ContactUpdate, ContactGet, ContactsGet
from src.services.contacts import ContactService

from src.database.models import User
from src.services.auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=ContactsGet)
async def read_contacts(
    skip: int | None = Query(default=0),
    limit: int | None = Query(default=100),
    first_name: str | None = Query(default=None),
    last_name: str | None = Query(default=None),
    email: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a list of contacts for the current user.

    Supports pagination and optional filtering by first name, last name and email.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(
        user=user,
        skip=skip,
        limit=limit,
        first_name=first_name,
        last_name=last_name,
        email=email,
    )
    return ContactsGet(data=contacts)


@router.get("/birthdays/next7", response_model=ContactsGet)
async def upcoming_birthdays(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get contacts whose birthdays are in the next 7 days."""
    contact_service = ContactService(db)
    contacts = await contact_service.get_upcoming_birthdays(user, days=7)
    return ContactsGet(data=contacts)


@router.get("/{contact_id}", response_model=ContactGet)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a single contact by ID for the current user.

    :raises HTTPException: 404 if contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(user, contact_id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    return contact


@router.post("/", response_model=ContactGet, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a new contact belonging to the current user."""
    contact_service = ContactService(db)
    return await contact_service.create_contact(user, body)


@router.patch("/{contact_id}", response_model=ContactGet)
async def update_contact(
    body: ContactUpdate,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Partially update a contact for the current user.

    :raises HTTPException: 404 if contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(user, contact_id, body)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactGet)
async def remove_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete a contact for the current user.

    :raises HTTPException: 404 if contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(user, contact_id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    return contact
