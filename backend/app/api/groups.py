"""Notification group API endpoints."""
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import CurrentUser, CurrentDB
from app.models.user import User
from app.models.group import NotificationGroup, GroupMember, MemberRoleEnum
from app.schemas.group import (
    GroupCreate,
    GroupUpdate,
    GroupResponse,
    GroupDetailResponse,
    GroupMemberResponse,
    GroupListResponse,
    AddMemberRequest,
)

router = APIRouter(prefix="/groups", tags=["Groups"])


async def _get_group_or_404(
    db: AsyncSession,
    group_id: UUID,
    user_id: UUID,
) -> NotificationGroup:
    """Get a group if user is a member, else raise 404."""
    stmt = (
        select(NotificationGroup)
        .join(GroupMember)
        .where(NotificationGroup.id == group_id, GroupMember.user_id == user_id)
    )
    result = await db.execute(stmt)
    group = result.scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


async def _check_admin(
    db: AsyncSession,
    group_id: UUID,
    user_id: UUID,
) -> None:
    """Ensure the user is an admin of the group."""
    stmt = select(GroupMember).where(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id,
        GroupMember.role == MemberRoleEnum.admin,
    )
    result = await db.execute(stmt)
    member = result.scalar_one_or_none()
    if member is None:
        raise HTTPException(status_code=403, detail="Admin access required")


# ── CRUD ────────────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=GroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a notification group",
)
async def create_group(
    group_data: GroupCreate,
    current_user: CurrentUser,
    db: CurrentDB,
):
    """Create a group. The creator is automatically added as admin."""
    group = NotificationGroup(
        name=group_data.name,
        description=group_data.description,
        created_by=current_user.id,
    )
    db.add(group)
    await db.flush()

    # Creator becomes admin
    admin_member = GroupMember(
        group_id=group.id,
        user_id=current_user.id,
        role=MemberRoleEnum.admin,
    )
    db.add(admin_member)
    await db.commit()
    await db.refresh(group)

    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        created_by=group.created_by,
        created_at=group.created_at,
        updated_at=group.updated_at,
        member_count=1,
    )


@router.get(
    "",
    response_model=GroupListResponse,
    summary="List user's groups",
)
async def list_groups(
    current_user: CurrentUser,
    db: CurrentDB,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List all groups the current user is a member of."""
    base = (
        select(NotificationGroup)
        .join(GroupMember)
        .where(GroupMember.user_id == current_user.id)
    )

    # Count
    count_q = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    groups_q = base.order_by(NotificationGroup.created_at.desc()).offset(offset).limit(page_size)
    groups = (await db.execute(groups_q)).scalars().all()

    # Fetch member counts for each group
    items = []
    for g in groups:
        count_q = select(func.count()).where(GroupMember.group_id == g.id)
        mc = (await db.execute(count_q)).scalar() or 0
        items.append(GroupResponse(
            id=g.id,
            name=g.name,
            description=g.description,
            created_by=g.created_by,
            created_at=g.created_at,
            updated_at=g.updated_at,
            member_count=mc,
        ))

    return GroupListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get(
    "/{group_id}",
    response_model=GroupDetailResponse,
    summary="Get group details with members",
)
async def get_group(
    group_id: str,
    current_user: CurrentUser,
    db: CurrentDB,
):
    """Get group details including all members."""
    group = await _get_group_or_404(db, UUID(group_id), current_user.id)

    # Fetch members
    members_stmt = (
        select(GroupMember, User.username, User.email)
        .join(User, User.id == GroupMember.user_id)
        .where(GroupMember.group_id == group.id)
        .order_by(GroupMember.role.desc(), GroupMember.joined_at)
    )
    rows = (await db.execute(members_stmt)).all()

    members = [
        GroupMemberResponse(
            id=gm.id,
            user_id=gm.user_id,
            username=username,
            email=email,
            role=gm.role,
            joined_at=gm.joined_at,
        )
        for gm, username, email in rows
    ]

    return GroupDetailResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        created_by=group.created_by,
        created_at=group.created_at,
        updated_at=group.updated_at,
        member_count=len(members),
        members=members,
    )


@router.put(
    "/{group_id}",
    response_model=GroupResponse,
    summary="Update group",
)
async def update_group(
    group_id: str,
    group_data: GroupUpdate,
    current_user: CurrentUser,
    db: CurrentDB,
):
    """Update group name or description (admin only)."""
    await _check_admin(db, UUID(group_id), current_user.id)
    group = await _get_group_or_404(db, UUID(group_id), current_user.id)

    if group_data.name is not None:
        group.name = group_data.name
    if group_data.description is not None:
        group.description = group_data.description

    await db.commit()
    await db.refresh(group)

    # Count members
    count_q = select(func.count()).where(GroupMember.group_id == group.id)
    member_count = (await db.execute(count_q)).scalar() or 0

    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        created_by=group.created_by,
        created_at=group.created_at,
        updated_at=group.updated_at,
        member_count=member_count,
    )


@router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete group",
)
async def delete_group(
    group_id: str,
    current_user: CurrentUser,
    db: CurrentDB,
):
    """Delete a group (admin only)."""
    await _check_admin(db, UUID(group_id), current_user.id)
    group = await _get_group_or_404(db, UUID(group_id), current_user.id)
    await db.delete(group)
    await db.commit()


# ── Member Management ──────────────────────────────────────────────────────

@router.post(
    "/{group_id}/members",
    response_model=GroupMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add member to group",
)
async def add_member(
    group_id: str,
    member_data: AddMemberRequest,
    current_user: CurrentUser,
    db: CurrentDB,
):
    """Add a user to the group (admin only)."""
    await _check_admin(db, UUID(group_id), current_user.id)

    # Check if already a member
    existing = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == UUID(group_id),
            GroupMember.user_id == member_data.user_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User is already a member")

    member = GroupMember(
        group_id=UUID(group_id),
        user_id=member_data.user_id,
        role=member_data.role,
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)

    # Get user info
    user_result = await db.execute(select(User).where(User.id == member_data.user_id))
    user = user_result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return GroupMemberResponse(
        id=member.id,
        user_id=member.user_id,
        username=user.username,
        email=user.email,
        role=member.role,
        joined_at=member.joined_at,
    )


@router.delete(
    "/{group_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove member from group",
)
async def remove_member(
    group_id: str,
    user_id: str,
    current_user: CurrentUser,
    db: CurrentDB,
):
    """Remove a user from the group (admin only)."""
    gid = UUID(group_id)
    uid = UUID(user_id)

    await _check_admin(db, gid, current_user.id)

    # Prevent removing the last admin
    members = await db.execute(
        select(GroupMember).where(GroupMember.group_id == gid)
    )
    member_list = members.scalars().all()
    admins = [m for m in member_list if m.role == MemberRoleEnum.admin]
    target = next((m for m in member_list if m.user_id == uid), None)

    if target is None:
        raise HTTPException(status_code=404, detail="Member not found")

    if target in admins and len(admins) <= 1:
        raise HTTPException(status_code=400, detail="Cannot remove the last admin")

    await db.delete(target)
    await db.commit()
