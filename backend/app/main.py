from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import users, categories, departments, grievances, updateGrievance , auth

app = FastAPI(
    title="ResolveRAG Backend API",
    description="Smart Grievance Management and Resolution System for Educational Institutions",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def root():
    return {"message": "ResolveRAG Backend is running! ✅"}


# Mount all resource routers
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(departments.router)
app.include_router(grievances.router)
app.include_router(updateGrievance.router)
app.include_router(auth.router)