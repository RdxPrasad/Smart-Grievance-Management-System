from fastapi import APIRouter , Depends , HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Grievance , User
from app.schemas import GrievanceCreate, GrievanceUpdate, GrievanceResponse
from app.auth import get_current_user


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
def create_grievance(grievance : GrievanceCreate , db : Session = Depends(get_db), current_user: User = Depends(get_current_user)) :
    new_grievance = Grievance(
        submitted_by = current_user.id ,
        complaint = grievance.complaint ,
        priority = grievance.priority ,
        status = grievance.status , 
        category_id = grievance.category_id ,
        department_id=grievance.department_id
    )

    db.add(new_grievance)
    db.commit()
    db.refresh(new_grievance)

    return new_grievance


#GET ONE GRIEVANCE
@router.get("/grievances/{grievance_id}",response_model=GrievanceResponse)
def get_grievance(grievance_id : int , db : Session = Depends(get_db)) :
    grivence = db.query(Grievance).filter(Grievance.id == grievance_id).first()

    if not grivence :
        raise HTTPException(
            status_code=404 ,
            detail="No grievance found ❌"
        )

    return grivence

#UPDATE GRIEVANCE
@router.put("/grievances/{grievance_id}",response_model=GrievanceUpdate)
def update_grievance(grievance_id : int , update_grievance : GrievanceUpdate , db : Session = Depends(get_db)) :
    grievance = db.query(Grievance).filter(grievance_id == Grievance.id).first()

    if not grievance :
        raise HTTPException(
            status_code= 404 ,
            detail= "No grievance found ❌"
        )

    grievance.complaint = update_grievance.complaint
    grievance.priority = update_grievance.priority
    grievance.status = update_grievance.status
    grievance.category_id = update_grievance.category_id

    db.commit()
    db.refresh(grievance)

    return grievance

#DELETE GRIEVANCE
@router.delete("/grievances/{grievance_id}")
def delete_grievance(grievance_id : int , db : Session = Depends(get_db)) :
    grievance = db.query(Grievance).filter(grievance_id == Grievance.id).first()

    if not grievance :
        raise HTTPException(
            status_code= 404 ,
            detail= "No grievance found ❌"
        )

    db.delete(grievance)
    db.commit()

    return {"message" : "Grievance deleted successfully ✅"}