# Codebase Concerns

**Analysis Date:** 2026-11-07

## Tech Debt

**Inconsistent Module Naming:**
- Issue: `backend/app/routers/updateGrievance.py` uses camelCase while all other files follow snake_case (`users.py`, `departments.py`, `categories.py`, `grievances.py`).
- Files: `backend/app/routers/updateGrievance.py`, `backend/app/main.py` (import line 4).
- Impact: Violates PEP 8 naming conventions and creates import style inconsistency.
- Fix approach: Rename to `update_grievance.py` (or merge grievance update endpoints into `grievances.py` under `/grievances/{id}/updates`) and update imports in `main.py`.

**Unconfigured CORS Middleware:**
- Issue: `CORSMiddleware` is imported in `backend/app/main.py` but never registered via `app.add_middleware()`.
- File: `backend/app/main.py` (lines 2, 7).
- Impact: Any frontend client (React, Vue, mobile app) hosted on a different port or domain will fail with browser CORS errors upon calling API endpoints.
- Fix approach: Add `CORSMiddleware` configuration with allowed origins, methods, and headers.

**Duplicate Email Check Missing in User Creation:**
- Issue: `create_user` in `backend/app/routers/users.py` checks role validity and department existence, but does not query if `email` is already registered before calling `db.commit()`.
- File: `backend/app/routers/users.py` (lines 26-57), `backend/app/models.py` (line 12, `User.email` lacks `unique=True`).
- Impact: Multiple users can be registered with identical email addresses, leading to auth ambiguity.
- Fix approach: Add `unique=True, index=True` to `User.email` in `models.py` and raise `HTTPException(400, "Email already registered")` in `users.py`.

## Known Bugs & Typographical Errors

**Typo in Authentication Helper:**
- Issue: In `backend/app/auth.py`, the parameter for `verify_password` is misspelled as `plain_paassword`.
- File: `backend/app/auth.py` (line 12: `def verify_password(plain_paassword:str,hashed_password:str):`).
- Impact: Minor readability defect; can cause keyword argument errors if invoked with `plain_password=...`.
- Fix approach: Correct parameter name to `plain_password`.

**Variable Shadowing in Category Router:**
- Issue: In `backend/app/routers/categories.py`, the variable assigned from `db.query(Category)...` is named `update_category`, shadowing the router function name `def update_category(...)`.
- File: `backend/app/routers/categories.py` (lines 48-63).
- Impact: Causes namespace confusion and makes static analysis/debugging harder.
- Fix approach: Rename variable to `category_obj` or `existing_category`.

## Security Considerations

**Unprotected Endpoints & Client-Supplied User IDs:**
- Risk: Critical endpoints (`POST /grievances` and `POST /grievance-updates`) rely on client-supplied integer IDs (`submitted_by` and `updated_by`) directly in the request body.
- Files: `backend/app/schemas.py` (lines 84, 118), `backend/app/routers/grievances.py` (lines 22-36), `backend/app/routers/updateGrievance.py` (lines 25-56).
- Current mitigation: Code contains explicit comments noting this is temporary until authentication is implemented.
- Recommendations: Implement JWT authentication dependency (`get_current_active_user`) in `auth.py` and derive `submitted_by` and `updated_by` strictly from verified JWT claims.

**Nullable Password Hash:**
- Risk: In `backend/app/models.py`, `User.hashed_password` has `nullable=True`.
- File: `backend/app/models.py` (line 14).
- Current mitigation: `UserCreate` schema requires `password: str`, but database schema allows null values.
- Recommendations: Set `nullable=False` once user migration strategy is stabilized.

## Data Model & Schema Consistency

**Primary Key / Foreign Key Type Discrepancies:**
- Issue: `User.id` is defined as `Column(Integer, primary_key=True)` in `backend/app/models.py` (line 10), whereas `Department.id`, `Category.id`, `Grievance.id`, and `GrievanceUpdate.id` are defined as `BigInteger`. Furthermore, `Grievance.submitted_by` is defined as `BigInteger` referencing `users.id` (which is `Integer`), and `User.department_id` is `BigInteger`.
- File: `backend/app/models.py` (lines 10, 15, 28, 38, 48, 49, 66, 68).
- Impact: Cross-type foreign key mismatches in PostgreSQL can cause casting overhead or strict schema migration issues.
- Fix approach: Standardize all identifier keys to `BigInteger` (or `Integer`) across all tables.

## Missing Critical Features

**Complete JWT Authentication Flow:**
- Problem: `backend/app/auth.py` has basic password hashing, but JWT secret key, algorithm, token generation, and decoding routines are not yet written.
- Blocks: Role-based access control (RBAC), user authentication, securing grievance submission.
- Implementation complexity: Low to Medium.

**AI Grievance Triage & Classification:**
- Problem: `groq==1.7.0` is listed in `requirements.txt`, but no AI services or prompts are wired up.
- Blocks: The "Smart" capability of the Smart Grievance Management System (auto-tagging categories, urgency detection, sentiment analysis).
- Implementation complexity: Medium.

## Test Coverage Gaps

**Zero Automated Test Coverage:**
- What's not tested: No unit tests or integration tests exist; `backend/test_auth.py` is empty (0 bytes).
- Risk: Regressions in CRUD logic, broken foreign keys, or auth vulnerabilities can pass undetected.
- Priority: High.
- Difficulty: Low (FastAPI `TestClient` makes route testing straightforward).

---

*Concerns audit: 2026-11-07*
*Update as issues are fixed or new ones discovered*

