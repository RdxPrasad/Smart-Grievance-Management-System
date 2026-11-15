from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Grievance, User, Category, Department
from app.schemas import GrievanceCreate, GrievanceUpdate, GrievanceResponse
from app.dependencies import get_current_user, require_role

VALID_STATUSES = ["Open", "In Progress", "Resolved", "Rejected"]
VALID_PRIORITIES = ["Low", "Medium", "High", "Urgent"]

router = APIRouter(
    prefix="/grievances",
    tags=["Grievances"]
)


# GET ALL GRIEVANCES
# - Students: only their own grievances
# - Staff: only grievances of their assigned department
# - Admin: all grievances (can use all filters)
@router.get("/", response_model=list[GrievanceResponse])
def get_grievances(
    status_filter: Optional[str] = None,
    department_id: Optional[int] = None,
    category_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Grievance)

    # Role-based visibility scoping
    if current_user.role == "student":
        # Students can only ever see their own submitted grievances
        query = query.filter(Grievance.submitted_by == current_user.id)
    elif current_user.role == "staff":
        # Staff can only see grievances assigned to their department
        if current_user.department_id is None:
            # If staff has no department assigned, return empty list
            return []
        query = query.filter(Grievance.department_id == current_user.department_id)
    elif current_user.role == "admin":
        # Admins can filter by department if they specify
        if department_id:
            query = query.filter(Grievance.department_id == department_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized role"
        )

    if status_filter:
        query = query.filter(Grievance.status.ilike(status_filter.strip()))
    if category_id:
        query = query.filter(Grievance.category_id == category_id)

    return query.order_by(Grievance.created_at.desc()).all()


# CREATE GRIEVANCE (Students and Admins)
# Note: submitted_by is automatically set to current_user.id!
@router.post("/", response_model=GrievanceResponse, status_code=status.HTTP_201_CREATED)
def create_grievance(
    grievance: GrievanceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["student", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff cannot submit grievances ❌"
        )

    # Validate category if provided
    if grievance.category_id is not None:
        cat = db.query(Category).filter(Category.id == grievance.category_id).first()
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {grievance.category_id} not found ❌"
            )

    # Validate department if provided
    if grievance.department_id is not None:
        dept = db.query(Department).filter(Department.id == grievance.department_id).first()
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Department with id {grievance.department_id} not found ❌"
            )

    new_grievance = Grievance(
        submitted_by=current_user.id,  # Set securely from authenticated user
        complaint=grievance.complaint.strip(),
        priority=grievance.priority if grievance.priority in VALID_PRIORITIES else "Medium",
        status="Open",
        category_id=grievance.category_id,
        department_id=grievance.department_id
    )

    db.add(new_grievance)
    db.commit()
    db.refresh(new_grievance)

    return new_grievance


# GET ONE GRIEVANCE
# - Student: must own the grievance
# - Staff: grievance must belong to staff's department
# - Admin: can view any grievance
@router.get("/{grievance_id}", response_model=GrievanceResponse)
def get_grievance(
    grievance_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    grievance = db.query(Grievance).filter(
        Grievance.id == grievance_id
    ).first()

    if not grievance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grievance not found ❌"
        )

    # Check ownership / permissions
    if current_user.role == "student" and grievance.submitted_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this grievance ❌"
        )
    if current_user.role == "staff" and grievance.department_id != current_user.department_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view grievances outside your department ❌"
        )

    return grievance


# UPDATE GRIEVANCE
# - Staff: can update grievances belonging to their department
# - Admin: can update any grievance
# - Students: cannot update
@router.put("/{grievance_id}", response_model=GrievanceResponse)
def update_grievance(
    grievance_id: int,
    update_data: GrievanceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["staff", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students cannot modify grievances ❌"
        )

    grievance = db.query(Grievance).filter(
        Grievance.id == grievance_id
    ).first()

    if not grievance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grievance not found ❌"
        )

    if current_user.role == "staff" and grievance.department_id != current_user.department_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff cannot modify grievances outside their department ❌"
        )

    # Validate category if provided
    if update_data.category_id is not None:
        cat = db.query(Category).filter(Category.id == update_data.category_id).first()
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {update_data.category_id} not found ❌"
            )

    # Validate department if provided
    if update_data.department_id is not None:
        dept = db.query(Department).filter(Department.id == update_data.department_id).first()
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Department with id {update_data.department_id} not found ❌"
            )

    grievance.complaint = update_data.complaint.strip()
    grievance.priority = update_data.priority
    grievance.status = update_data.status
    grievance.category_id = update_data.category_id
    grievance.department_id = update_data.department_id

    db.commit()
    db.refresh(grievance)

    return grievance


# DELETE GRIEVANCE (Admin only)
@router.delete(
    "/{grievance_id}",
    dependencies=[Depends(require_role("admin"))]
)
def delete_grievance(
    grievance_id: int,
    db: Session = Depends(get_db)
):
    grievance = db.query(Grievance).filter(
        Grievance.id == grievance_id
    ).first()

    if not grievance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grievance not found ❌"
        )

    db.delete(grievance)
    db.commit()

    return {"message": "Grievance deleted successfully ✅"}
