from fastapi import FastAPI, Depends , HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserResponse , UserCreate , UserUpdate
from app.routers import users , categories


app = FastAPI()


@app.get("/")
def root():
    return {"message": "SGMS Backend is running! ✅"}

app.include_router(users.router)
app.include_router(categories.router)




