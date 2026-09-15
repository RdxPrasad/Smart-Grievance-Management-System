
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

# USER TABLE
class UserCreate(BaseModel):
    name : str
    email : str
    role : str
    department_id: Optional[int] = None

class UserUpdate(BaseModel):
    name : str 
    email : str 
    role : str
    department_id: Optional[int] = None

class UserResponse(BaseModel):
    id : int
    name : str 
    email : str
    role : str
    department_id: Optional[int]
    created_at : datetime
    updated_at : datetime

    class Config :
            from_attributes = True



# DEPARTMENTS TABLE

class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None


class DepartmentUpdate(BaseModel):
    name: str
    description: Optional[str] = None


class DepartmentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
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
    department_id: Optional[int] = None

class GrievanceUpdate(BaseModel):
    complaint : str 
    priority : str 
    status : str 
    category_id : int
    department_id: Optional[int] = None

class GrievanceResponse(BaseModel):
    id : int
    submitted_by : int
    complaint : str
    priority : str
    status : str
    category_id : int
    created_at : datetime
    updated_at : datetime
    department_id: Optional[int]

    class Config :
        from_attributes = True




# GRIEVANCE_UPDATE TABLE
class GrievanceUpdateCreate(BaseModel):
    grievance_id : int
    updated_by : int
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


