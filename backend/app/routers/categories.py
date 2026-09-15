from fastapi import APIRouter , Depends , HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category
from app.schemas import CategoryCreate , CategoryUpdate , CategoryResponse
from app.auth import require_admin
from app.models import Category, User


router = APIRouter() 

# GET ONE CATEGORY
@router.get("/categories/{category_id}",response_model=CategoryResponse)
def get_category(category_id : int , db : Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category :
        raise HTTPException(
            status_code=404 ,
            detail="Category not found ❌"
        )

    return category

# GET ALL CATEGORIES
@router.get("/categories" , response_model=list[CategoryResponse])
def get_categories(db : Session = Depends(get_db)):
    categories = db.query(Category).all()
    
    return categories

# CREATE CATEGORY
@router.post("/categories" , response_model=CategoryResponse)
def create_category( category : CategoryCreate , current_user: User = Depends(require_admin) , db : Session = Depends(get_db)):
    new_category = Category(
        name = category.name ,
        description = category.description
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category

# UPDATE CATEGORY
@router.put("/categories/{category_id}",response_model=CategoryResponse)
def update_category(category_id : int , category : CategoryUpdate ,  db : Session = Depends(get_db) , current_user: User = Depends(require_admin) ):
    update_category = db.query(Category).filter(Category.id == category_id).first()

    if not update_category :
        raise HTTPException(
            status_code=404 ,
            detail="Category not found ❌"
        )

    update_category.name = category.name
    update_category.description = category.description

    db.commit()
    db.refresh(update_category)

    return update_category

# DELETE CATEGORY
@router.delete("/categories/{category_id}")
def delete_category(category_id : int , db : Session = Depends(get_db) , current_user: User = Depends(require_admin)):
    search_category = db.query(Category).filter(category_id == Category.id).first()

    if not search_category :
        raise HTTPException(
            status_code=404,
            detail="Category not found ❌"
        )

    db.delete(search_category)
    db.commit()

    return {"message" : "Category deleted successfully ✅"}







