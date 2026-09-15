from fastapi import APIRouter , Depends , HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Grievance , User
from app.schemas import GrievanceCreate, GrievanceUpdate, GrievanceResponse
from app.auth import get_current_user , require_admin, require_staff , require_student_or_admin


router = APIRouter()

# GET ALL GRIEVANCES
@router.get("/grievances", response_model=list[GrievanceResponse])
def get_grievances(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "admin":
        grievances = db.query(Grievance).all()

    elif current_user.role == "staff":
        grievances = db.query(Grievance).filter(
            Grievance.department_id == current_user.department_id
        ).all()

    else:  # student
        grievances = db.query(Grievance).filter(
            Grievance.submitted_by == current_user.id
        ).all()

    return grievances

#CREATE GRIEVANCE
@router.post("/grievances",response_model=GrievanceResponse)
def create_grievance(
    grievance: GrievanceCreate,
    current_user: User = Depends(require_student_or_admin),
    db: Session = Depends(get_db)
):
    new_grievance = Grievance(
    submitted_by=current_user.id,
    complaint=grievance.complaint,
    priority=grievance.priority,
    status=grievance.status,
    category_id=grievance.category_id,
    department_id=grievance.department_id
)

    db.add(new_grievance)
    db.commit()
    db.refresh(new_grievance)

    return new_grievance


# GET ONE GRIEVANCE
@router.get("/grievances/{grievance_id}", response_model=GrievanceResponse)
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
            status_code=404,
            detail="No grievance found ❌"
        )

    if current_user.role == "admin":
        return grievance

    elif current_user.role == "staff":
        if grievance.department_id != current_user.department_id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to view this grievance"
            )

    else:  # student
        if grievance.submitted_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to view this grievance"
            )

    return grievance

# UPDATE GRIEVANCE
@router.put("/grievances/{grievance_id}", response_model=GrievanceResponse)
def update_grievance(
    grievance_id: int,
    update_grievance: GrievanceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    grievance = db.query(Grievance).filter(
        Grievance.id == grievance_id
    ).first()

    if not grievance:
        raise HTTPException(
            status_code=404,
            detail="No grievance found ❌"
        )

    # Student cannot update grievances
    if current_user.role == "student":
        raise HTTPException(
            status_code=403,
            detail="Students cannot update grievances"
        )

    # Staff can update only grievances from their department
    if current_user.role == "staff":
        if grievance.department_id != current_user.department_id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to update this grievance"
            )

    # Admin can update any grievance

    grievance.complaint = update_grievance.complaint
    grievance.priority = update_grievance.priority
    grievance.status = update_grievance.status
    grievance.category_id = update_grievance.category_id
    grievance.department_id = update_grievance.department_id

    db.commit()
    db.refresh(grievance)

    return grievance

# DELETE GRIEVANCE
@router.delete("/grievances/{grievance_id}")
def delete_grievance(
    grievance_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    grievance = db.query(Grievance).filter(
        Grievance.id == grievance_id
    ).first()

    if not grievance:
        raise HTTPException(
            status_code=404,
            detail="No grievance found ❌"
        )

    db.delete(grievance)
    db.commit()

    return {
        "message": "Grievance deleted successfully ✅"
    }