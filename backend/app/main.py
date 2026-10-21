from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import users, categories, departments, grievances, updateGrievance


app = FastAPI(
    title="SGMS API",
    description="Smart Grievance Management System Backend",
)

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
app.include_router(departments.router)
app.include_router(grievances.router)
app.include_router(updateGrievance.router)
