# Technology Stack

**Analysis Date:** 2026-11-07

## Languages

**Primary:**
- Python 3.13 - All backend application logic, API routing, database models, and authentication utilities

**Secondary:**
- None (SQL handled via ORM, environment configuration via dotenv files)

## Runtime

**Environment:**
- Python 3.13 (CPython)
- Virtual Environment: `venv` located at project root
- Server Gateway: Uvicorn 0.52.4 (ASGI server with Starlette)

**Package Manager:**
- pip
- Manifest: `requirements.txt` at project root

## Frameworks

**Core:**
- FastAPI 0.141.1 - Asynchronous web framework for REST API endpoints
- Starlette 1.6.0 - Underlying ASGI framework for request handling and middleware

**Data & Validation:**
- SQLAlchemy 2.0.52 - Relational database ORM and query construction
- Pydantic 2.13.5 (pydantic-core 2.46.5, pydantic-settings 2.15.0) - Request/response schema validation and settings parsing

**Testing:**
- Currently unconfigured (placeholder `backend/test_auth.py` exists; `pytest` / FastAPI `TestClient` recommended)

**Build/Dev:**
- watchfiles 1.2.0 - File change monitoring for live reload in dev server
- python-dotenv 1.2.3 - Local `.env` configuration loader

## Key Dependencies

**Critical:**
- `fastapi` (0.141.1) - REST API routing, dependency injection (`Depends`), and automatic OpenAPI docs
- `sqlalchemy` (2.0.52) - ORM mapping and database session lifecycle
- `pydantic` (2.13.5) - Data validation and JSON serialization
- `passlib` (with `bcrypt`) - Password hashing and salt verification
- `python-jose` (3.5.0) / `jwt` - JSON Web Token generation and validation (in progress)
- `psycopg2-binary` (2.9.12) - PostgreSQL dialect driver for SQLAlchemy

**Infrastructure & AI:**
- `groq` (1.7.0) - Groq Cloud LLM SDK (installed for smart grievance classification and automated triage)
- `httpx` (0.28.1) - Asynchronous HTTP client (used by Groq SDK and testing)
- `cryptography` (50.0.1) - Cryptographic primitives supporting JWT and hashing

## Configuration

**Environment:**
- Configured via root `.env` file, loaded via `python-dotenv` in `backend/app/database.py`
- Required variables:
  - `DATABASE_URL` (PostgreSQL connection string with credentials, host, database name)
  - `SUPABASE_URL` (Supabase project API endpoint)
  - `SUPABASE_PUBLISHABLE_KEY` (Supabase client access key)

**Build:**
- Standard Python package structure with `requirements.txt`
- `.gitignore` configured for `.env`, `venv/`, `__pycache__/`, `*.pyc`

## Platform Requirements

**Development:**
- Windows / Linux / macOS with Python 3.10+ (tested on Python 3.13)
- Active network connection to hosted PostgreSQL (Supabase)

**Production:**
- Any containerized or Linux/cloud host supporting Python 3.10+ and ASGI (e.g., Docker, AWS ECS/EC2, Render, Railway)
- Hosted PostgreSQL database (Supabase)

---

*Stack analysis: 2026-11-07*
*Update after major dependency changes*

