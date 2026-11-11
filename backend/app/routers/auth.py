
"""Authentication routes for ResolveRAG."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.models import User, Department
from app.schemas import UserCreate, UserResponse
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Request and response models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# 1. Register a new student
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(user: UserCreate, db: Session = Depends(get_db)):

    email = user.email.strip().lower()

    # Check whether email already exists
    existing_user = db.query(User).filter(
        User.email.ilike(email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

    # Check whether the department exists
    if user.department_id is not None:
        department = db.query(Department).filter(
            Department.id == user.department_id
        ).first()

        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )

    # Create user with student role only
    new_user = User(
        name=user.name.strip(),
        email=email,
        role="student",
        department_id=user.department_id,
        hashed_password=hash_password(user.password)
    )

    # Save user in database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# 2. Login and generate JWT
@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):

    email = request.email.strip().lower()

    # Find user by email
    user = db.query(User).filter(
        User.email.ilike(email)
    ).first()

    # Check email and password
    if not user or not user.hashed_password or not verify_password(
        request.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Create JWT payload
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    }

    # Generate access token
    token = create_access_token(payload)

    return TokenResponse(access_token=token)
