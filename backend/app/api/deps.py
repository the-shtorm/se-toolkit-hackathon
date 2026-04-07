"""API dependencies."""
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status, Cookie, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.core.security import decode_access_token


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    access_token: str | None = Cookie(None),
) -> User:
    """Get the current authenticated user from the HTTPOnly cookie."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    if access_token is None:
        raise credentials_exception

    payload = decode_access_token(access_token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    return user


async def get_current_user_optional(
    db: Annotated[AsyncSession, Depends(get_db)] = Depends(get_db),
    access_token: str | None = Cookie(None),
) -> User | None:
    """Get current user if authenticated, None otherwise."""
    try:
        return await get_current_user(db, access_token)
    except HTTPException:
        return None


# Type aliases for cleaner endpoint definitions
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentDB = Annotated[AsyncSession, Depends(get_db)]
