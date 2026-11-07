# Architecture

**Analysis Date:** 2026-11-07

## Pattern Overview

**Overall:** Layered Monolithic REST API (FastAPI + SQLAlchemy)

**Key Characteristics:**
- Modular routing: Endpoints split by resource (`users`, `departments`, `categories`, `grievances`, `updateGrievance`)
- Schema-driven validation: Strict Pydantic models for incoming payloads and outgoing serializations
- Declarative ORM: Relational entity modeling via SQLAlchemy `declarative_base`
- Dependency injection: Per-request database session management using FastAPI's `Depends(get_db)`
- Stateless design: No server-side session state; database transactions committed per endpoint call

## Layers

**API / Routing Layer:**
- Purpose: HTTP endpoint handling, request parameter parsing, HTTP status responses
- Location: `backend/app/routers/*.py`, `backend/app/main.py`
- Contains: FastAPI `APIRouter` instances for CRUD operations
- Depends on: Pydantic schemas, SQLAlchemy models, database session generator, auth functions
- Used by: HTTP clients / frontend consumers

**Validation & Schema Layer:**
- Purpose: Input validation, type coercion, and JSON response shaping
- Location: `backend/app/schemas.py`
- Contains: Pydantic models split by role (`UserCreate`, `UserUpdate`, `UserResponse`, `GrievanceCreate`, etc.)
- Depends on: Pydantic `BaseModel`
- Used by: Routing layer for request body validation and response serialization (`from_attributes = True`)

**Domain & Persistence Layer:**
- Purpose: Database table mapping, relational constraints, foreign keys, query execution
- Location: `backend/app/models.py`, `backend/app/database.py`
- Contains: Declarative models (`User`, `Department`, `Category`, `Grievance`, `GrievanceUpdate`) and engine/session factories
- Depends on: SQLAlchemy Core & ORM, `psycopg2-binary`
- Used by: Router functions via database session

**Security Layer:**
- Purpose: Cryptographic password hashing and verification, token encoding/decoding
- Location: `backend/app/auth.py`
- Contains: `pwd_context` (`bcrypt`), `hash_password()`, `verify_password()`, JWT configuration stubs
- Depends on: `passlib`, `jwt`
- Used by: `backend/app/routers/users.py` and forthcoming authentication endpoints

## Data Flow

**Standard Grievance Lifecycle:**

1. **Submission:**
   - Client sends `POST /grievances` with `GrievanceCreate` JSON payload
   - FastAPI parses and validates fields (`complaint`, `priority`, `category_id`, `department_id`, `submitted_by`)
   - Route handler instantiates SQLAlchemy `Grievance` model
   - Session commits record to PostgreSQL and refreshes entity
   - `GrievanceResponse` serializes record with generated `id`, `created_at`, `updated_at`

2. **Status Progression / Update:**
   - Client sends `POST /grievance-updates` with `GrievanceUpdateCreate` payload
   - Route verifies target grievance exists in `grievances` table (raises 404 if missing)
   - Route mutates `Grievance.status` to match new status
   - Route writes immutable audit log record to `grievance_updates` table
   - Database transaction committed and updated record returned

**State Management:**
- Stateless REST architecture. All state is persisted in PostgreSQL across five relational tables.

## Key Abstractions

**Declarative Model (`backend/app/models.py`):**
- Purpose: Python representation of relational database tables
- Pattern: SQLAlchemy Declarative Mapping with automatic timestamp defaults (`server_default=func.now()`)
- Examples: `User`, `Department`, `Category`, `Grievance`, `GrievanceUpdate`

**Data Transfer Object (`backend/app/schemas.py`):**
- Purpose: Strong typing for API boundaries to decouple database models from client representations
- Pattern: Pydantic `BaseModel` with nested `Config.from_attributes = True` for ORM conversion
- Examples: `DepartmentCreate`, `DepartmentUpdate`, `DepartmentResponse`

**Database Session Dependency (`backend/app/database.py`):**
- Purpose: Scoped database session lifecycle per incoming HTTP request
- Pattern: Generator function with context teardown (`yield db` / `finally: db.close()`) injected via `Depends(get_db)`

## Entry Points

**FastAPI Application Instance:**
- Location: `backend/app/main.py`
- Triggers: Uvicorn invocation (`uvicorn app.main:app --reload`)
- Responsibilities: Creates `FastAPI` instance, defines health check root route (`GET /`), mounts routers

**Route Registration:**
- `app.include_router(users.router)`
- `app.include_router(categories.router)`
- `app.include_router(departments.router)`
- `app.include_router(grievances.router)`
- `app.include_router(updateGrievance.router)`

## Error Handling

**Strategy:** Explicit exception throwing using `fastapi.HTTPException` with localized error messages.

**Patterns:**
- Validation failure: `HTTPException(status_code=400, detail="Invalid role '...' ❌")`
- Missing entity: `HTTPException(status_code=404, detail="... not found ❌")`
- Duplication check: `HTTPException(status_code=400, detail="Department already exists ❌")`

## Cross-Cutting Concerns

**Authentication & Roles:**
- Role validation currently enforced via runtime check `user.role in VALID_ROLES` (`student`, `staff`, `admin`) in `users.py`
- Password hashing with `bcrypt` when persisting user records

**CORS Middleware:**
- `CORSMiddleware` imported in `backend/app/main.py` (needs `app.add_middleware` activation for browser frontend access)

---

*Architecture analysis: 2026-11-07*
*Update when major patterns change*
