from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Grievance, User, Category, Department
from app.schemas import GrievanceCreate, GrievanceUpdate, GrievanceResponse

VALID_STATUSES = ["Open", "In Progress", "Resolved", "Rejected"]
VALID_PRIORITIES = ["Low", "Medium", "High", "Urgent"]

router = APIRouter(
    prefix="/grievances",
    tags=["Grievances"]
)


# GET ALL GRIEVANCES (with optional filters)
@router.get("/", response_model=list[GrievanceResponse])
def get_grievances(
    status_filter: Optional[str] = None,
    department_id: Optional[int] = None,
    category_id: Optional[int] = None,
    submitted_by: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Grievance)

    if status_filter:
        query = query.filter(Grievance.status.ilike(status_filter.strip()))
    if department_id:
        query = query.filter(Grievance.department_id == department_id)
    if category_id:
        query = query.filter(Grievance.category_id == category_id)
    if submitted_by:
        query = query.filter(Grievance.submitted_by == submitted_by)

    return query.order_by(Grievance.created_at.desc()).all()


# CREATE GRIEVANCE
@router.post("/", response_model=GrievanceResponse, status_code=status.HTTP_201_CREATED)
def create_grievance(
    grievance: GrievanceCreate,
    db: Session = Depends(get_db)
):
    # Verify submitting user exists
    user = db.query(User).filter(User.id == grievance.submitted_by).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {grievance.submitted_by} not found ❌"
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
        submitted_by=grievance.submitted_by,
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
@router.get("/{grievance_id}", response_model=GrievanceResponse)
def get_grievance(
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

    return grievance


# UPDATE GRIEVANCE
@router.put("/{grievance_id}", response_model=GrievanceResponse)
def update_grievance(
    grievance_id: int,
    update_data: GrievanceUpdate,
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


# DELETE GRIEVANCE
@router.delete("/{grievance_id}")
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