
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine

# Import all models
from app.models.student import Student
from app.models.attendance import Attendance
from app.models.assessment import Assessment
from app.models.admin import Admin

# Import API routers
from app.api.student import router as students_router
from app.api.attendance import router as attendance_router
from app.api.analytics import router as analytics_router
from app.api.auth import router as auth_router


app = FastAPI(
    title="CampusConnect",
    description="Smart Campus Management System API",
    version="1.0.0"
)

# Existing database tables are already created.
# Do not run create_all again right now.

# Enable frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Register API routers
app.include_router(students_router)
app.include_router(attendance_router)
app.include_router(analytics_router)
app.include_router(auth_router)


@app.get("/")
def home():
    return {
        "success": True,
        "message": "Welcome to CampusConnect!",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "CampusConnect"
    }
