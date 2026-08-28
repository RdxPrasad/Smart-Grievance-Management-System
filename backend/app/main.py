from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User


app = FastAPI()


@app.get("/")
def root():
    return {"message": "SGMS Backend is running!"}


@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users