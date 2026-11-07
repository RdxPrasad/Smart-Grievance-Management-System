# Testing Patterns

**Analysis Date:** 2026-11-07

## Test Framework

**Runner:**
- `pytest` (standard for Python/FastAPI projects)
- Status: Placeholder `backend/test_auth.py` exists (currently 0 bytes). Test runner framework needs initial harness setup.

**Assertion Library:**
- Python standard `assert` with pytest runner

**Recommended Run Commands:**
```bash
pytest backend/                     # Run all backend tests
pytest backend/test_auth.py          # Run auth unit tests
pytest -v                            # Verbose output
pytest --cov=backend/app             # Coverage report (when pytest-cov installed)
```

## Test File Organization

**Location:**
- Unit and integration tests located under `backend/` or `backend/tests/`
- Naming convention: `test_*.py`

**Current Files:**
- `backend/test_auth.py`: Placeholder for authentication and token validation testing

## Recommended Test Architecture for FastAPI

**Client Setup:**
FastAPI provides `TestClient` (backed by `httpx` and `starlette`):

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "SGMS Backend is running! ✅"}
```

**Database Isolation Fixture:**
Use an in-memory SQLite database or test PostgreSQL database to isolate tests:

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
```

## Mocking & AI Testing

**External Services (Groq Cloud API):**
- Mock the `groq.Groq` client responses using `unittest.mock.patch` or `pytest-mock` to avoid external API calls and token consumption during automated testing.

## Coverage Gaps

**Current State:**
- 0% test coverage across all routes (`users`, `departments`, `categories`, `grievances`, `updateGrievance`).
- `test_auth.py` is empty and requires implementation of password hashing/verification tests and token generation tests.

---

*Testing analysis: 2026-11-07*
*Update when test patterns change*
