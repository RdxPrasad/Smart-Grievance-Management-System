from fastapi import FastAPI, Depends , HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserResponse , UserCreate , UserUpdate
from app.routers import users , categories , grievances , updateGrievance
from app.routers import auth
from app.routers import departments


app = FastAPI()

# Configure CORS (Cross-Origin Resource Sharing)
# This allows our React frontend running on port 5173 to send requests to this backend.
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "SGMS Backend is running! ✅"}

app.include_router(users.router)
app.include_router(categories.router)
app.include_router(grievances.router)
app.include_router(updateGrievance.router)
app.include_router(auth.router)
app.include_router(departments.router)



