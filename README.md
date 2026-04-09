# Smart Notification Manager

A full-stack notification management system with FastAPI backend, React frontend, PostgreSQL, Redis, and Celery for scheduled/real-time delivery.

## Features

### V1: Real-Time Notification Dashboard ✅
- User authentication (register/login) with JWT + HTTP-only cookies
- Rate limiting (5 attempts/min) on auth endpoints
- Argon2 password hashing
- Create notifications with priority levels (low, medium, high, critical)
- Real-time delivery via WebSocket with heartbeat ping/pong
- Notification list with pagination, filtering, and mark-as-read
- Toast popup for new notifications
- WebSocket reconnection with exponential backoff
- Quick snooze menu (15m, 1h, 4h, 1d, 1w) on individual notifications
- Clean, responsive UI with TailwindCSS

### V2: Smart Notification Management Platform ✅
- **Groups** — Create notification groups, manage members (admin/member roles), send to entire groups
- **Events** — Schedule notifications for future dates, Celery worker fires at the correct time
- **Templates** — Create/edit/delete reusable notification templates with categories, public/private visibility
- **Preferences** — Per-user settings: channel toggles (web/email/SMS), quiet hours, daily limits, timezone, digest frequency
- **Analytics** — Interactive dashboard with charts (Recharts): daily activity line chart, priority distribution pie chart, read vs unread bar chart
- **Snooze** — Quick snooze presets + custom snooze times, list active snoozes, unsnooze
- **Production Deployment** — Nginx reverse proxy, Celery Beat scheduler, Flower monitoring dashboard

---

## Quick Start

### Prerequisites
- Docker & Docker Compose

### Setup

1. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

2. **Start all services (development)**
   ```bash
   docker compose up -d --build
   ```

3. **Start production deployment (with Nginx + Celery Beat)**
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.v2.yml --profile production up -d
   ```

4. **Access the application**
   - **Frontend (dev)**: http://localhost:3000
   - **Frontend (prod via Nginx)**: http://localhost:80
   - **API Docs**: http://localhost:8000/docs (dev) or http://localhost/docs (prod)
   - **Health**: http://localhost:8000/health or http://localhost/health

---

## Services

### Development (V1 + V2)

| Service         | Port  | Description                    |
|-----------------|-------|--------------------------------|
| frontend        | 3000  | React Vite dev server          |
| backend         | 8000  | FastAPI API server             |
| db              | 5432  | PostgreSQL database            |
| redis           | 6379  | Redis (Celery broker/cache)    |
| celery-worker   | —     | Background task processor      |

### Production (V2 extras)

| Service         | Port  | Description                    |
|-----------------|-------|--------------------------------|
| nginx           | 80    | Reverse proxy for frontend/API |
| celery-beat     | —     | Scheduled task scheduler       |
| flower          | 5555  | Celery monitoring dashboard    |

---

## API Endpoints

### Health
| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/health` | Simple health check |
| `GET`  | `/api/v1/health` | Detailed health with service info |

### Authentication
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/auth/register` | Register new user |
| `POST` | `/api/v1/auth/login` | Login (returns token + sets HTTP-only cookie) |
| `POST` | `/api/v1/auth/logout` | Logout and clear cookie |
| `GET`  | `/api/v1/auth/me` | Get current user info |
| `GET`  | `/api/v1/auth/ws-token` | Get JWT token for WebSocket auth |

### Notifications
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/notifications` | Create notification |
| `GET`  | `/api/v1/notifications` | List (paginated, filterable by status) |
| `GET`  | `/api/v1/notifications/{id}` | Get by ID |
| `PUT`  | `/api/v1/notifications/{id}/read` | Mark as read |
| `PUT`  | `/api/v1/notifications/read-all` | Mark all as read |
| `GET`  | `/api/v1/notifications/stats` | Full analytics (total, read rate, by priority, daily activity) |

### Groups
| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/api/v1/groups` | List user's groups |
| `POST` | `/api/v1/groups` | Create group |
| `GET`  | `/api/v1/groups/{id}` | Get group details |
| `PUT`  | `/api/v1/groups/{id}` | Update group |
| `DELETE` | `/api/v1/groups/{id}` | Delete group |
| `POST` | `/api/v1/groups/{id}/members` | Add member |
| `DELETE` | `/api/v1/groups/{id}/members/{user_id}` | Remove member |

### Events
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/events` | Create scheduled event (queues Celery task) |
| `GET`  | `/api/v1/events` | List events (paginated) |
| `GET`  | `/api/v1/events/{id}` | Get event details |
| `PUT`  | `/api/v1/events/{id}` | Update event (revokes + reschedules Celery task) |
| `DELETE` | `/api/v1/events/{id}` | Delete event (revokes Celery task) |

### Templates
| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/api/v1/templates` | List templates (public + user's own) |
| `POST` | `/api/v1/templates` | Create template |
| `GET`  | `/api/v1/templates/{id}` | Get template |
| `PUT`  | `/api/v1/templates/{id}` | Update template (owner only) |
| `DELETE` | `/api/v1/templates/{id}` | Delete template (owner only) |

### Preferences
| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/api/v1/preferences` | Get user preferences (auto-creates defaults) |
| `POST` | `/api/v1/preferences` | Create initial preferences |
| `PUT`  | `/api/v1/preferences` | Update preferences |

### Snoozes
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/snoozes` | Snooze notification until specific time |
| `POST` | `/api/v1/snoozes/quick?notification_id=&duration=` | Quick snooze (15m, 1h, 4h, 1d, 1w) |
| `GET`  | `/api/v1/snoozes` | List active snoozes |
| `GET`  | `/api/v1/snoozes/options` | Get available quick snooze options |
| `DELETE` | `/api/v1/snoozes/{notification_id}` | Remove snooze (wake up now) |

### WebSocket
| Protocol | Path | Description |
|----------|------|-------------|
| `WS`     | `/ws/notifications?token=<jwt>` | Real-time notification stream |

---

## Frontend Pages

| Page | URL | Description |
|------|-----|-------------|
| Notifications | `/notifications` | Real-time notification feed with filters, snooze, mark-as-read |
| Groups | `/groups` | Create/manage notification groups and members |
| Events | `/events` | Schedule notifications for future delivery |
| Templates | `/templates` | Browse, create, and manage notification templates |
| Analytics | `/analytics` | Interactive charts: activity, priority distribution, read rate |
| Settings | `/settings` | User preferences: channels, quiet hours, timezone, digests |

---

## Tech Stack

### Backend
- **Python 3.12** / **FastAPI 0.115** / **Pydantic v2**
- **SQLAlchemy 2.0** (async) + **Alembic** (migrations)
- **Celery + Redis** — background task processing
- **Argon2** password hashing, **PyJWT** authentication
- **SlowApi** rate limiting, **asyncpg** PostgreSQL driver
- **psycopg2-binary** — sync PostgreSQL driver for Celery workers

### Frontend
- **React 18** + **TypeScript** + **Vite**
- **TailwindCSS** — styling
- **Zustand** — state management
- **React Router** — navigation
- **Recharts** — analytics charts
- **Axios** — HTTP client with cookie auth

### Infrastructure
- **PostgreSQL 16** — primary database
- **Redis 7** — Celery broker, WebSocket pub/sub
- **Docker & Docker Compose** — containerization
- **Nginx 1.25** — production reverse proxy

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

## Development

### Database migrations
```bash
# Create new migration
docker compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker compose exec backend alembic upgrade head

# Rollback one migration
docker compose exec backend alembic downgrade -1
```

### Testing
```bash
pip install requests websocket-client
python test_api.py          # Full API test suite
python test_scheduled_event.py  # Scheduled event delivery test
```

### API testing with curl
```bash
# Login (saves cookie)
curl -c cookies.txt -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!"}'

# List notifications (uses saved cookie)
curl -b cookies.txt http://localhost:8000/api/v1/notifications

# Create notification
curl -b cookies.txt -X POST http://localhost:8000/api/v1/notifications \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","message":"Hello","priority":"high"}'
```

### View Celery worker logs
```bash
docker compose logs -f celery-worker
```

### View Celery Beat logs (V2)
```bash
docker compose -f docker-compose.yml -f docker-compose.v2.yml logs -f celery-beat
```

---

## Project Structure

```
hackaton/
├── backend/
│   ├── app/
│   │   ├── api/             # auth, notifications, groups, events,
│   │   │                    # templates, preferences, snoozes,
│   │   │                    # broadcast, websocket, health, users
│   │   ├── core/            # security.py, websocket.py
│   │   ├── models/          # user, notification, group, event,
│   │   │                    # template, preference, snooze
│   │   ├── schemas/         # Matching Pydantic schemas
│   │   ├── services/        # notification_service.py
│   │   ├── celery_app.py    # Celery app + scheduled notification task
│   │   ├── config.py        # Environment settings
│   │   ├── database.py      # Async DB engine & session
│   │   └── main.py          # FastAPI app entry point
│   ├── alembic/             # Database migrations
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pip.conf             # PyPI mirror config
├── frontend/
│   ├── src/
│   │   ├── api/             # client, auth, notifications, groups,
│   │   │                    # events, templates, preferences, snoozes, ws
│   │   ├── components/      # NavBar.tsx
│   │   ├── hooks/           # useAuth, useWebSocket
│   │   ├── pages/           # Login, Register, Notifications, Groups,
│   │   │                    # Events, Templates, Analytics, Settings
│   │   ├── stores/          # authStore, notificationStore
│   │   └── types/           # TypeScript interfaces
│   ├── Dockerfile
│   └── vite.config.ts
├── nginx/
│   ├── Dockerfile
│   └── nginx.conf           # Production reverse proxy config
├── scripts/
│   └── init-db.sql
├── docker-compose.yml       # Main compose (dev)
├── docker-compose.v2.yml    # V2 additions (nginx, celery-beat, flower)
├── .env.example
├── test_api.py              # Comprehensive API test suite
└── test_scheduled_event.py  # Scheduled event delivery test
```

---

## Environment Variables

```env
# JWT
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DB_USER=user
DB_PASSWORD=password
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/notifications

# Redis
REDIS_URL=redis://redis:6379/0

# CORS
CORS_ORIGINS=http://localhost:8000,http://localhost:3000,http://localhost:80

# Application
APP_NAME=Smart Notification Manager
APP_VERSION=2.0.0
DEBUG=true
ENVIRONMENT=development
```

---

## License

See [LICENSE](LICENSE) for details.
