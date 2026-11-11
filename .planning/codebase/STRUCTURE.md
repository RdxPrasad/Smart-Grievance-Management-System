# Codebase Structure

**Analysis Date:** 2026-11-07

## Directory Layout

```
Smart Grievance Management System/
├── backend/                  # Backend application root
│   ├── app/                  # FastAPI core package
│   │   ├── routers/          # Route controllers and endpoints
│   │   │   ├── categories.py # Categories CRUD endpoints
│   │   │   ├── departments.py# Departments CRUD endpoints
│   │   │   ├── grievances.py # Grievances CRUD endpoints
│   │   │   ├── updateGrievance.py # Grievance status update and audit log endpoints
│   │   │   ├── users.py      # Users CRUD endpoints
│   │   │   └── __init__.py   # Router package exports
│   │   ├── auth.py           # Password hashing and token authentication utilities
│   │   ├── database.py       # SQLAlchemy engine, session maker, get_db dependency
│   │   ├── main.py           # FastAPI application entry point
│   │   ├── models.py         # SQLAlchemy ORM entity models
│   │   ├── schemas.py        # Pydantic schemas for request/response serialization
│   │   └── __init__.py       # App package marker
│   ├── test_auth.py          # Auth tests placeholder
│   └── __init__.py           # Backend package marker
├── .planning/                # GSD project memory, planning artifacts, and codebase docs
│   └── codebase/             # 7 structured codebase mapping documents
├── venv/                     # Python 3.13 virtual environment (gitignored)
├── .env                      # Environment variables and database connection (gitignored)
├── .gitignore                # Git ignore rules
├── README.md                 # Project README
└── requirements.txt          # Python dependencies manifest
```

## Directory Purposes

**`backend/app/`:**
- Purpose: Core application module containing the server setup, database layer, domain models, and business logic
- Contains: `main.py`, `database.py`, `models.py`, `schemas.py`, `auth.py`
- Key files: `main.py` (entry point), `database.py` (database engine)

**`backend/app/routers/`:**
- Purpose: HTTP route handlers grouped by resource domain
- Contains: Resource controllers implementing REST endpoints
- Key files: `grievances.py` (core workflow), `users.py` (user management), `updateGrievance.py` (status audit logs)

**`.planning/codebase/`:**
- Purpose: Living documentation of the codebase state for agentic workflows
- Contains: `STACK.md`, `INTEGRATIONS.md`, `ARCHITECTURE.md`, `STRUCTURE.md`, `CONVENTIONS.md`, `TESTING.md`, `CONCERNS.md`

## Key File Locations

**Entry Points:**
- `backend/app/main.py`: ASGI application definition, router aggregation, and health route

**Configuration:**
- `.env`: Database credentials and API endpoints
- `backend/app/database.py`: Resolves root `.env` via `Path(__file__).resolve().parents[2]` and initializes SQLAlchemy engine

**Core Logic:**
- `backend/app/models.py`: Database table definitions for `users`, `departments`, `categories`, `grievances`, `grievance_updates`
- `backend/app/schemas.py`: Request validation and response data structures
- `backend/app/auth.py`: Password hashing using `passlib.context.CryptContext` with bcrypt

**Testing:**
- `backend/test_auth.py`: Initial test file location

**Documentation:**
- `README.md`: Project documentation
- `.planning/codebase/*.md`: Codebase intelligence map

## Naming Conventions

**Files:**
- Snake case: `database.py`, `models.py`, `schemas.py`, `categories.py`, `departments.py`, `grievances.py`, `users.py`
- Outlier: `updateGrievance.py` (camelCase naming convention)

**Classes:**
- PascalCase: `User`, `Department`, `Category`, `Grievance`, `GrievanceUpdate` (models)
- Schema Suffixes: `UserCreate`, `UserUpdate`, `UserResponse`, etc.

**Functions and Endpoints:**
- Snake case: `get_users`, `create_user`, `get_department`, `hash_password`, `verify_password`

## Where to Add New Code

**New Endpoint / Router:**
- Implementation: `backend/app/routers/{resource_name}.py`
- Export: Include in `backend/app/routers/__init__.py` and mount in `backend/app/main.py`
- Schemas: Define `*Create`, `*Update`, `*Response` in `backend/app/schemas.py`
- Models: Add table model in `backend/app/models.py`

**AI / Service Modules (e.g. Groq Grievance Triage):**
- Implementation: `backend/app/services/triage.py` or `backend/app/services/ai.py`
- Dependencies: Inject via FastAPI `Depends()` into router handlers

**Tests:**
- Location: `backend/tests/test_{module}.py` or root `backend/test_{module}.py`
- Setup: Use FastAPI `TestClient` and SQLite/test PostgreSQL database

## Special Directories

**`venv/`:**
- Purpose: Isolated Python 3.13 packages
- Committed: No (in `.gitignore`)

**`.planning/`:**
- Purpose: GSD workflow planning, requirements, and codebase documentation
- Committed: Yes (tracked for project continuity)

---

*Structure analysis: 2026-11-07*
*Update when directory structure changes*

