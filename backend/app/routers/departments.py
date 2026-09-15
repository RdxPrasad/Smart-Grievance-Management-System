from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Department
from app.schemas import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse
)

router = APIRouter(
    prefix="/departments",
    tags=["Departments"]
)


@router.post("/", response_model=DepartmentResponse)
def create_department(
    department: DepartmentCreate,
    db: Session = Depends(get_db)
):
    existing_department = db.query(Department).filter(
        Department.name == department.name
    ).first()

    if existing_department:
        raise HTTPException(
            status_code=400,
            detail="Department already exists ❌"
        )

    new_department = Department(
        name=department.name,
        description=department.description
    )

    db.add(new_department)
    db.commit()
    db.refresh(new_department)

    return new_department


@router.get("/", response_model=list[DepartmentResponse])
def get_departments(
    db: Session = Depends(get_db)
):
    return db.query(Department).all()


@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(
    department_id: int,
    db: Session = Depends(get_db)
):
    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found ❌"
        )

    return department


@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department(
    department_id: int,
    department: DepartmentUpdate,
    db: Session = Depends(get_db)
):
    existing_department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not existing_department:
        raise HTTPException(
            status_code=404,
            detail="Department not found ❌"
        )

    existing_department.name = department.name
    existing_department.description = department.description

    db.commit()
    db.refresh(existing_department)

    return existing_department


@router.delete("/{department_id}")
def delete_department(
    department_id: int,
    db: Session = Depends(get_db)
):
    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found ❌"
        )

    db.delete(department)
    db.commit()

    return {
        "message": "Department deleted successfully ✅"
    }