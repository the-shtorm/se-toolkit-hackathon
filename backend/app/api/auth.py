"""Authentication API endpoints."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, LoginResponse
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.config import settings
from app.api.deps import get_current_user, CurrentUser

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Rate limiter: 5 attempts per minute per IP
limiter = Limiter(key_func=get_remote_address)

# Cookie settings
COOKIE_MAX_AGE = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds
COOKIE_SECURE = False  # Set to True in production with HTTPS


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Register a new user account."""
    # Hash the password
    password_hash = hash_password(user_data.password)

    # Create new user
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=password_hash,
    )

    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email or username already exists",
        )

    return new_user


@router.post("/login", response_model=LoginResponse, summary="Login and receive authentication cookie")
@limiter.limit("5/minute")
async def login(
    request: Request,
    login_data: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Authenticate user and set HTTPOnly cookie with JWT token."""
    # Find user by email
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is disabled",
        )

    # Create access token (convert UUID to string for JSON serialization)
    access_token = create_access_token(data={"sub": str(user.id)})

    # Create response with HTTPOnly cookie AND token in body for API testing
    response = JSONResponse(
        content={
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
        }
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
        path="/",
    )

    return response


@router.post("/logout", summary="Logout and clear authentication cookie")
async def logout(response: Response):
    """Clear the authentication cookie."""
    response.delete_cookie(
        key="access_token",
        path="/",
    )
    return {"message": "Logout successful"}


@router.get("/me", response_model=UserResponse, summary="Get current user info")
async def get_me(current_user: CurrentUser):
    """Return the currently authenticated user's information."""
    return current_user


@router.get("/ws-token", summary="Get authentication token for WebSocket")
async def get_ws_token(current_user: CurrentUser):
    """
    Return a JWT token for WebSocket authentication.
    Since HTTP-only cookies can't be read by frontend JS, this endpoint
    provides the token needed to authenticate WebSocket connections.
    """
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": str(current_user.id)})
    return {"token": token}
