from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GrievanceUpdate, Grievance
from app.schemas import GrievanceUpdateCreate, GrievanceUpdateResponse


router = APIRouter()


# GET ALL GRIEVANCE UPDATES
@router.get(
    "/grievance-updates",
    response_model=list[GrievanceUpdateResponse]
)
def get_all_grievance_updates(
    db: Session = Depends(get_db)
):
    updates = db.query(GrievanceUpdate).all()
    return updates


# CREATE GRIEVANCE UPDATE
# updated_by now comes from the request body (temporary until auth is implemented)
@router.post(
    "/grievance-updates",
    response_model=GrievanceUpdateResponse
)
def create_grievance_update(
    grievance: GrievanceUpdateCreate,
    db: Session = Depends(get_db)
):
    existing_grievance = (
        db.query(Grievance)
        .filter(Grievance.id == grievance.grievance_id)
        .first()
    )

    if not existing_grievance:
        raise HTTPException(
            status_code=404,
            detail="Grievance not found ❌"
        )

    # Update the current grievance status
    existing_grievance.status = grievance.status

    # Create immutable history record
    new_grievance_update = GrievanceUpdate(
        grievance_id=grievance.grievance_id,
        updated_by=grievance.updated_by,
        status=grievance.status,
        note=grievance.note
    )

    db.add(new_grievance_update)
    db.commit()
    db.refresh(new_grievance_update)

    return new_grievance_update


# GET ONE GRIEVANCE UPDATE
@router.get(
    "/grievance-updates/{update_id}",
    response_model=GrievanceUpdateResponse
)
def get_grievance_update(
    update_id: int,
    db: Session = Depends(get_db)
):
    grievance_update = (
        db.query(GrievanceUpdate)
        .filter(GrievanceUpdate.id == update_id)
        .first()
    )

    if not grievance_update:
        raise HTTPException(
            status_code=404,
            detail="No grievance update found ❌"
        )

    return grievance_update