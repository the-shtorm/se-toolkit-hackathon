# Smart Notification Manager

A full-stack notification management system with FastAPI backend, React frontend, and PostgreSQL database.

## Version 1: Real-Time Notification Dashboard (MVP) ✅ COMPLETE

A functioning real-time notification system with WebSocket delivery.

### Features
- ✅ User authentication (register/login) with JWT + HTTP-only cookies
- ✅ Rate limiting (5 attempts/min) on auth endpoints
- ✅ Argon2 password hashing
- ✅ Create notifications with priority levels (low, medium, high, critical)
- ✅ Real-time delivery via WebSocket with 30s heartbeat ping/pong
- ✅ Notification list with pagination, filtering, and mark-as-read
- ✅ Toast popup for new notifications
- ✅ WebSocket reconnection with exponential backoff
- ✅ Clean, responsive UI with TailwindCSS

### Tech Stack
- **Backend**: FastAPI + SQLAlchemy (async) + SlowApi (rate limiting)
- **Frontend**: React 18 + TypeScript + Vite + TailwindCSS + Zustand
- **Database**: PostgreSQL 16
- **Real-time**: WebSockets with connection manager
- **Infrastructure**: Docker & Docker Compose

---

## Quick Start

### Prerequisites
- Docker & Docker Compose

### Setup

1. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

2. **Start all services**
   ```bash
   docker compose up -d --build
   ```

3. **Seed demo data (5 users, 50 notifications)**
   ```bash
   docker compose exec backend sh -c "cd /app && PYTHONPATH=/app python scripts/seed.py"
   ```

4. **Access the application**
   - **Frontend**: http://localhost:3000
   - **API Docs**: http://localhost:8000/docs
   - **Health**: http://localhost:8000/api/v1/health

### Demo Credentials

| Username | Email              | Password   |
|----------|--------------------|------------|
| alice    | alice@demo.com     | demo1234   |
| bob      | bob@demo.com       | demo1234   |
| charlie  | charlie@demo.com   | demo1234   |
| diana    | diana@demo.com     | demo1234   |
| eve      | eve@demo.com       | demo1234   |

### Services

| Service    | Port  | Description               |
|------------|-------|---------------------------|
| frontend   | 3000  | React Vite dev server     |
| backend    | 8000  | FastAPI API server        |
| db         | 5432  | PostgreSQL database       |

---

## API Endpoints (V1)

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
| `GET`  | `/api/v1/notifications/stats` | Get unread count |

### WebSocket
| Protocol | Path | Description |
|----------|------|-------------|
| `WS`     | `/ws/notifications?token=<jwt>` | Real-time notification stream |

---

## Project Structure

```
hackaton/
├── backend/
│   ├── app/
│   │   ├── api/             # Routes: auth, notifications, websocket, health
│   │   ├── core/            # security.py, websocket.py (ConnectionManager)
│   │   ├── models/          # SQLAlchemy: user.py, notification.py
│   │   ├── schemas/         # Pydantic: user.py, notification.py
│   │   ├── services/        # notification_service.py
│   │   ├── config.py        # Environment settings
│   │   ├── database.py      # Async DB engine & session
│   │   └── main.py          # FastAPI app entry point
│   ├── scripts/
│   │   └── seed.py          # Demo data generator
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/             # Axios client, auth, notifications, ws
│   │   ├── hooks/           # useAuth, useWebSocket
│   │   ├── pages/           # Login, Register, Notifications
│   │   ├── stores/          # Zustand: authStore, notificationStore
│   │   └── types/           # TypeScript interfaces
│   ├── Dockerfile
│   └── vite.config.ts
├── scripts/
│   └── init-db.sql
├── docker-compose.yml
├── .env.example
└── PLAN.md
```

---

## Development

### Backend auto-reload
Changes to Python files trigger uvicorn reload automatically.

### Frontend HMR
Vite hot module replacement updates the UI instantly.

### Reseed database
```bash
docker compose exec backend sh -c "cd /app && PYTHONPATH=/app python scripts/seed.py"
```

### API testing with Swagger UI
1. Open http://localhost:8000/docs
2. Register a user via `POST /api/v1/auth/register`
3. Login via `POST /api/v1/auth/login` — copy `access_token` from response
4. Use the `/api/v1/auth/ws-token` endpoint to get a WebSocket token
5. All subsequent requests auto-authenticate via the HTTP-only cookie

### API testing with curl
```bash
# Login (saves cookie)
curl -c cookies.txt -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@demo.com","password":"demo1234"}'

# List notifications (uses saved cookie)
curl -b cookies.txt http://localhost:8000/api/v1/notifications

# Create notification
curl -b cookies.txt -X POST http://localhost:8000/api/v1/notifications \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","message":"Hello","priority":"high"}'
```

---

## License

See [LICENSE](LICENSE) for details.
