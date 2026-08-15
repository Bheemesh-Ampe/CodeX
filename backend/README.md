# CivicFix Backend API

FastAPI backend and SQLite database layer for **CivicFix** — a civic issue reporting platform connecting residents and municipal administrators.

---

## Database Architecture (SQLAlchemy + SQLite)

### 1. `User` Model (`users` table)
- `id`: Integer Primary Key
- `name`: String
- `email`: String (Unique, Indexed)
- `role`: String (`resident` | `admin`, Indexed)
- `created_at`: DateTime
- **Relationships**:
  - `issues_created`: One-to-Many with `Issue` (`Issue.created_by`)
  - `issues_assigned`: One-to-Many with `Issue` (`Issue.assigned_to`)
  - `issue_updates`: One-to-Many with `IssueUpdate` (`IssueUpdate.updated_by`)

### 2. `Issue` Model (`issues` table)
- `id`: Integer Primary Key
- `title`: String (Indexed)
- `description`: Text
- `category`: String (Indexed)
- `status`: String (Default: `"REPORTED"`, Indexed)
- `priority`: String (Default: `"MEDIUM"`, Indexed)
- `latitude`: Float (Indexed)
- `longitude`: Float (Indexed)
- `address`: String (Nullable)
- `image_path`: String (Nullable)
- **AI Fields (Groq integration ready)**:
  - `ai_summary`: Text
  - `ai_category`: String
  - `ai_priority`: String
  - `ai_suggested_action`: Text
- `created_by`: Foreign Key (`users.id`, Indexed)
- `assigned_to`: Foreign Key (`users.id`, Indexed)
- `created_at`: DateTime (Indexed)
- `updated_at`: DateTime
- **Composite Indexes**:
  - `ix_issues_location` on `(latitude, longitude)` for high-performance map bounding box & radius queries
  - `ix_issues_status_category` on `(status, category)`
- **Relationships**:
  - `creator`: Belongs to `User`
  - `assignee`: Belongs to `User`
  - `updates`: One-to-Many with `IssueUpdate` (Cascade delete on issue deletion)

### 3. `IssueUpdate` Model (`issue_updates` table)
- `id`: Integer Primary Key
- `issue_id`: Foreign Key (`issues.id`, Indexed, Cascade Delete)
- `status`: String (Indexed)
- `comment`: Text (Nullable)
- `updated_by`: Foreign Key (`users.id`, Indexed)
- `created_at`: DateTime (Indexed)
- **Relationships**:
  - `issue`: Belongs to `Issue`
  - `user`: Belongs to `User`

---

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app initialization, CORS, lifespan & static mounting
│   ├── config.py            # Pydantic Settings & environment variables
│   ├── database/            # SQLAlchemy session & SQLite setup
│   │   ├── __init__.py
│   │   └── session.py       # Engine, Base, get_db, init_db
│   ├── models/              # Database models
│   │   ├── __init__.py
│   │   ├── user.py          # User model (resident / admin)
│   │   ├── issue.py         # Issue model (status="REPORTED", priority="MEDIUM", coordinates)
│   │   ├── issue_update.py  # IssueUpdate model (audit & comment trail)
│   │   └── report.py        # Backward-compatibility alias
│   ├── schemas/             # Pydantic validation & response schemas
│   │   ├── __init__.py
│   │   ├── health.py
│   │   ├── user.py
│   │   ├── issue.py
│   │   ├── issue_update.py
│   │   └── report.py
│   ├── routes/              # Modular API endpoints
│   │   ├── __init__.py
│   │   ├── api.py           # Master API router aggregator
│   │   ├── health.py        # GET /api/health
│   │   ├── users.py         # /api/users
│   │   ├── issues.py        # /api/issues
│   │   └── reports.py       # /api/reports (legacy alias)
│   ├── services/            # Business logic & database operations
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── issue_service.py
│   │   └── report_service.py
│   └── utils/               # Synthetic demo seed data generator
│       ├── __init__.py
│       └── seed_data.py
├── uploads/                 # Static file upload storage
│   └── .gitkeep
├── tests/                   # Pytest test suite
│   ├── __init__.py
│   ├── test_models.py       # Database models & relationship unit tests
│   ├── test_issues.py       # Issues & users API endpoint tests
│   ├── test_health.py       # Health check tests
│   └── test_reports.py      # Legacy reports backward compatibility tests
├── requirements.txt         # Pinned lightweight dependencies
├── .env.example             # Example configuration
├── .env                     # Local environment settings
└── .gitignore
```

---

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Backend Server
```bash
uvicorn app.main:app --reload --port 8000
```

The database tables (`users`, `issues`, `issue_updates`) are **automatically created and seeded** on server startup.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Healthcheck verifying API & SQLite database connection |
| `POST` | `/api/issues` | Create a new civic issue (with coordinates & default `status="REPORTED"`) |
| `GET` | `/api/issues` | List issues with search, category, status, priority & user filters |
| `GET` | `/api/issues/{id}` | Get full issue details (with creator, assignee, and update history) |
| `PATCH` | `/api/issues/{id}/status` | Admin: Update issue status & priority (records an `IssueUpdate`) |
| `POST` | `/api/issues/{id}/updates` | Append a progress comment/update to an issue |
| `PUT` | `/api/issues/{id}` | Update issue details |
| `DELETE` | `/api/issues/{id}` | Delete an issue (cascades to updates) |
| `GET` | `/api/issues/stats/summary` | Aggregate issue counts for admin dashboard |
| `POST` | `/api/issues/seed` | Seed/re-seed synthetic demo issues and users |
| `GET` | `/api/users` | List registered residents and administrators |
| `POST` | `/api/users` | Register a new user |
| `GET` | `/docs` | Interactive Swagger API documentation |

---

## Running Tests

```bash
pytest
```
