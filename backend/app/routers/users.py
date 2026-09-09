from fastapi import APIRouter, Depends , HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserResponse , UserCreate , UserUpdate


router = APIRouter()



# GET ALL USERS
@router.get("/users" , response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)) :
    users = db.query(User).all()
    return users

# CREATE USER
@router.post("/users" , response_model=UserResponse)
def create_user(user : UserCreate , db : Session = Depends(get_db)) :
    new_user = User(
        name = user.name ,
        email = user.email ,
        role = user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# GET ONE USER
@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id : int , db : Session = Depends(get_db)) :
    user = db.query(User).filter(User.id == user_id).first()

    if not user :
        raise HTTPException( 
            status_code=404 ,
            detail="User not found ❌"
        )

    return user

# UPDATE USER
@router.put("/users/{user_id}" , response_model=UserResponse)
def update_user(user_id : int , user_data : UserUpdate , db : Session = Depends(get_db)) :
    user =  db.query(User).filter(User.id == user_id).first()

    if not user :
        raise HTTPException (
            status_code=404 ,
            detail="User not found ❌"
        )

    user.name = user_data.name
    user.email = user_data.email
    user.role = user_data.role

    db.commit()
    db.refresh(user)

    return user

# DELETE USER
@router.delete("/users/{user_id}")
def delete_user(user_id : int , db : Session = Depends(get_db)) :
    user = db.query(User).filter(User.id == user_id).first()

    if not user :
        raise HTTPException(
            status_code=404 ,
            detail="User not found ❌"
        )

    db.delete(user)
    db.commit()

    return { "message" : "User deleted successfully ✅"}

