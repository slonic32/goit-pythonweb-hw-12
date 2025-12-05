from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas import (
    UserCreate,
    Token,
    User,
    RequestEmail,
    TokenRefreshRequest,
    RequestPasswordReset,
    ResetPassword,
)
from src.services.auth import (
    create_access_token,
    Hash,
    get_email_from_token,
    create_refresh_token,
    verify_refresh_token,
)
from src.services.users import UserService
from src.database.db import get_db

from src.services.email import send_email, send_reset_password_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is used",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Name is used",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong user name or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email is not confirmed",
        )
    access_token = await create_access_token(data={"sub": user.username})
    refresh_token = await create_refresh_token(data={"sub": user.username})

    user.refresh_token = refresh_token
    await db.commit()
    await db.refresh(user)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Email is already confirmed"}
    await user_service.confirmed_email(email)
    return {"message": "Email is confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if not user:
        return {"message": "Wrong mail"}

    if user.confirmed:
        return {"message": "Email is already confirmed"}

    background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your mail"}


@router.post("/refresh-token", response_model=Token)
async def new_token(request: TokenRefreshRequest, db: Session = Depends(get_db)):

    user = await verify_refresh_token(request.refresh_token, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    new_access_token = await create_access_token(data={"sub": user.username})
    return {
        "access_token": new_access_token,
        "refresh_token": request.refresh_token,
        "token_type": "bearer",
    }


@router.post("/request_password_reset")
async def request_password_reset(
    body: RequestPasswordReset,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user:
        background_tasks.add_task(
            send_reset_password_email, user.email, user.username, request.base_url
        )

    return {"message": "A reset link has been sent"}


@router.post("/reset_password")
async def reset_password(
    data: ResetPassword,
    token: str,
    db: Session = Depends(get_db),
):
    try:
        email = await get_email_from_token(token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )

    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )

    hashed_password = Hash().get_password_hash(data.password)
    await user_service.update_password(email, hashed_password)

    return {"message": "Password has been successfully reset"}
