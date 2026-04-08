"""Seed data script: Creates 5 users and 50 sample notifications."""
import asyncio
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import engine, async_session_factory, Base
from app.models.user import User
from app.models.notification import (
    Notification,
    NotificationRecipient,
    PriorityEnum,
    NotificationStatusEnum,
    DeliveryStatusEnum,
)

# Sample data
USERS = [
    {"email": "alice@demo.com", "username": "alice", "password": "demo1234"},
    {"email": "bob@demo.com", "username": "bob", "password": "demo1234"},
    {"email": "charlie@demo.com", "username": "charlie", "password": "demo1234"},
    {"email": "diana@demo.com", "username": "diana", "password": "demo1234"},
    {"email": "eve@demo.com", "username": "eve", "password": "demo1234"},
]

NOTIFICATION_TEMPLATES = [
    {"title": "System Update", "message": "A new system update is available. Please review and apply at your earliest convenience.", "priority": "medium"},
    {"title": "Security Alert", "message": "Unusual login attempt detected from a new location. Please verify your recent activity.", "priority": "critical"},
    {"title": "Meeting Reminder", "message": "Your team meeting starts in 30 minutes. Don't forget to prepare your status update.", "priority": "low"},
    {"title": "Deployment Success", "message": "Production deployment completed successfully. All services are running normally.", "priority": "medium"},
    {"title": "Payment Received", "message": "A payment of $1,250.00 has been processed and deposited into your account.", "priority": "high"},
    {"title": "New Comment", "message": "Someone left a comment on your recent post. Check the discussion thread for details.", "priority": "low"},
    {"title": "Storage Warning", "message": "Your storage usage has exceeded 85% capacity. Consider upgrading your plan.", "priority": "high"},
    {"title": "Password Changed", "message": "Your account password has been successfully updated. If you didn't make this change, contact support.", "priority": "medium"},
    {"title": "Task Assigned", "message": "You have been assigned a new task: 'Review pull request #42'. Deadline is next Friday.", "priority": "medium"},
    {"title": "Server Down", "message": "CRITICAL: Database server us-west-2 is unreachable. Automated failover has been initiated.", "priority": "critical"},
    {"title": "Weekly Report", "message": "Your weekly activity report is ready. You received 23 notifications and completed 15 tasks.", "priority": "low"},
    {"title": "API Key Expiring", "message": "Your API key will expire in 7 days. Please generate a new key to avoid service interruption.", "priority": "high"},
    {"title": "Feature Request Approved", "message": "Your feature request for 'Dark Mode' has been approved and is now in the development backlog.", "priority": "low"},
    {"title": "Backup Completed", "message": "Daily database backup completed successfully. 2.3 GB backed up to us-east-1.", "priority": "low"},
    {"title": "Rate Limit Warning", "message": "Your application has reached 90% of its API rate limit. Requests may be throttled soon.", "priority": "medium"},
]

PRIORITIES = [p for p in PriorityEnum]
STATUSES = [NotificationStatusEnum.sent, NotificationStatusEnum.read]


async def seed():
    async with engine.begin() as conn:
        from app.models import user  # noqa: F401
        from app.models import notification  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        # Check if users already exist
        result = await db.execute(select(User).limit(1))
        existing_users = result.scalars().all()
        if existing_users:
            print("⚠️  Users already exist. Dropping and recreating...")
            await conn.rollback()

    # Create tables if they don't exist
    async with engine.begin() as conn:
        from app.models import user, notification  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        # Clear existing data (in reverse dependency order)
        await db.execute(NotificationRecipient.__table__.delete())
        await db.execute(Notification.__table__.delete())
        await db.execute(User.__table__.delete())
        await db.commit()
        print("🧹 Cleared existing data")

        # Create users
        print("👥 Creating 5 users...")
        user_map = {}  # username -> User object
        for u in USERS:
            from app.core.security import hash_password
            new_user = User(
                email=u["email"],
                username=u["username"],
                password_hash=hash_password(u["password"]),
                is_active=True,
            )
            db.add(new_user)
        await db.commit()

        result = await db.execute(select(User).order_by(User.username))
        users = result.scalars().all()
        for u in users:
            user_map[u.username] = u

        print(f"   ✅ Created {len(users)} users")

        # Create 50 notifications spread across users and time
        print("📝 Creating 50 notifications...")
        now = datetime.now(timezone.utc)
        created_count = 0

        for i in range(50):
            # Random template
            template = random.choice(NOTIFICATION_TEMPLATES)

            # Random creator
            creator = random.choice(list(user_map.values()))

            # Random time (within last 7 days)
            hours_ago = random.uniform(0, 168)
            created_at = now - timedelta(hours=hours_ago)

            # Status: 40% read, 60% sent
            is_read = random.random() < 0.4

            notification = Notification(
                title=template["title"],
                message=template["message"],
                priority=PriorityEnum(template["priority"]),
                status=NotificationStatusEnum.read if is_read else NotificationStatusEnum.sent,
                created_by=creator.id,
                created_at=created_at,
                read_at=created_at + timedelta(minutes=random.randint(1, 120)) if is_read else None,
            )
            db.add(notification)
            await db.flush()

            # Add creator as recipient
            recipient = NotificationRecipient(
                notification_id=notification.id,
                user_id=creator.id,
                delivery_status=DeliveryStatusEnum.read if is_read else DeliveryStatusEnum.delivered,
                delivered_at=created_at + timedelta(seconds=random.randint(1, 30)),
            )
            db.add(recipient)
            created_count += 1

        await db.commit()
        print(f"   ✅ Created {created_count} notifications")

        # Summary
        result = await db.execute(select(User))
        total_users = len(result.scalars().all())
        result = await db.execute(select(Notification))
        total_notifs = len(result.scalars().all())
        result = await db.execute(select(NotificationRecipient))
        total_recipients = len(result.scalars().all())

        print("\n📊 Seed Summary:")
        print(f"   Users:          {total_users}")
        print(f"   Notifications:  {total_notifs}")
        print(f"   Recipients:     {total_recipients}")
        print(f"\n🔑 Demo credentials:")
        for u in USERS:
            print(f"   {u['username']:10s} | {u['email']:20s} | {u['password']}")
        print("\n🚀 Open http://localhost:3000 to see the dashboard!")


if __name__ == "__main__":
    asyncio.run(seed())
