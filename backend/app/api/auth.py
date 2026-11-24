
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.admin import Admin
from app.core.config import settings


router = APIRouter(prefix="/auth", tags=["Authentication"])

security = HTTPBearer()

def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        admin_id = int(payload.get("sub"))

    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    admin = db.query(Admin).filter(Admin.id == admin_id).first()

    if not admin:
        raise HTTPException(
            status_code=401,
            detail="Admin not found"
        )

    return admin

password_hash = PasswordHash.recommended()


class AdminCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class AdminLogin(BaseModel):
    email: EmailStr
    password: str


# Create the first admin account only once
@router.post("/setup")
def setup_admin(data: AdminCreate, db: Session = Depends(get_db)):

    if db.query(Admin).first():
        raise HTTPException(
            status_code=403,
            detail="Admin account already exists"
        )

    admin = Admin(
        full_name=data.full_name,
        email=data.email,
        hashed_password=password_hash.hash(data.password)
    )

    db.add(admin)
    db.commit()

    return {
        "success": True,
        "message": "Admin account created successfully"
    }


# Admin Login
@router.post("/login")
def admin_login(data: AdminLogin, db: Session = Depends(get_db)):

    admin = db.query(Admin).filter(
        Admin.email == data.email
    ).first()

    if not admin or not password_hash.verify(
        data.password, admin.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    expire_time = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    token = jwt.encode(
        {
            "sub": str(admin.id),
            "exp": expire_time
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return {
        "success": True,
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "admin_name": admin.full_name
    }
