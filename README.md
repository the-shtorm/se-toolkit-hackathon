# Smart Notification Manager

A full-stack notification management system with FastAPI backend, React frontend, and PostgreSQL database.

## Version 1: Real-Time Notification Dashboard (MVP)

A functioning notification system with real-time WebSocket delivery.

### Features
- ✅ User authentication (register/login)
- ✅ Create notifications with priority levels
- ✅ Real-time delivery via WebSocket
- ✅ Notification list with mark-as-read
- ✅ Clean, responsive UI with TailwindCSS

### Tech Stack
- **Backend**: FastAPI + SQLAlchemy (async) + Alembic
- **Frontend**: React 18 + TypeScript + Vite + TailwindCSS
- **Database**: PostgreSQL 16
- **Infrastructure**: Docker & Docker Compose

## Quick Start

### Prerequisites
- Docker & Docker Compose
- (Optional) WSL with ZSH and UV for local Python development

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smart-notification-manager
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the services**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/v1/health
   - PostgreSQL: localhost:5432

### Local Development (WSL with ZSH + UV)

If you prefer to run the backend locally:

```bash
# Navigate to backend directory
cd backend

# Create virtual environment with UV
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Run the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Services

| Service    | Port  | Description              |
|------------|-------|--------------------------|
| backend    | 8000  | FastAPI API server       |
| frontend   | 3000  | React development server |
| db         | 5432  | PostgreSQL database      |

## Project Structure

```
smart-notification-manager/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Security, WebSocket manager
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── config.py       # Settings
│   │   ├── database.py     # DB connection
│   │   └── main.py         # FastAPI app
│   ├── alembic/            # Database migrations
│   ├── Dockerfile
│   ├── requirements.txt
│   └── alembic.ini
├── frontend/               # React frontend
│   ├── src/
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.ts
├── scripts/                # Database & utility scripts
│   └── init-db.sql
├── docker-compose.yml
├── .env.example
└── PLAN.md
```

## API Endpoints (V1)

### Health Check
- `GET /api/v1/health` - Service health status
- `GET /api/v1/` - Root endpoint

### Authentication (Coming Soon)
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

### Notifications (Coming Soon)
- `GET /api/v1/notifications`
- `POST /api/v1/notifications`
- `PUT /api/v1/notifications/{id}/read`

### WebSocket (Coming Soon)
- `WS /ws/notifications` - Real-time notification stream

## Development Workflow

### Backend Changes
The backend auto-reloads when Python files change (uvicorn --reload).

### Frontend Changes
The frontend auto-reloads via Vite's HMR.

### Database Migrations

```bash
# Enter the backend container
docker-compose exec backend bash

# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Checkpoint 1.1 Status

✅ All 3 services start successfully with `docker-compose up -d`  
✅ Can access PostgreSQL from host (localhost:5432)  
✅ Basic docker-compose.yml committed  
✅ Health check endpoint working  
✅ Frontend accessible and displaying backend status

## License

See [LICENSE](LICENSE) for details.
