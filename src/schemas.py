from datetime import date
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List


class ContactBase(BaseModel):
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
    pass


class ContactUpdate(BaseModel):
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
    id: int

    model_config = ConfigDict(from_attributes=True)


class ContactsGet(BaseModel):
    data: List[ContactGet]


class User(BaseModel):
    id: int
    username: str = Field(max_length=100)
    email: EmailStr = Field(max_length=100)
    avatar: str | None = Field(default=None, max_length=255)
    role: str

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str = Field(max_length=100)
    email: EmailStr = Field(max_length=100)
    password: str
    role: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class RequestEmail(BaseModel):
    email: EmailStr


class RequestPasswordReset(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    password: str
