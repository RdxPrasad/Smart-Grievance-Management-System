from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Department
from app.schemas import UserResponse, UserCreate, UserUpdate
from app.auth import get_current_user, require_admin

VALID_ROLES = ["student", "staff", "admin"]

router = APIRouter(tags=["Users"])


# GET ALL USERS — ADMIN ONLY
@router.get("/users", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    users = db.query(User).all()
    return users


# CREATE USER — ADMIN ONLY
@router.post("/users", response_model=UserResponse)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    if user.role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role '{user.role}'. Must be one of: {', '.join(VALID_ROLES)}"
        )

    # Validate department if provided
    if user.department_id is not None:
        dept = db.query(Department).filter(Department.id == user.department_id).first()
        if not dept:
            raise HTTPException(
                status_code=404,
                detail=f"Department with id {user.department_id} not found ❌"
            )

    new_user = User(
        name=user.name,
        email=user.email,
        role=user.role,
        department_id=user.department_id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# GET ONE USER — OWN PROFILE OR ADMIN
@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only admin can view other users' profiles
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to view this user profile ❌"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found ❌"
        )

    return user


# UPDATE USER — ADMIN ONLY
@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found ❌"
        )

    if user_data.role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role '{user_data.role}'. Must be one of: {', '.join(VALID_ROLES)}"
        )

    # Validate department if provided
    if user_data.department_id is not None:
        dept = db.query(Department).filter(Department.id == user_data.department_id).first()
        if not dept:
            raise HTTPException(
                status_code=404,
                detail=f"Department with id {user_data.department_id} not found ❌"
            )

    user.name = user_data.name
    user.email = user_data.email
    user.role = user_data.role
    user.department_id = user_data.department_id

    db.commit()
    db.refresh(user)

    return user


# DELETE USER — ADMIN ONLY
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Admin cannot delete their own account ❌"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found ❌"
        )

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully ✅"}

