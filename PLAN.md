# Smart Notification Manager - Project Plan

## Overview
A full-stack notification management system that allows users to create, manage, and receive notifications through a web interface, with a FastAPI backend and PostgreSQL database, all containerized with Docker.

### Core Value Proposition
**"Never miss important updates - get real-time notifications delivered instantly to your personalized dashboard."**

---

## Product Versions

### Version 1: Real-Time Notification Dashboard (MVP)
**Core Feature:** Users can create notifications and receive them instantly in a web dashboard via WebSocket.

**Scope:**
- User authentication (register/login)
- Create notifications (title, message, priority)
- Real-time delivery via WebSocket
- Notification list with mark-as-read
- Clean, functional UI

**Why this works:**
- Single, focused value proposition
- Functioning product, not a prototype
- Solves real problem: centralized notification tracking
- Technically achievable and demonstrable

**Components:**
- ✅ Backend: FastAPI + WebSocket support
- ✅ Database: PostgreSQL with notification storage
- ✅ Frontend: React web app with real-time updates

---

### Version 2: Smart Notification Management Platform
**Builds on V1 by adding:**
- Notification groups (team notifications)
- Events & scheduled notifications
- Notification templates
- User preferences (quiet hours, timezone)
- Analytics dashboard
- Scheduled digests
- Production deployment

**Deployment:** Docker Compose with Nginx reverse proxy, ready for production use.

---

## Tech Stack

### Backend
- **Python 3.12+**
- **FastAPI** - High-performance async web framework
- **SQLAlchemy 2.0** - ORM with async support
- **Alembic** - Database migrations
- **Pydantic v2** - Data validation
- **asyncpg** - Async PostgreSQL driver
- **WebSockets** - Real-time notification delivery
- **Celery + Redis** - Background task processing (V2: scheduled notifications, email/SMS)

### Frontend
- **React 18+ with TypeScript** (Recommended over alternatives for this use case)
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **React Query (TanStack Query)** - Server state management
- **Zustand** - Client state management
- **React Router** - Routing
- **Sonner/Toast** - In-app notification UI

### Database
- **PostgreSQL 16** - Primary database
- **Redis 7** - Cache & message broker for Celery

### Infrastructure
- **Docker & Docker Compose** - Containerization

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│                    http://localhost:3000                     │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP / WebSocket
┌────────────────────────▼────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│                    http://localhost:8000                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   REST API   │  │  WebSocket   │  │  Celery Workers  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
┌──────────────────┐          ┌──────────────────┐
│   PostgreSQL     │          │      Redis       │
│   (port 5432)    │          │   (port 6379)    │
└──────────────────┘          └──────────────────┘
```

---

## Database Schema

### Version 1 Tables (Core Functionality)

```sql
-- Users
users
├── id (UUID, PK)
├── email (VARCHAR, UNIQUE, NOT NULL)
├── username (VARCHAR, UNIQUE, NOT NULL)
├── password_hash (VARCHAR, NOT NULL)
├── is_active (BOOLEAN, DEFAULT TRUE)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)

-- Notifications
notifications
├── id (UUID, PK)
├── title (VARCHAR, NOT NULL)
├── message (TEXT, NOT NULL)
├── priority (ENUM: 'low', 'medium', 'high', 'critical')
├── status (ENUM: 'pending', 'sent', 'delivered', 'read', 'failed')
├── created_by (UUID, FK -> users.id)
├── created_at (TIMESTAMP)
├── sent_at (TIMESTAMP, NULLABLE)
└── read_at (TIMESTAMP, NULLABLE)

-- Notification Recipients
notification_recipients
├── id (UUID, PK)
├── notification_id (UUID, FK -> notifications.id)
├── user_id (UUID, FK -> users.id)
├── delivery_status (ENUM: 'pending', 'delivered', 'read', 'failed')
└── delivered_at (TIMESTAMP, NULLABLE)
```

---

### Version 2 Tables (Enhanced Features)

```sql
-- Notification Groups (V2)
notification_groups
├── id (UUID, PK)
├── name (VARCHAR, NOT NULL)
├── description (TEXT)
├── created_by (UUID, FK -> users.id)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)

-- Group Memberships (Many-to-Many) (V2)
group_members
├── id (UUID, PK)
├── group_id (UUID, FK -> notification_groups.id)
├── user_id (UUID, FK -> users.id)
├── role (ENUM: 'admin', 'member')
└── joined_at (TIMESTAMP)

-- Notification Events/Triggers (V2)
events
├── id (UUID, PK)
├── name (VARCHAR, NOT NULL)
├── description (TEXT)
├── created_by (UUID, FK -> users.id)
├── scheduled_at (TIMESTAMP, NULLABLE) -- For scheduled notifications
├── is_recurring (BOOLEAN, DEFAULT FALSE)
├── recurrence_rule (VARCHAR, NULLABLE) -- iCal RRULE format
└── created_at (TIMESTAMP)

-- User Notification Preferences (V2)
notification_preferences
├── id (UUID, PK)
├── user_id (UUID, FK -> users.id, UNIQUE)
├── web_enabled (BOOLEAN, DEFAULT TRUE)
├── email_enabled (BOOLEAN, DEFAULT TRUE)
├── sms_enabled (BOOLEAN, DEFAULT FALSE)
├── quiet_hours_start (TIME, NULLABLE)
├── quiet_hours_end (TIME, NULLABLE)
├── max_daily_notifications (INTEGER, DEFAULT 50)
├── timezone (VARCHAR, DEFAULT 'UTC')
├── digest_enabled (BOOLEAN, DEFAULT FALSE)
└── digest_frequency (ENUM: 'daily', 'weekly', NULLABLE)

-- Notification Channels (V2 - future extensibility)
notification_channels
├── id (UUID, PK)
├── name (VARCHAR, UNIQUE) -- 'email', 'sms', 'push', 'webhook'
├── is_active (BOOLEAN)
└── config (JSONB)

-- Idempotency Keys (V2 - prevent duplicate notifications)
idempotency_keys
├── id (UUID, PK)
├── key (VARCHAR, UNIQUE, NOT NULL, INDEXED)
├── notification_id (UUID, FK -> notifications.id, NULLABLE)
├── created_by (UUID, FK -> users.id)
├── expires_at (TIMESTAMP, NOT NULL)
└── created_at (TIMESTAMP)

-- Notification Templates (V2)
notification_templates
├── id (UUID, PK)
├── name (VARCHAR, NOT NULL)
├── title_template (VARCHAR, NOT NULL) -- Can use {variables}
├── message_template (TEXT, NOT NULL)
├── priority (ENUM: 'low', 'medium', 'high', 'critical')
├── category (VARCHAR, NULLABLE) -- 'system', 'meeting', 'task', etc.
├── created_by (UUID, FK -> users.id)
├── is_public (BOOLEAN, DEFAULT FALSE) -- Shared across users
└── created_at (TIMESTAMP)

-- Notification Snoozes (V2)
notification_snoozes
├── id (UUID, PK)
├── notification_id (UUID, FK -> notifications.id)
├── user_id (UUID, FK -> users.id)
├── snoozed_until (TIMESTAMP, NOT NULL)
└── created_at (TIMESTAMP)

-- Audit Logs (V2)
audit_logs
├── id (UUID, PK)
├── user_id (UUID, FK -> users.id)
├── action (VARCHAR, NOT NULL) -- 'create', 'update', 'delete', 'send'
├── entity_type (VARCHAR, NOT NULL) -- 'notification', 'group', 'event'
├── entity_id (UUID, NOT NULL)
├── old_values (JSONB, NULLABLE)
├── new_values (JSONB, NULLABLE)
├── ip_address (VARCHAR, NULLABLE)
└── created_at (TIMESTAMP)
```

---

## API Endpoints

### Version 1 Endpoints

#### Authentication
```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
GET    /api/v1/auth/me
```

#### Notifications
```
GET    /api/v1/notifications                   # List user's notifications
POST   /api/v1/notifications                   # Create & send notification
GET    /api/v1/notifications/{notif_id}        # Get notification
PUT    /api/v1/notifications/{notif_id}/read   # Mark as read
```

#### WebSocket
```
WS     /ws/notifications                       # Real-time notification stream
```

---

### Version 2 Endpoints (Additional)

#### Users
```
GET    /api/v1/users              # List users (admin)
GET    /api/v1/users/{user_id}    # Get user details
PUT    /api/v1/users/{user_id}    # Update user
```

#### Notification Groups
```
GET    /api/v1/groups                        # List user's groups
POST   /api/v1/groups                        # Create group
GET    /api/v1/groups/{group_id}             # Get group details
PUT    /api/v1/groups/{group_id}             # Update group
DELETE /api/v1/groups/{group_id}             # Delete group
POST   /api/v1/groups/{group_id}/members     # Add member
DELETE /api/v1/groups/{group_id}/members/{user_id}  # Remove member
```

#### Events
```
GET    /api/v1/events                        # List events
POST   /api/v1/events                        # Create event
GET    /api/v1/events/{event_id}             # Get event
PUT    /api/v1/events/{event_id}             # Update event
DELETE /api/v1/events/{event_id}             # Delete event
```

#### Advanced Notifications
```
POST   /api/v1/notifications/bulk-send         # Send to multiple recipients
GET    /api/v1/notifications/stats             # Notification statistics
```

#### Templates
```
GET    /api/v1/templates                         # List templates
POST   /api/v1/templates                         # Create template
GET    /api/v1/templates/{template_id}           # Get template
PUT    /api/v1/templates/{template_id}           # Update template
DELETE /api/v1/templates/{template_id}           # Delete template
```

#### Preferences
```
GET    /api/v1/preferences                       # Get user preferences
PUT    /api/v1/preferences                       # Update preferences
```

---

## Project Structure

```
smart-notification-manager/
├── PLAN.md                          # This file
├── docker-compose.yml               # Main Docker Compose file
├── docker-compose.v2.yml            # V2 additions (celery, nginx, etc.)
├── .env.example                     # Environment variables template
├── .gitignore
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt             # See below for contents
│   ├── alembic.ini
│   └── app/
│       ├── __init__.py
│       ├── main.py                  # FastAPI app entry point
│       ├── config.py                # Settings & config
│       ├── database.py              # DB connection
│       ├── models/                  # SQLAlchemy models
│       │   ├── __init__.py
│       │   ├── user.py              # V1
│       │   └── notification.py      # V1
│       │   ├── group.py             # V2
│       │   ├── event.py             # V2
│       │   ├── template.py          # V2
│       │   ├── audit.py             # V2
│       │   └── idempotency.py       # V2
│       ├── schemas/                 # Pydantic schemas
│       │   ├── __init__.py
│       │   ├── user.py              # V1
│       │   └── notification.py      # V1
│       │   ├── group.py             # V2
│       │   ├── event.py             # V2
│       │   └── template.py          # V2
│       ├── api/                     # API routes
│       │   ├── __init__.py
│       │   ├── deps.py              # V1 - Dependencies
│       │   ├── auth.py              # V1
│       │   └── notifications.py     # V1
│       │   ├── users.py             # V2
│       │   ├── groups.py            # V2
│       │   ├── events.py            # V2
│       │   ├── templates.py         # V2
│       │   └── health.py            # V1
│       ├── core/                    # Core utilities
│       │   ├── __init__.py
│       │   ├── security.py          # V1 - JWT, password hashing (Argon2)
│       │   └── websocket.py         # V1 - WebSocket manager
│       │   ├── exceptions.py        # V2 - Custom exceptions
│       │   └── websocket_v2.py      # V2 - WebSocket with Redis pub/sub
│       ├── services/                # Business logic
│       │   ├── __init__.py
│       │   └── notification_service.py  # V1
│       │   ├── delivery_service.py  # V2 - Channel strategy pattern
│       │   ├── email_service.py     # V2
│       │   └── scheduler_service.py # V2
│       ├── channels/                # V2 - Notification channel implementations
│       │   ├── __init__.py
│       │   ├── base.py              # Abstract NotificationChannel class
│       │   ├── web.py
│       │   └── email.py
│       └── celery_app/              # V2 - Celery configuration
│           ├── __init__.py
│           ├── celery_config.py
│           └── tasks.py             # Background tasks with retries
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── index.css
│       ├── api/                     # API client
│       │   ├── client.ts            # V1 - Axios instance with cookie auth
│       │   ├── auth.ts              # V1
│       │   └── notifications.ts     # V1
│       │   ├── groups.ts            # V2
│       │   ├── events.ts            # V2
│       │   └── templates.ts         # V2
│       ├── components/              # Reusable components
│       │   ├── ui/                  # Base UI components
│       │   ├── NotificationCard.tsx     # V1
│       │   └── NotificationList.tsx     # V1
│       │   ├── CreateNotificationModal.tsx  # V1
│       │   ├── GroupCard.tsx            # V2
│       │   ├── TemplatePicker.tsx         # V2
│       │   └── AnalyticsDashboard.tsx     # V2
│       ├── hooks/                   # Custom hooks
│       │   ├── useNotifications.ts  # V1
│       │   ├── useWebSocket.ts      # V1 - With reconnection + heartbeat
│       │   └── useAuth.ts           # V1
│       ├── pages/                   # Page components
│       │   ├── Login.tsx            # V1
│       │   ├── Dashboard.tsx        # V1 - Real-time notification feed
│       │   ├── Notifications.tsx    # V1 - List with filters
│       │   ├── Groups.tsx               # V2
│       │   ├── Events.tsx               # V2
│       │   ├── Templates.tsx            # V2
│       │   ├── Analytics.tsx            # V2
│       │   └── Settings.tsx             # V2
│       ├── stores/                  # Zustand stores
│       │   ├── authStore.ts         # V1
│       │   └── notificationStore.ts # V1
│       └── types/                   # TypeScript types
│           └── index.ts
│
├── nginx/                           # V2 - Reverse proxy
│   ├── Dockerfile
│   └── nginx.conf
│
└── scripts/
    ├── init-db.sql                  # Database initialization + indexes
    └── seed.py                      # Sample data + templates
```

### backend/requirements.txt
```txt
# === VERSION 1: Core Dependencies ===

# Core
fastapi==0.115.6
uvicorn[standard]==0.34.0
python-multipart==0.0.18

# Database
sqlalchemy[asyncio]==2.0.36
asyncpg==0.30.0
alembic==1.14.0

# Authentication & Security
PyJWT==2.10.1
argon2-cffi==23.1.0

# Rate Limiting
slowapi==0.1.9

# Validation
pydantic==2.10.4
pydantic-settings==2.7.0
email-validator==2.2.0

# WebSockets
websockets==14.1


# === VERSION 2: Additional Dependencies ===

# Redis & Background Tasks
redis[hiredis]==5.2.1
celery==5.4.0
flower==2.0.1

# HTTP Client (for integrations)
httpx==0.28.1
aiosmtplib==3.0.2

# Monitoring & Logging
python-json-logger==3.2.1
opentelemetry-api==1.29.0
```

---

## Docker Configuration

### Version 1 Services (docker-compose.yml)

```yaml
version: '3.9'

services:
  # Backend API
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/notifications
      - JWT_SECRET=${JWT_SECRET}
      - CORS_ORIGINS=http://localhost:3000,http://frontend:5173
    depends_on:
      - db
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # Frontend
  frontend:
    build: ./frontend
    ports:
      - "3000:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend
    command: npm run dev -- --host

  # PostgreSQL
  db:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=notifications
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql

volumes:
  postgres_data:
```

**V1 Services:**
- ✅ Backend (FastAPI)
- ✅ Frontend (React)
- ✅ PostgreSQL (Database)

---

### Version 2 Additional Services (docker-compose.v2.yml)

```yaml
version: '3.9'

services:
  # Redis (V2 - for Celery & WebSocket pub/sub)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Celery Worker (V2)
  celery-worker:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/notifications
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    command: celery -A app.celery_app.celery_config.celery_app worker --loglevel=info

  # Celery Beat (V2 - Scheduler)
  celery-beat:
    build: ./backend
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    command: celery -A app.celery_app.celery_config.celery_app beat --loglevel=info

  # Nginx (V2 - Reverse proxy for production)
  nginx:
    build: ./nginx
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
      - frontend
    profiles:
      - production

volumes:
  redis_data:
```

**V2 Additional Services:**
- Redis (Celery broker, WebSocket scaling)
- Celery Worker (background tasks)
- Celery Beat (scheduled tasks)
- Nginx (production reverse proxy)

**Run V2:** `docker-compose -f docker-compose.yml -f docker-compose.v2.yml up -d`

---

## Implementation Phases

# VERSION 1: Real-Time Notification Dashboard (MVP)

**Goal:** Create a functioning product where users can create notifications and receive them in real-time via a web dashboard.

---

### Phase 1.1: Project Setup & Infrastructure
- [ ] Initialize project structure
- [ ] Create Docker Compose configuration (backend, frontend, db)
- [ ] Set up PostgreSQL with initial schema (users, notifications, recipients)
- [ ] Create basic FastAPI app with health check endpoints
- [ ] Create basic React app with Vite + TailwindCSS
- [ ] Configure Alembic for migrations

**🛑 CHECKPOINT 1.1:** After Docker Compose setup
> ✅ All 3 services start successfully with `docker-compose up -d`
> ✅ Can access PostgreSQL from host (localhost:5432)
> ✅ Basic docker-compose.yml committed
> **Commit message:** `feat(v1): add Docker Compose configuration`

**🛑 CHECKPOINT 1.2:** After backend skeleton + health check
> ✅ `http://localhost:8000/health` returns `{"status": "healthy"}`
> ✅ FastAPI docs available at `http://localhost:8000/docs`
> ✅ Database connection working
> **Commit message:** `feat(v1): add FastAPI backend skeleton with health checks`

**🛑 CHECKPOINT 1.3:** After frontend skeleton
> ✅ Frontend accessible at `http://localhost:3000`
> ✅ Basic React app with TailwindCSS renders correctly
> ✅ Can communicate with backend API
> **Commit message:** `feat(v1): add React frontend with Vite and TailwindCSS`

---

### Phase 1.2: Authentication & Users
- [ ] Implement user model (users table)
- [ ] Create JWT authentication with HTTPOnly cookies
- [ ] Implement Argon2 password hashing
- [ ] Build login/register pages with form validation
- [ ] Implement auth endpoints: register, login, logout, me
- [ ] Add rate limiting to auth endpoints (slowapi) - 5 attempts/min

**🛑 CHECKPOINT 1.4:** After user model + security setup
> ✅ Alembic migration created and applied successfully
> ✅ Users table exists in database with all fields
> ✅ Password hashing with Argon2 works correctly
> **Commit message:** `feat(v1): add user model with Argon2 password hashing`

**🛑 CHECKPOINT 1.5:** After auth endpoints implemented
> ✅ Can register new user via POST `/api/v1/auth/register`
> ✅ Can login and receive HTTPOnly cookies
> ✅ Rate limiting active (5 attempts/min on login)
> ✅ Test with Swagger UI or curl
> **Commit message:** `feat(v1): implement JWT authentication with HTTPOnly cookies`

**🛑 CHECKPOINT 1.6:** After auth UI pages complete
> ✅ Login form works and redirects to dashboard
> ✅ Registration form with validation
> ✅ Auth state persists across page refreshes (cookies)
> ✅ Logout clears cookies and redirects to login
> **Commit message:** `feat(v1): add login/register pages with form validation`

---

### Phase 1.3: Notifications Core
- [ ] Implement notification models (notifications, notification_recipients tables)
- [ ] Create notification sending endpoint
- [ ] Build recipient resolution (notification goes to creating user)
- [ ] Add notification status tracking (pending → sent → delivered → read)
- [ ] Create notification list UI with basic filters (all, unread)

**🛑 CHECKPOINT 1.7:** After notification models + service
> ✅ Notification tables created (notifications, notification_recipients)
> ✅ Can create notification via POST `/api/v1/notifications`
> ✅ Notification appears in recipient's list
> ✅ Status tracking working (pending, sent, delivered)
> **Commit message:** `feat(v1): add notification models and creation endpoint`

---

### Phase 1.4: Real-Time WebSocket Delivery
- [ ] Implement WebSocket endpoint `/ws/notifications`
- [ ] Build WebSocket connection manager
- [ ] Send notification to user via WebSocket when created
- [ ] Frontend: WebSocket hook with reconnection logic
- [ ] Frontend: Real-time notification updates in UI

**🛑 CHECKPOINT 1.8:** After WebSocket implementation
> ✅ WebSocket connection established successfully
> ✅ Real-time notifications received when created
> ✅ Reconnection logic works (disconnect/reconnect)
> ✅ Heartbeat ping/pong active (30s interval)
> **Commit message:** `feat(v1): add WebSocket for real-time notifications`

**🛑 CHECKPOINT 1.9:** After notification list UI with real-time updates
> ✅ Notifications page shows list with pagination
> ✅ Can filter by status (unread, read, all)
> ✅ Can mark notification as read
> ✅ New notifications appear instantly via WebSocket (no refresh needed)
> ✅ Toast notification popup when new notification arrives
> **Commit message:** `feat(v1): add notification list with real-time updates`

---

### Phase 1.5: V1 Polish & Demo Ready
- [ ] Add basic error handling
- [ ] Add loading states in frontend
- [ ] Create seed data script (5 users, 50 notifications)
- [ ] Test complete user flow: register → login → create notification → receive
- [ ] Write README with V1 setup instructions

**🛑 CHECKPOINT 1.10:** V1 Complete - Ready for Demo
> ✅ All services running without errors
> ✅ Demo flow works end-to-end:
>   1. User registers and logs in
>   2. User creates notification with title, message, priority
>   3. Notification appears instantly in dashboard
>   4. User can mark as read
>   5. Notification list filters work
> ✅ Seed data script creates realistic demo data
> ✅ README.md has clear setup instructions
> ✅ `/api/v1/docs` shows API documentation
> **Commit message:** `feat(v1): complete MVP - real-time notification dashboard`

---

**🎉 VERSION 1 COMPLETE!**

**What we have:**
- ✅ Functioning product, not a prototype
- ✅ One core feature done well: real-time notification delivery
- ✅ All three components working: backend (FastAPI), database (PostgreSQL), frontend (React)
- ✅ Can deploy with `docker-compose up -d`
- ✅ Ready for use and testing

---

# VERSION 2: Smart Notification Management Platform

**Goal:** Build upon V1 by adding groups, scheduling, templates, analytics, and production deployment.

---

### Phase 2.1: Notification Groups
- [ ] Implement group models (notification_groups, group_members tables)
- [ ] Create group CRUD endpoints
- [ ] Implement member management (add/remove/roles: admin, member)
- [ ] Add audit logging for group operations
- [ ] Frontend: Groups page with list and details
- [ ] Frontend: Create group modal, manage members UI

**🛑 CHECKPOINT 2.1:** After groups backend + UI
> ✅ Can create/update/delete groups via API
> ✅ Can add/remove members to groups
> ✅ Groups page shows list of user's groups
> ✅ Can view group details and manage members
> **Commit message:** `feat(v2): add notification groups with member management`

---

### Phase 2.2: Events & Scheduled Notifications
- [ ] Implement event models (events table with scheduling)
- [ ] Create event CRUD endpoints
- [ ] Add Redis + Celery infrastructure to docker-compose
- [ ] Implement Celery Beat for scheduled notifications
- [ ] Frontend: Events page with date picker
- [ ] Frontend: Schedule notification for future time

**🛑 CHECKPOINT 2.2:** After events + scheduling
> ✅ Events table created with scheduling fields
> ✅ Can create event with scheduled_at timestamp
> ✅ Celery Beat running and visible in logs
> ✅ Scheduled notification delivered at correct time
> **Commit message:** `feat(v2): add events and scheduled notifications`

---

### Phase 2.3: Templates & User Preferences
- [ ] Create notification templates table
- [ ] Seed 3-5 pre-built templates (meeting reminder, system alert, task assignment)
- [ ] Implement template CRUD endpoints
- [ ] Create user preferences table
- [ ] Implement preferences endpoint (quiet hours, timezone, digest settings)
- [ ] Frontend: Template picker when creating notification
- [ ] Frontend: Settings page with preferences form

**🛑 CHECKPOINT 2.3:** After templates + preferences
> ✅ Templates table seeded with 3-5 pre-built templates
> ✅ Can select template when creating notification
> ✅ User preferences page with quiet hours toggle
> ✅ Timezone selection working
> **Commit message:** `feat(v2): add notification templates and user preferences`

---

### Phase 2.4: Advanced Notification Features
- [ ] Implement notification snooze functionality
- [ ] Add priority inbox (tabs: Important, Updates, All)
- [ ] Add "Mark all as read" bulk action
- [ ] Implement notification delivery retries (if WebSocket fails)
- [ ] Frontend: Snooze button on notifications
- [ ] Frontend: Priority inbox tabs

**🛑 CHECKPOINT 2.4:** After advanced features
> ✅ Can snooze notification for 1 hour / 1 day
> ✅ Priority inbox tabs filter notifications correctly
> ✅ "Mark all as read" works
> **Commit message:** `feat(v2): add advanced notification features (snooze, priority inbox)`

---

### Phase 2.5: Analytics Dashboard
- [ ] Create backend stats endpoint (notifications over time, by priority, read rate)
- [ ] Frontend: Install charting library (Recharts)
- [ ] Frontend: Analytics page with 3 charts:
  - Chart 1: Notifications sent/read over time (line chart)
  - Chart 2: Notifications by priority (pie chart)
  - Chart 3: Delivery success rate or peak hours (bar chart)

**🛑 CHECKPOINT 2.5:** After analytics dashboard
> ✅ Analytics page renders 3 charts
> ✅ Charts display correct data from backend
> ✅ Stats endpoint returns accurate statistics
> **Commit message:** `feat(v2): add analytics dashboard with charts`

---

### Phase 2.6: Production Deployment
- [ ] Add Nginx reverse proxy configuration
- [ ] Create production docker-compose (no --reload flags)
- [ ] Add comprehensive error handling (custom exception handlers)
- [ ] Implement request validation with Pydantic v2
- [ ] Add health checks (/health, /ready for all services)
- [ ] Write production README with deployment instructions
- [ ] Test complete V2 deployment

**🛑 CHECKPOINT 2.6:** V2 Production Deployment
> ✅ Production docker-compose works: `docker-compose -f docker-compose.yml -f docker-compose.v2.yml up -d`
> ✅ Nginx reverse proxy serves frontend and routes API
> ✅ Health checks pass for all services
> ✅ All services running without errors in production mode
> **Commit message:** `feat(v2): add production deployment with Nginx`

---

### Phase 2.7: Final Polish & Documentation
- [ ] Write comprehensive README with V1 and V2 instructions
- [ ] Add API documentation examples in /docs
- [ ] Create demo script/guide
- [ ] Optional: Write tests (pytest for backend, Vitest for frontend)
- [ ] Final review: complete user journey V1 + V2 features

**🛑 CHECKPOINT 2.7:** V2 Complete - Production Ready
> ✅ README.md complete with setup, deployment, and usage instructions
> ✅ API documentation available at /docs
> ✅ Demo flow showcases V2 features:
>   1. Create group and add members
>   2. Send notification to group
>   3. Schedule notification for future
>   4. Use template to create notification
>   5. View analytics dashboard
> ✅ Project is production-ready
> **Commit message:** `docs(v2): finalize documentation and complete smart notification platform`

---

**🎉 VERSION 2 COMPLETE!**

**What we have:**
- ✅ Enhanced V1 with groups, events, templates, scheduling
- ✅ User preferences and analytics
- ✅ Production deployment with Docker + Nginx
- ✅ Fully functional notification management platform
- ✅ Available for real-world use

---

## Recommendations & Critical Issues

### ✅ Applied Critical Fixes (Implemented in This Plan)

#### 1. Authentication Security - HTTPOnly Cookies + Argon2
- **JWT Storage**: Tokens stored in HTTPOnly, Secure, SameSite cookies (not localStorage)
- **Password Hashing**: Using `argon2-cffi` instead of bcrypt
- **Refresh Token Rotation**: Implements token rotation with old token invalidation
- **Rate Limiting**: `slowapi` applied to auth endpoints (5 attempts/minute)

**Implementation:**
```python
# backend/app/core/security.py
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import jwt
from datetime import datetime, timedelta

ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    try:
        ph.verify(hashed, password)
        return True
    except VerifyMismatchError:
        return False

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh", "jti": str(uuid4())})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
```

```python
# backend/app/api/auth.py - Cookie-based auth
@router.post("/login")
async def login(response: Response, login_data: LoginSchema, db: AsyncSession = Depends(get_db)):
    # ... validate user ...
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=1800,  # 30 minutes
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=604800,  # 7 days
    )
    return {"message": "Login successful"}
```

#### 2. Notification Delivery Guarantees - Idempotency + Retries
- **Idempotency Keys**: Each notification creation requires a unique key
- **Retry Logic**: Exponential backoff with Celery (3 retries: 1min, 5min, 15min)
- **Deduplication Table**: Tracks sent notifications to prevent duplicates

**Implementation:**
```python
# backend/app/models/notification.py
class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    key = Column(String, unique=True, nullable=False, index=True)
    notification_id = Column(UUID, ForeignKey("notifications.id"), nullable=True)
    created_by = Column(UUID, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

```python
# backend/app/services/notification_service.py
from fastapi import HTTPException
from sqlalchemy import select

async def create_notification(
    db: AsyncSession,
    data: NotificationCreateSchema,
    idempotency_key: str,
    user_id: UUID
) -> Notification:
    # Check for duplicate
    result = await db.execute(
        select(IdempotencyKey).where(IdempotencyKey.key == idempotency_key)
    )
    existing = result.scalar_one_or_none()
    if existing:
        if existing.notification_id:
            # Return existing notification (idempotent)
            notif_result = await db.execute(
                select(Notification).where(Notification.id == existing.notification_id)
            )
            return notif_result.scalar_one()
        raise HTTPException(status_code=409, detail="Request in progress")
    
    # Create idempotency record
    idem_record = IdempotencyKey(
        key=idempotency_key,
        created_by=user_id,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db.add(idem_record)
    await db.flush()
    
    # Create notification
    notification = Notification(**data.dict())
    db.add(notification)
    await db.flush()
    
    # Update idempotency record
    idem_record.notification_id = notification.id
    await db.commit()
    
    # Queue for delivery
    from app.celery_app.tasks import deliver_notification
    deliver_notification.apply_async(
        args=[str(notification.id)],
        retry=True,
        retry_policy={
            "max_retries": 3,
            "interval_start": 60,
            "interval_step": 240,
        }
    )
    
    return notification
```

```python
# backend/app/celery_app/tasks.py
from celery import Celery
import asyncio

celery_app = Celery("notification_tasks")

@celery_app.task(bind=True, max_retries=3)
def deliver_notification(self, notification_id: str):
    """Deliver notification with exponential backoff."""
    try:
        from app.services.delivery_service import deliver_sync
        result = deliver_sync(notification_id)
        return {"status": "delivered", "notification_id": notification_id}
    except Exception as exc:
        countdown = (2 ** self.request.retries) * 60  # 1min, 2min, 4min
        raise self.retry(exc=exc, countdown=countdown)
```

#### 3. Database Performance - Indexes + Connection Pooling
- **Composite Indexes**: Added to high-query field combinations
- **Connection Pooling**: Configured asyncpg pool with size limits
- **Query Optimization**: Selective loading with joinedload/deferred

**Implementation:**
```sql
-- backend/scripts/init-db.sql - Performance indexes
CREATE INDEX idx_notifications_user_status_created ON notifications(user_id, status, created_at DESC);
CREATE INDEX idx_notifications_event_id ON notifications(event_id) WHERE event_id IS NOT NULL;
CREATE INDEX idx_notification_recipients_user_status ON notification_recipients(user_id, delivery_status);
CREATE INDEX idx_notification_recipients_group ON notification_recipients(group_id) WHERE group_id IS NOT NULL;
CREATE INDEX idx_group_members_user ON group_members(user_id);
CREATE INDEX idx_events_scheduled ON events(scheduled_at) WHERE scheduled_at IS NOT NULL AND is_recurring = FALSE;
CREATE INDEX idx_idempotency_keys_key ON idempotency_keys(key) WHERE expires_at > NOW();
```

```python
# backend/app/database.py - Connection pooling
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,  # Max connections in pool
    max_overflow=10,  # Extra connections during spikes
    pool_timeout=30,  # Seconds to wait for connection
    pool_recycle=1800,  # Recycle connections every 30 min
    pool_pre_ping=True,  # Verify connection before use
    echo=settings.DEBUG,  # SQL logging in dev
)

async_session = async_sessionmaker(engine, expire_on_commit=False)
```

#### 4. WebSocket Scalability - Redis Pub/Sub
- **Redis Pub/Sub**: Enables horizontal scaling across multiple backend instances
- **Reconnection Logic**: Frontend implements exponential backoff
- **Heartbeat**: Ping/pong every 30 seconds to detect stale connections

**Implementation:**
```python
# backend/app/core/websocket.py
import redis.asyncio as redis
from fastapi import WebSocket
import asyncio
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.pubsub = None
        
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        
        # Subscribe to user's channel in Redis
        if not self.pubsub:
            self.pubsub = redis.Redis.from_url(settings.REDIS_URL).pubsub()
        await self.pubsub.subscribe(f"user:{user_id}")
        
    async def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if self.pubsub:
            await self.pubsub.unsubscribe(f"user:{user_id}")
    
    async def send_personal_message(self, message: dict, user_id: str):
        # Publish to Redis (scales across instances)
        await redis.Redis.from_url(settings.REDIS_URL).publish(
            f"user:{user_id}",
            json.dumps(message)
        )
    
    async def broadcast_from_redis(self):
        """Listen to Redis pub/sub and forward to WebSocket connections."""
        while True:
            if self.pubsub:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                if message and message["type"] == "message":
                    data = json.loads(message["data"])
                    user_id = data.get("user_id")
                    if user_id in self.active_connections:
                        try:
                            await self.active_connections[user_id].send_json(data)
                        except Exception:
                            await self.disconnect(user_id)
            await asyncio.sleep(0.01)

manager = ConnectionManager()
```

```typescript
// frontend/src/hooks/useWebSocket.ts - Reconnection logic
import { useEffect, useRef, useState } from 'react';

export function useNotificationWebSocket(onMessage: (data: any) => void) {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const connect = () => {
      const ws = new WebSocket(
        `${import.meta.env.VITE_WS_URL}/ws/notifications`
      );
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        reconnectAttempts.current = 0;
        
        // Start heartbeat
        const heartbeat = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000);
        ws.onclose = () => clearInterval(heartbeat);
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'pong') return;  // Ignore heartbeat
        onMessage(data);
      };

      ws.onclose = () => {
        setIsConnected(false);
        // Exponential backoff: 1s, 2s, 4s, 8s, max 30s
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current++), 30000);
        setTimeout(connect, delay);
      };
    };

    connect();
    return () => wsRef.current?.close();
  }, [onMessage]);

  return isConnected;
}
```

#### 5. Notification Channel Abstraction - Strategy Pattern
- **Interface-Based Design**: Easy to add email, SMS, push, webhooks
- **Channel Registry**: Dynamic channel selection based on user preferences
- **Fallback Logic**: Automatic fallback to alternative channels

**Implementation:**
```python
# backend/app/services/channels/base.py
from abc import ABC, abstractmethod

class NotificationChannel(ABC):
    """Base class for notification channels."""
    
    @abstractmethod
    async def send(self, recipient: User, notification: Notification) -> bool:
        """Send notification. Returns True if successful."""
        pass
    
    @abstractmethod
    def get_channel_name(self) -> str:
        pass

# backend/app/services/channels/web.py
class WebChannel(NotificationChannel):
    async def send(self, recipient: User, notification: Notification) -> bool:
        from app.core.websocket import manager
        try:
            await manager.send_personal_message(
                {
                    "type": "notification",
                    "id": str(notification.id),
                    "title": notification.title,
                    "message": notification.message,
                    "priority": notification.priority,
                },
                str(recipient.id)
            )
            return True
        except Exception:
            return False
    
    def get_channel_name(self) -> str:
        return "web"

# backend/app/services/channels/email.py
class EmailChannel(NotificationChannel):
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        # ... email config ...
    
    async def send(self, recipient: User, notification: Notification) -> bool:
        # Implementation using aiosmtplib or similar
        pass
    
    def get_channel_name(self) -> str:
        return "email"

# backend/app/services/delivery_service.py
from app.services.channels.base import NotificationChannel

class DeliveryService:
    def __init__(self):
        self.channels: dict[str, NotificationChannel] = {}
    
    def register_channel(self, channel: NotificationChannel):
        self.channels[channel.get_channel_name()] = channel
    
    async def deliver(self, notification: Notification, recipient: User, preferences: UserPreferences):
        """Deliver via user's enabled channels with fallback."""
        enabled_channels = []
        if preferences.web_enabled:
            enabled_channels.append("web")
        if preferences.email_enabled:
            enabled_channels.append("email")
        
        delivered = False
        failed_channels = []
        
        for channel_name in enabled_channels:
            if channel_name in self.channels:
                success = await self.channels[channel_name].send(recipient, notification)
                if success:
                    delivered = True
                    break
                failed_channels.append(channel_name)
        
        if not delivered:
            raise DeliveryFailedError(
                f"Failed to deliver via channels: {failed_channels}"
            )

# Register channels at startup
delivery_service = DeliveryService()
delivery_service.register_channel(WebChannel())
delivery_service.register_channel(EmailChannel())
```

### 💡 Recommendations to Make Project More "Useful"

These additions keep the project **simple to build** but create the **impression of a production-ready, valuable tool**:

#### 🎯 High Impact, Low Effort

1. **Notification Templates Library** ⭐ (Best ROI)
   - Pre-built templates for common scenarios (meeting reminders, system alerts, task assignments)
   - Users can customize & save their own templates
   - **Impression**: "This is a mature platform, not a toy"
   - **Effort**: 2-3 hours (just a templates table + UI)

2. **Smart Quiet Hours + Timezone Awareness**
   - Auto-detect user timezone, don't send notifications during sleep hours
   - "Do Not Disturb" toggle with schedule
   - **Impression**: "Respects user's time and attention"
   - **Effort**: 1-2 hours

3. **Notification Digests** ⭐
   - Daily/weekly summary emails: "You received 23 notifications today"
   - Bundles low-priority notifications to reduce noise
   - **Impression**: "Actually solves notification fatigue"
   - **Effort**: 2-3 hours (Celery Beat + email template)

4. **Quick Actions on Notifications**
   - "Snooze for 1 hour / 1 day" button
   - "Mark all as read" with one click
   - "Unsubscribe from this type" option
   - **Impression**: "User-centric design"
   - **Effort**: 1-2 hours

#### 🚀 Medium Effort, High Value

5. **Priority Inbox** (like email)
   - Tabs: "Important", "Updates", "Promotions", "Social"
   - Auto-categorize based on sender/priority
   - **Impression**: "Smart notification management"
   - **Effort**: 3-4 hours

6. **Real-Time Activity Feed**
   - Dashboard showing live notification stream
   - Filters by group, priority, date range
   - **Impression**: "Command center for notifications"
   - **Effort**: 2-3 hours (just WebSocket + filters)

7. **Team Collaboration Features**
   - @mention users in notifications
   - Comment threads on notifications
   - Assign notifications to team members
   - **Impression**: "Built for teams, not just individuals"
   - **Effort**: 4-5 hours

8. **Notification Analytics Dashboard** ⭐
   - Charts: notifications sent/delivered/read over time
   - Peak hours heatmap
   - Average read time per priority
   - **Impression**: "Data-driven notification platform"
   - **Effort**: 3-4 hours (Recharts + 2-3 API endpoints)

#### 💎 "Wow Factor" Features

9. **Smart Notification Routing**
   - Critical alerts bypass quiet hours
   - Escalation: if not read in 10min, notify via email too
   - **Impression**: "Intelligent, context-aware system"
   - **Effort**: 2-3 hours

10. **One-Click Integrations** (Fake it for demo)
    - GitHub webhook integration (notify on PR/review)
    - Slack bridge (mirror notifications to Slack)
    - Calendar reminders (sync with Google Calendar)
    - **Impression**: "Part of your workflow, not another app"
    - **Effort**: 2-3 hours per integration (can use mock data)

### 📦 Recommended Feature Set for Maximum Impact

For a hackathon/demo, implement these to maximize the "useful" impression:

```
MUST HAVE (Core functionality):
✅ User auth + groups + events
✅ Real-time notifications (WebSocket)
✅ Notification creation & delivery
✅ Basic UI (list, create, mark as read)

SHOULD HAVE (Creates "useful" impression):
⭐ Notification templates (3-5 pre-built)
⭐ Daily digest feature
⭐ Quiet hours + timezone
⭐ Quick actions (snooze, bulk mark)
⭐ Simple analytics (3 charts)

NICE TO HAVE (If time permits):
- Priority inbox tabs
- @mention support
- One mock integration (GitHub/Slack)
```

---

### 🔧 Additional Critical Fixes Applied

#### 6. Soft Deletes for Critical Tables
```python
# Added to all main models
class SoftDeleteMixin:
    deleted_at = Column(DateTime, nullable=True, index=True)
    
    @property
    def is_deleted(self):
        return self.deleted_at is not None
```

#### 7. Audit Logging
```python
# backend/app/models/audit.py
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)  # 'create', 'update', 'delete', 'send'
    entity_type = Column(String, nullable=False)  # 'notification', 'group', 'event'
    entity_id = Column(UUID, nullable=False)
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### 8. Rate Limiting
```python
# backend/app/main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, ...):
    ...

@router.post("/notifications")
@limiter.limit("30/minute")
async def create_notification(request: Request, ...):
    ...
```

#### 9. Consistent Error Handling
```python
# backend/app/main.py
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "details": exc.errors()
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        }
    )
```

#### 10. Health Checks
```python
# backend/app/api/health.py
@router.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "healthy"}

@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Check if service is ready (DB, Redis connected)."""
    try:
        await db.execute(text("SELECT 1"))
        redis_client = redis.Redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        return {"status": "ready", "database": "connected", "redis": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
```

---

## Quick Start Commands

### Version 1: Real-Time Notification Dashboard

```bash
# Clone and setup
git clone <repo>
cd smart-notification-manager
cp .env.example .env

# Start V1 services (backend, frontend, PostgreSQL)
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Seed data (optional)
docker-compose exec backend python scripts/seed.py

# Access services
# Frontend:    http://localhost:3000
# Backend API: http://localhost:8000
# API Docs:    http://localhost:8000/docs
# PostgreSQL:  localhost:5432
```

---

### Version 2: Smart Notification Platform

```bash
# Start V1 + V2 services (adds Redis, Celery, Nginx)
docker-compose -f docker-compose.yml -f docker-compose.v2.yml up -d

# Access additional services
# Redis:       localhost:6379
# Celery:      (internal - check logs)
# Nginx:       http://localhost:80 (production mode)

# View Celery worker logs
docker-compose -f docker-compose.yml -f docker-compose.v2.yml logs -f celery-worker

# View scheduled tasks
docker-compose -f docker-compose.yml -f docker-compose.v2.yml logs -f celery-beat
```

---

### Development Commands

```bash
# Run backend locally (outside Docker)
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run frontend locally
cd frontend
npm run dev

# Create new database migration
cd backend
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

---

## Environment Variables (.env.example)

```env
# Database
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_NAME=notifications

# JWT
JWT_SECRET=your_jwt_secret_key_change_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis
REDIS_URL=redis://redis:6379/0

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Frontend
VITE_API_URL=http://localhost:8000
```

---

*Last updated: April 6, 2026*
