
from datetime import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    name : str
    email : str
    role : str

class UserResponse(BaseModel):
    id : int
    name : str 
    email : str
    role : str
    created_at : datetime
    updated_at : datetime

class UserUpdate(BaseModel) :
    name : str 
    email : str 
    role : str

    class config :
        from_attributes = True

