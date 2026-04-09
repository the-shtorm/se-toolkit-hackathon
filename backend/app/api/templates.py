"""Notification templates API endpoints."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import CurrentUser
from app.models.template import NotificationTemplate
from app.schemas.template import TemplateCreate, TemplateUpdate, TemplateResponse, TemplateListResponse

router = APIRouter(prefix="/templates", tags=["Templates"])


@router.post(
    "",
    response_model=TemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a notification template",
)
async def create_template(
    template_data: TemplateCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Create a new notification template."""
    template = NotificationTemplate(
        name=template_data.name,
        title_template=template_data.title_template,
        message_template=template_data.message_template,
        priority=template_data.priority,
        category=template_data.category,
        created_by=current_user.id,
        is_public=template_data.is_public,
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return TemplateResponse.model_validate(template)


@router.get(
    "",
    response_model=TemplateListResponse,
    summary="List notification templates",
)
async def list_templates(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
):
    """List all templates (public + user's own)."""
    base = select(NotificationTemplate).where(
        or_(
            NotificationTemplate.is_public == True,
            NotificationTemplate.created_by == current_user.id,
        )
    )

    if category:
        base = base.where(NotificationTemplate.category == category)

    count_q = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    templates_q = base.order_by(NotificationTemplate.created_at.desc()).offset(offset).limit(page_size)
    templates = (await db.execute(templates_q)).scalars().all()

    return TemplateListResponse(
        items=[TemplateResponse.model_validate(t) for t in templates],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{template_id}",
    response_model=TemplateResponse,
    summary="Get template details",
)
async def get_template(
    template_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get template details."""
    template = await db.get(NotificationTemplate, UUID(template_id))
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    # Check access: must be public or owned
    if not template.is_public and template.created_by != current_user.id:
        raise HTTPException(status_code=404, detail="Template not found")
    return TemplateResponse.model_validate(template)


@router.put(
    "/{template_id}",
    response_model=TemplateResponse,
    summary="Update template",
)
async def update_template(
    template_id: str,
    template_data: TemplateUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Update a notification template (owner only)."""
    template = await db.get(NotificationTemplate, UUID(template_id))
    if not template or template.created_by != current_user.id:
        raise HTTPException(status_code=404, detail="Template not found")

    for field, value in template_data.model_dump(exclude_unset=True).items():
        setattr(template, field, value)

    await db.commit()
    await db.refresh(template)
    return TemplateResponse.model_validate(template)


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete template",
)
async def delete_template(
    template_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Delete a notification template (owner only)."""
    template = await db.get(NotificationTemplate, UUID(template_id))
    if not template or template.created_by != current_user.id:
        raise HTTPException(status_code=404, detail="Template not found")

    await db.delete(template)
    await db.commit()
