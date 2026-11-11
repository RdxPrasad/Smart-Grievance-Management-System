from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Department
from app.schemas import UserResponse, UserCreate, UserUpdate
from app.auth import hash_password

VALID_ROLES = ["student", "staff", "admin"]

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# GET ALL USERS (with optional role/department filters)
@router.get("/", response_model=list[UserResponse])
def get_users(
    role: Optional[str] = None,
    department_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role.lower().strip())
    if department_id:
        query = query.filter(User.department_id == department_id)
    return query.order_by(User.id).all()


# CREATE USER
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    normalized_role = user.role.lower().strip()
    if normalized_role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role '{user.role}'. Must be one of: {', '.join(VALID_ROLES)}"
        )

    # Check for duplicate email
    existing_user = db.query(User).filter(User.email.ilike(user.email.strip())).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email '{user.email}' already exists ❌"
        )

    # Validate department if provided
    if user.department_id is not None:
        dept = db.query(Department).filter(Department.id == user.department_id).first()
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Department with id {user.department_id} not found ❌"
            )

    new_user = User(
        name=user.name.strip(),
        email=user.email.strip().lower(),
        role=normalized_role,
        department_id=user.department_id,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# GET ONE USER
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found ❌"
        )
    return user


# UPDATE USER
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found ❌"
        )

    normalized_role = user_data.role.lower().strip()
    if normalized_role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role '{user_data.role}'. Must be one of: {', '.join(VALID_ROLES)}"
        )

    # Check for email conflict with other users
    email_conflict = db.query(User).filter(
        User.email.ilike(user_data.email.strip()),
        User.id != user_id
    ).first()
    if email_conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Another user with email '{user_data.email}' already exists ❌"
        )

    # Validate department if provided
    if user_data.department_id is not None:
        dept = db.query(Department).filter(Department.id == user_data.department_id).first()
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Department with id {user_data.department_id} not found ❌"
            )

    user.name = user_data.name.strip()
    user.email = user_data.email.strip().lower()
    user.role = normalized_role
    user.department_id = user_data.department_id

    db.commit()
    db.refresh(user)

    return user


# DELETE USER
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found ❌"
        )

    # Check for associated records before deleting
    if user.grievances:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete user with submitted grievances ❌"
        )
    if user.updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete user with recorded grievance updates ❌"
        )

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully ✅"}