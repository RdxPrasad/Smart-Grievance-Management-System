from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GrievanceUpdate, Grievance, User
from app.schemas import GrievanceUpdateCreate, GrievanceUpdateResponse
from app.auth import get_current_user, require_staff


router = APIRouter()


# GET ALL GRIEVANCE UPDATES
@router.get(
    "/grievance-updates",
    response_model=list[GrievanceUpdateResponse]
)
def get_all_grievance_updates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "admin":
        updates = db.query(GrievanceUpdate).all()

    elif current_user.role == "staff":
        updates = (
            db.query(GrievanceUpdate)
            .join(
                Grievance,
                GrievanceUpdate.grievance_id == Grievance.id
            )
            .filter(
                Grievance.department_id == current_user.department_id
            )
            .all()
        )

    else:
        updates = (
            db.query(GrievanceUpdate)
            .join(
                Grievance,
                GrievanceUpdate.grievance_id == Grievance.id
            )
            .filter(
                Grievance.submitted_by == current_user.id
            )
            .all()
        )

    return updates


# CREATE GRIEVANCE UPDATE
# STAFF AND ADMIN ONLY
@router.post(
    "/grievance-updates",
    response_model=GrievanceUpdateResponse
)
def create_grievance_update(
    grievance: GrievanceUpdateCreate,
    current_user: User = Depends(require_staff),
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

    # Staff can update only grievances
    # belonging to their department
    if current_user.role == "staff":
        if existing_grievance.department_id != current_user.department_id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to update this grievance"
            )

    # Update the current grievance status
    existing_grievance.status = grievance.status

    # Create immutable history record
    new_grievance_update = GrievanceUpdate(
        grievance_id=grievance.grievance_id,
        updated_by=current_user.id,
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
    current_user: User = Depends(get_current_user),
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

    # Get the grievance associated with this history record
    grievance = (
        db.query(Grievance)
        .filter(Grievance.id == grievance_update.grievance_id)
        .first()
    )

    if not grievance:
        raise HTTPException(
            status_code=404,
            detail="Grievance not found ❌"
        )

    # Admin can view everything
    if current_user.role == "admin":
        return grievance_update

    # Staff can view history only for their department
    if current_user.role == "staff":
        if grievance.department_id != current_user.department_id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to view this grievance update"
            )

        return grievance_update

    # Student can view only their own grievance history
    if current_user.role == "student":
        if grievance.submitted_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to view this grievance update"
            )

        return grievance_update

    raise HTTPException(
        status_code=403,
        detail="You are not authorized to view this grievance update"
    )