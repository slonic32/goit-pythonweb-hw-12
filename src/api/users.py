"""User-related API routes.

Provides endpoints for reading current user info and updating avatar.
"""

from fastapi import APIRouter, Depends, UploadFile, File, Request
from src.schemas import User
from src.services.auth import get_current_user, get_current_admin_user

from slowapi import Limiter
from slowapi.util import get_remote_address

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.services.users import UserService
from src.services.upload_file import UploadFileService
from src.conf.config import settings

router = APIRouter(prefix="/users", tags=["users"])

limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/me", response_model=User, description="No more than 10 requests per minute"
)
@limiter.limit("10/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """Return the currently authenticated user.

    This endpoint is rate-limited to avoid abuse.
    """
    return user


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update avatar for the current admin user.

    The file is uploaded to Cloudinary and the avatar URL is stored in the database.
    Only users with the 'admin' role are allowed to call this endpoint.
    """
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
