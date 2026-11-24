
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.auth import get_current_admin
from app.models.student import Student
from app.models.attendance import Attendance

router = APIRouter(prefix="/attendance", tags=["Attendance"])


class AttendanceCreate(BaseModel):
    student_id: int
    status: str
    attendance_date: date = Field(default_factory=date.today)


# Mark Attendance
@router.post("/")
def mark_attendance(
    data: AttendanceCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    student = db.query(Student).filter(
        Student.id == data.student_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if data.status not in ["Present", "Absent"]:
        raise HTTPException(
            status_code=400,
            detail="Status must be Present or Absent"
        )

    existing = db.query(Attendance).filter(
        Attendance.student_id == data.student_id,
        Attendance.attendance_date == data.attendance_date
    ).first()

    if existing:
        existing.status = data.status
        db.commit()
        db.refresh(existing)

        return {
            "success": True,
            "message": "Attendance updated successfully",
            "attendance_id": existing.id
        }

    record = Attendance(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "success": True,
        "message": "Attendance marked successfully",
        "attendance_id": record.id
    }


# Get Attendance Percentage
@router.get("/{student_id}/percentage")
def attendance_percentage(
    student_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    records = db.query(Attendance).filter(
        Attendance.student_id == student_id
    ).all()

    total = len(records)
    present = sum(1 for r in records if r.status == "Present")
    percentage = round((present / total) * 100, 2) if total else 0

    return {
        "student_id": student_id,
        "total_classes": total,
        "present": present,
        "absent": total - present,
        "attendance_percentage": percentage
    }
