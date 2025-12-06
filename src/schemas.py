from datetime import date
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List


class ContactBase(BaseModel):
    """Base schema for contact data.

    Contains common fields used for creating, updating and returning contacts.
    """

    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: EmailStr = Field(max_length=100)
    phone: str = Field(
        max_length=30,
        pattern=r"^\+?[0-9\-\s()]{7,20}$",
        description="Phone number (allowed 7-20 symbols: numbers, spaces, '-', '()')",
    )
    birthday: date
    extra_info: str | None = None


class ContactCreate(ContactBase):
    """Schema for creating a new contact."""

    pass


class ContactUpdate(BaseModel):
    """Schema for partial update of contact data.

    All fields are optional and only provided values will be updated.
    """

    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=100)
    phone: str | None = Field(
        default=None,
        max_length=30,
        pattern=r"^\+?[0-9\-\s()]{7,20}$",
        description="Phone number (allowed 7-20 symbols: numbers, spaces, '-', '()')",
    )
    birthday: date | None = None
    extra_info: str | None = None


class ContactGet(ContactBase):
    """Schema for returning a single contact from the database."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class ContactsGet(BaseModel):
    """Schema for returning a list of contacts."""

    data: List[ContactGet]

    data: List[ContactGet]


class User(BaseModel):
    """Schema for returning user data."""

    id: int
    username: str = Field(max_length=100)
    email: EmailStr = Field(max_length=100)
    avatar: str | None = Field(default=None, max_length=255)
    role: str

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """Schema for user registration payload."""

    username: str = Field(max_length=100)
    email: EmailStr = Field(max_length=100)
    password: str
    role: str


class Token(BaseModel):
    """JWT token pair used for authentication."""

    access_token: str
    refresh_token: str
    token_type: str


class TokenRefreshRequest(BaseModel):
    """Payload for requesting a new access token using refresh token."""

    refresh_token: str


class RequestEmail(BaseModel):
    """Payload for requesting a new confirmation email."""

    email: EmailStr


class RequestPasswordReset(BaseModel):
    """Payload for requesting a password reset email."""

    email: EmailStr


class ResetPassword(BaseModel):
    """Payload with a new password for password reset."""

    password: str
