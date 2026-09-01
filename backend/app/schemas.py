
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

# USER TABLE
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

    class Config :
            from_attributes = True

class UserUpdate(BaseModel):
    name : str 
    email : str 
    role : str

    

# CATEGORIES TABLE
class CategoryCreate(BaseModel):
    name : str 
    description : Optional[str] = None

class CategoryUpdate(BaseModel):
    name : str 
    description : Optional[str] = None

class CategoryResponse(BaseModel):
    id : int 
    name : str 
    description : Optional[str] 
    created_at : datetime
    updated_at : datetime


    class Config :
        from_attributes = True

