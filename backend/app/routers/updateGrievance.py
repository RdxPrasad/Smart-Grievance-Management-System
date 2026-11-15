from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GrievanceUpdate, Grievance, User
from app.schemas import GrievanceUpdateCreate, GrievanceUpdateResponse
from app.dependencies import get_current_user, require_role

VALID_STATUSES = ["Open", "In Progress", "Resolved", "Rejected"]

router = APIRouter(
    prefix="/grievance-updates",
    tags=["Grievance Updates"]
)


# GET ALL GRIEVANCE UPDATES (Admin only)
@router.get(
    "/",
    response_model=list[GrievanceUpdateResponse],
    dependencies=[Depends(require_role("admin"))]
)
def get_all_grievance_updates(
    grievance_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(GrievanceUpdate)
    if grievance_id:
        query = query.filter(GrievanceUpdate.grievance_id == grievance_id)
    return query.order_by(GrievanceUpdate.created_at.asc()).all()


# CREATE GRIEVANCE UPDATE (Staff of assigned department or Admin)
# - Note: updated_by is securely populated from current_user.id
# - Grievance status change and timeline entry are recorded in the same transaction
@router.post("/", response_model=GrievanceUpdateResponse, status_code=status.HTTP_201_CREATED)
def create_grievance_update(
    update_data: GrievanceUpdateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["staff", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students cannot update grievance statuses or post timeline updates ❌"
        )

    # Verify grievance exists
    existing_grievance = db.query(Grievance).filter(
        Grievance.id == update_data.grievance_id
    ).first()

    if not existing_grievance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grievance with id {update_data.grievance_id} not found ❌"
        )

    # Department check for staff
    if current_user.role == "staff" and existing_grievance.department_id != current_user.department_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff cannot update grievances assigned to another department ❌"
        )

    # Validate status
    if update_data.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{update_data.status}'. Must be one of: {', '.join(VALID_STATUSES)}"
        )

    # 1. Update the parent grievance's current status
    existing_grievance.status = update_data.status

    # 2. Append immutable history/timeline entry with current_user.id
    new_update = GrievanceUpdate(
        grievance_id=update_data.grievance_id,
        updated_by=current_user.id,
        status=update_data.status,
        note=update_data.note.strip() if update_data.note else None
    )

    db.add(new_update)
    db.commit()
    db.refresh(new_update)

    return new_update


# GET TIMELINE FOR A SPECIFIC GRIEVANCE
# - Students: only if they submitted the grievance
# - Staff: only if grievance is assigned to their department
# - Admin: can view any grievance timeline
@router.get("/grievance/{grievance_id}", response_model=list[GrievanceUpdateResponse])
def get_grievance_timeline(
    grievance_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing_grievance = db.query(Grievance).filter(Grievance.id == grievance_id).first()
    if not existing_grievance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grievance with id {grievance_id} not found ❌"
        )

    if current_user.role == "student" and existing_grievance.submitted_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this grievance's timeline ❌"
        )

    if current_user.role == "staff" and existing_grievance.department_id != current_user.department_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view updates for another department's grievance ❌"
        )

    updates = db.query(GrievanceUpdate).filter(
        GrievanceUpdate.grievance_id == grievance_id
    ).order_by(GrievanceUpdate.created_at.asc()).all()

    return updates


# GET ONE SPECIFIC UPDATE BY ID
@router.get("/{update_id}", response_model=GrievanceUpdateResponse)
def get_grievance_update(
    update_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    grievance_update = db.query(GrievanceUpdate).filter(
        GrievanceUpdate.id == update_id
    ).first()

    if not grievance_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grievance update not found ❌"
        )

    parent_grievance = grievance_update.grievance
    if current_user.role == "student" and parent_grievance.submitted_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this update ❌"
        )

    if current_user.role == "staff" and parent_grievance.department_id != current_user.department_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view updates for another department's grievance ❌"
        )

    return grievance_update
