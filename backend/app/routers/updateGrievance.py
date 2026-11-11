from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GrievanceUpdate, Grievance, User
from app.schemas import GrievanceUpdateCreate, GrievanceUpdateResponse

VALID_STATUSES = ["Open", "In Progress", "Resolved", "Rejected"]

router = APIRouter(
    prefix="/grievance-updates",
    tags=["Grievance Updates"]
)


# GET ALL GRIEVANCE UPDATES (with optional filter by grievance_id)
@router.get("/", response_model=list[GrievanceUpdateResponse])
def get_all_grievance_updates(
    grievance_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(GrievanceUpdate)
    if grievance_id:
        query = query.filter(GrievanceUpdate.grievance_id == grievance_id)
    return query.order_by(GrievanceUpdate.created_at.asc()).all()


# CREATE GRIEVANCE UPDATE (Updates grievance status + records timeline entry)
@router.post("/", response_model=GrievanceUpdateResponse, status_code=status.HTTP_201_CREATED)
def create_grievance_update(
    update_data: GrievanceUpdateCreate,
    db: Session = Depends(get_db)
):
    # Verify grievance exists
    existing_grievance = db.query(Grievance).filter(
        Grievance.id == update_data.grievance_id
    ).first()

    if not existing_grievance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grievance with id {update_data.grievance_id} not found ❌"
        )

    # Verify user exists
    updater = db.query(User).filter(User.id == update_data.updated_by).first()
    if not updater:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {update_data.updated_by} not found ❌"
        )

    # Validate status
    if update_data.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{update_data.status}'. Must be one of: {', '.join(VALID_STATUSES)}"
        )

    # 1. Update the parent grievance's current status
    existing_grievance.status = update_data.status

    # 2. Append immutable history/timeline entry
    new_update = GrievanceUpdate(
        grievance_id=update_data.grievance_id,
        updated_by=update_data.updated_by,
        status=update_data.status,
        note=update_data.note.strip() if update_data.note else None
    )

    db.add(new_update)
    db.commit()
    db.refresh(new_update)

    return new_update


# GET TIMELINE FOR A SPECIFIC GRIEVANCE
@router.get("/grievance/{grievance_id}", response_model=list[GrievanceUpdateResponse])
def get_grievance_timeline(
    grievance_id: int,
    db: Session = Depends(get_db)
):
    existing_grievance = db.query(Grievance).filter(Grievance.id == grievance_id).first()
    if not existing_grievance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grievance with id {grievance_id} not found ❌"
        )

    updates = db.query(GrievanceUpdate).filter(
        GrievanceUpdate.grievance_id == grievance_id
    ).order_by(GrievanceUpdate.created_at.asc()).all()

    return updates


# GET ONE SPECIFIC UPDATE BY ID
@router.get("/{update_id}", response_model=GrievanceUpdateResponse)
def get_grievance_update(
    update_id: int,
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

    return grievance_update