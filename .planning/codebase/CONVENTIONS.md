# Coding Conventions

**Analysis Date:** 2026-11-07

## Naming Patterns

**Files:**
- snake_case for Python modules (`main.py`, `database.py`, `models.py`, `schemas.py`, `auth.py`, `users.py`)
- *Note:* `backend/app/routers/updateGrievance.py` is camelCase and diverges from the standard snake_case convention. New files should use snake_case (`update_grievance.py`).

**Classes:**
- PascalCase for SQLAlchemy models (`User`, `Department`, `Category`, `Grievance`, `GrievanceUpdate`)
- PascalCase with action/role suffix for Pydantic schemas (`UserCreate`, `UserUpdate`, `UserResponse`, `GrievanceCreate`, etc.)

**Functions & Variables:**
- snake_case for functions (`get_users`, `create_user`, `get_db`, `hash_password`, `verify_password`)
- snake_case for local variables and model attributes (`new_user`, `existing_department`, `department_id`, `hashed_password`)
- UPPER_SNAKE_CASE for global constants (`VALID_ROLES`, `BASE_DIR`, `DATABASE_URL`)

## Code Style

**Formatting & Syntax:**
- Python 3.10+ type hinting (`list[UserResponse]`, `Optional[int] = None`, `db: Session = Depends(get_db)`)
- 4-space indentation standard across all Python files
- Blank line separating route handlers and major functional sections

**Imports:**
- Grouped in order:
  1. Standard library (`pathlib`, `os`, `datetime`, `typing`)
  2. Third-party packages (`fastapi`, `sqlalchemy`, `pydantic`, `dotenv`, `passlib`)
  3. Internal application modules (`app.database`, `app.models`, `app.schemas`, `app.auth`)

## Error Handling

**HTTP Status Codes & Exceptions:**
- Raise `fastapi.HTTPException` with explicit status codes and emojis:
  - `status_code=400` for validation issues (e.g. `"Invalid role '{role}'. Must be one of: student, staff, admin"`)
  - `status_code=400` for duplicate conflicts (e.g. `"Department already exists ❌"`)
  - `status_code=404` for missing entities (e.g. `"User not found ❌"`, `"Department with id {id} not found ❌"`)
- Deletion operations return a simple dictionary message with a success checkmark:
  ```python
  return {"message": "User deleted successfully ✅"}
  ```

## Database Patterns

**Session Management:**
- Never instantiate `SessionLocal()` directly in routes. Always inject through FastAPI dependency:
  ```python
  db: Session = Depends(get_db)
  ```
- Route handlers manage transaction commits:
  ```python
  db.add(new_entity)
  db.commit()
  db.refresh(new_entity)
  ```
- Always ensure teardown in generator (`try: yield db finally: db.close()`).

**Model Definitions:**
- All primary keys use `primary_key=True` (and `index=True` on entity models).
- Explicit foreign keys using string references (`ForeignKey("departments.id")`, `ForeignKey("users.id")`).
- Automatic timestamping using SQLAlchemy `server_default=func.now()` with timezone enabled (`DateTime(timezone=True)`).

## Schema Validation

**Pydantic Configuration:**
- All response schemas include ORM mode configuration for SQLAlchemy compatibility:
  ```python
  class Config:
      from_attributes = True
  ```
- Separate schemas for input creation (`*Create`), updates (`*Update`), and API responses (`*Response`).

---

*Convention analysis: 2026-11-07*
*Update when patterns change*

