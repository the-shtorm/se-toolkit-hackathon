"""User notification preferences API endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import CurrentUser
from app.models.preference import UserPreferences, DigestFrequencyEnum
from app.schemas.preference import PreferencesCreate, PreferencesUpdate, PreferencesResponse

router = APIRouter(prefix="/preferences", tags=["Preferences"])


@router.get(
    "",
    response_model=PreferencesResponse,
    summary="Get user preferences",
)
async def get_preferences(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get current user's notification preferences."""
    result = await db.execute(
        select(UserPreferences).where(UserPreferences.user_id == current_user.id)
    )
    prefs = result.scalar_one_or_none()

    if not prefs:
        # Create default preferences if none exist
        prefs = UserPreferences(
            user_id=current_user.id,
            web_enabled=True,
            email_enabled=True,
            sms_enabled=False,
            max_daily_notifications=50,
            timezone="UTC",
            digest_enabled=False,
        )
        db.add(prefs)
        await db.commit()
        await db.refresh(prefs)

    return PreferencesResponse.model_validate(prefs)


@router.put(
    "",
    response_model=PreferencesResponse,
    summary="Update user preferences",
)
async def update_preferences(
    prefs_data: PreferencesUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Update user's notification preferences."""
    result = await db.execute(
        select(UserPreferences).where(UserPreferences.user_id == current_user.id)
    )
    prefs = result.scalar_one_or_none()

    if not prefs:
        # Create new preferences
        prefs = UserPreferences(
            user_id=current_user.id,
            **prefs_data.model_dump(exclude_unset=True),
        )
        db.add(prefs)
    else:
        # Update existing
        for field, value in prefs_data.model_dump(exclude_unset=True).items():
            setattr(prefs, field, value)

    await db.commit()
    await db.refresh(prefs)
    return PreferencesResponse.model_validate(prefs)


@router.post(
    "",
    response_model=PreferencesResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user preferences",
)
async def create_preferences(
    prefs_data: PreferencesCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Create initial notification preferences for user."""
    # Check if preferences already exist
    result = await db.execute(
        select(UserPreferences).where(UserPreferences.user_id == current_user.id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Preferences already exist for this user. Use PUT to update.",
        )

    # Validate digest_frequency
    digest_freq = None
    if prefs_data.digest_frequency:
        try:
            digest_freq = DigestFrequencyEnum(prefs_data.digest_frequency)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid digest_frequency: {prefs_data.digest_frequency}. Must be 'daily' or 'weekly'.",
            )

    prefs = UserPreferences(
        user_id=current_user.id,
        web_enabled=prefs_data.web_enabled,
        email_enabled=prefs_data.email_enabled,
        sms_enabled=prefs_data.sms_enabled,
        quiet_hours_start=prefs_data.quiet_hours_start,
        quiet_hours_end=prefs_data.quiet_hours_end,
        max_daily_notifications=prefs_data.max_daily_notifications,
        timezone=prefs_data.timezone,
        digest_enabled=prefs_data.digest_enabled,
        digest_frequency=digest_freq,
    )
    db.add(prefs)
    await db.commit()
    await db.refresh(prefs)
    return PreferencesResponse.model_validate(prefs)
