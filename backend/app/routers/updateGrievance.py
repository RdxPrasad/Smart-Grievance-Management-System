from fastapi import APIRouter , Depends , HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GrievanceUpdate
from app.schemas import GrievanceUpdateCreate , GrievanceUpdateResponse 


router = APIRouter()


@router.get("/grievance-updates" , response_model=list[GrievanceUpdateResponse])
def get_all_grievance_update(db : Session = Depends(get_db)):
    grievances = db.query(GrievanceUpdate).all()

    return grievances

@router.post("/grievance-updates" , response_model=GrievanceUpdateResponse)
def create_grievance_update(grievance : GrievanceUpdateCreate , db : Session = Depends(get_db)):
    new_grievance = GrievanceUpdate(
        grievance_id=grievance.grievance_id,
        updated_by=grievance.updated_by,
        status=grievance.status,
        note=grievance.note
    )
    db.add(new_grievance)
    db.commit()
    db.refresh(new_grievance)

    return new_grievance


@router.get("/grievance-updates/{update_id}" , response_model= GrievanceUpdateResponse)
def get_grievance_update( update_id : int , db : Session = Depends(get_db)):
    grievance = db.query(GrievanceUpdate).filter(update_id == GrievanceUpdate.id).first()

    if not grievance :
        raise HTTPException(
            status_code=404 ,
            detail="No grievance update found ❌"        )

    return grievance


