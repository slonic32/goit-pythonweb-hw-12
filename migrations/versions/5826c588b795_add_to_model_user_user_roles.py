"""add to model User user roles

Revision ID: 5826c588b795
Revises: 29269af5837a
Create Date: 2025-12-05 17:51:27.313448
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "5826c588b795"
down_revision: Union[str, Sequence[str], None] = "29269af5837a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    user_role_enum = postgresql.ENUM("user", "admin", name="userrole")
    user_role_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "users",
        sa.Column(
            "role",
            user_role_enum,
            nullable=False,
            server_default="user",
        ),
    )

    op.alter_column("users", "role", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""

    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS role")

    user_role_enum = postgresql.ENUM("user", "admin", name="userrole")
    user_role_enum.drop(op.get_bind(), checkfirst=True)
