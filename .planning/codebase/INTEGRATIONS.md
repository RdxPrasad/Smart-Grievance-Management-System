# External Integrations

**Analysis Date:** 2026-11-07

## APIs & External Services

**AI & LLM Services:**
- Groq Cloud API - Fast inference LLM SDK (`groq==1.7.0`)
  - SDK: `groq` Python client library
  - Purpose: Planned integration for automated grievance categorization, priority assessment, and sentiment/triage analysis
  - Auth: Expected via `GROQ_API_KEY` environment variable (pending configuration)
  - Status: Package installed in `requirements.txt`, pending endpoint implementation

## Data Storage

**Databases:**
- PostgreSQL on Supabase - Cloud-hosted relational database
  - Connection: `DATABASE_URL` loaded from `.env` via `psycopg2-binary` driver
  - Client: SQLAlchemy 2.0 ORM (`create_engine`, `sessionmaker` in `backend/app/database.py`)
  - Tables: `users`, `departments`, `categories`, `grievances`, `grievance_updates`
  - Connection lifecycle: Per-request session yielded by `get_db()` generator in `backend/app/database.py`

**Caching:**
- None currently (all queries execute against PostgreSQL)

**File Storage:**
- None configured in application code (Supabase storage SDK not yet wired)

## Authentication & Identity

**Auth Provider:**
- Custom JWT / Password Hashing (in development)
  - Hashing: `passlib.context.CryptContext` with bcrypt in `backend/app/auth.py`
  - Token handling: `python-jose` / `jwt` installed; JWT configuration and token endpoint pending
  - Roles: `student`, `staff`, `admin` enforced via `VALID_ROLES` in `backend/app/routers/users.py`
  - Current interim behavior: Routes accept `submitted_by` and `updated_by` as plain integer IDs in request bodies until auth middleware/dependency is completed

## Monitoring & Observability

**Error Tracking:**
- None configured (standard FastAPI `HTTPException` returns JSON responses)

**Analytics:**
- None

**Logs:**
- Standard Uvicorn access and application logging to stdout / stderr

## CI/CD & Deployment

**Hosting:**
- Local development via Uvicorn (`uvicorn app.main:app --reload`)
- Git repository tracked on branch `main`

**CI Pipeline:**
- None currently configured (no `.github/workflows/` present)

## Environment Configuration

**Development:**
- Required `.env` keys in project root:
  - `DATABASE_URL`: Full PostgreSQL connection string
  - `SUPABASE_URL`: Supabase project URL
  - `SUPABASE_PUBLISHABLE_KEY`: Supabase API key
- Secrets location: Root `.env` file (verified in `.gitignore`)

**Production:**
- Secrets management: Expected cloud environment variables (e.g. Render, Railway, AWS Secrets Manager)

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

---

*Integration audit: 2026-11-07*
*Update when adding/removing external services*

