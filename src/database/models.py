"""SQLAlchemy ORM models for users and contacts."""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Text,
    func,
    Boolean,
    Enum as SqlEnum,
)
from sqlalchemy.orm import DeclarativeBase, relationship

from datetime import datetime

from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.sql.schema import ForeignKey

from enum import Enum


class UserRole(str, Enum):
    """Enum with available user roles."""

    USER = "user"
    ADMIN = "admin"


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


class Contact(Base):
    """Contact entity stored in the database."""

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100))
    phone = Column(String(30))
    birthday = Column(Date)
    extra_info = Column(Text)
    user_id = Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    user = relationship("User", backref="notes")


class User(Base):
    """User entity stored in the database."""

    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    refresh_token = Column(String(255), nullable=True)
    role = Column(
        String(20),
        default="user",
        nullable=False,
    )
