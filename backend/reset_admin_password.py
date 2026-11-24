
from app.database import SessionLocal
from app.models.admin import Admin
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

db = SessionLocal()

try:
    admin = db.query(Admin).filter(
        Admin.email == "admin@campusconnect.com"
    ).first()

    if not admin:
        print("Admin account not found!")
    else:
        admin.hashed_password = password_hash.hash("CampusAdmin@2026")
        db.commit()
        print("Admin password reset successfully!")

finally:
    db.close()
