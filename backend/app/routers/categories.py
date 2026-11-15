from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category
from app.schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from app.dependencies import get_current_user, require_role

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


# GET ALL CATEGORIES (Any authenticated user)
@router.get(
    "/",
    response_model=list[CategoryResponse],
    dependencies=[Depends(get_current_user)]
)
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.name).all()


# GET ONE CATEGORY (Any authenticated user)
@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    dependencies=[Depends(get_current_user)]
)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found ❌"
        )

    return category


# CREATE CATEGORY (Admin only)
@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))]
)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(Category).filter(Category.name.ilike(category.name)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category '{category.name}' already exists ❌"
        )

    new_category = Category(
        name=category.name.strip(),
        description=category.description
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


# UPDATE CATEGORY (Admin only)
@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    dependencies=[Depends(require_role("admin"))]
)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found ❌"
        )

    name_conflict = db.query(Category).filter(
        Category.name.ilike(category_data.name),
        Category.id != category_id
    ).first()
    if name_conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category '{category_data.name}' already exists ❌"
        )

    category.name = category_data.name.strip()
    category.description = category_data.description

    db.commit()
    db.refresh(category)

    return category


# DELETE CATEGORY (Admin only)
@router.delete(
    "/{category_id}",
    dependencies=[Depends(require_role("admin"))]
)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found ❌"
        )

    if category.grievances:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category that has grievances associated with it ❌"
        )

    db.delete(category)
    db.commit()

    return {"message": "Category deleted successfully ✅"}
