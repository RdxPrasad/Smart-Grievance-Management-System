
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

# USER TABLE
class UserCreate(BaseModel):
    name : str
    email : str
    role : str

class UserUpdate(BaseModel):
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




# GRIEVANCES TABLE
class GrievanceCreate(BaseModel):
    submitted_by : int
    complaint : str 
    priority : str
    status : str
    category_id : int

class GrievanceUpdate(BaseModel):
    complaint : str 
    priority : str 
    status : str 
    category_id : int

class GrievanceResponse(BaseModel):
    id : int
    submitted_by : int
    complaint : str
    priority : str
    status : str
    category_id : int
    created_at : datetime
    updated_at : datetime

    class Config :
        from_attributes = True




# GRIEVANCE_UPDATE TABLE
class GrievanceUpdateCreate(BaseModel):
    grievance_id : int
    updated_by : int
    status : str
    note : Optional[str] = None

class GrievanceUpdateUpdate(BaseModel):
    status : str
    note : Optional[str] = None

class GrievanceUpdateResponse(BaseModel):
    id : int 
    grievance_id : int
    updated_by : int
    status : str
    note : Optional[str] = None
    created_at : datetime

    class Config :
        from_attributes = True


