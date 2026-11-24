
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.auth import get_current_admin
from app.models.student import Student
from app.models.assessment import Assessment
from app.models.attendance import Attendance

router = APIRouter(tags=["Academic Analytics"])


class AssessmentCreate(BaseModel):
    student_id: int
    subject: str
    marks_obtained: float = Field(ge=0)
    max_marks: float = Field(gt=0)


# Add Assessment Marks
@router.post("/assessments/")
def add_assessment(
    data: AssessmentCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    if data.marks_obtained > data.max_marks:
        raise HTTPException(
            status_code=400,
            detail="Marks cannot exceed maximum marks"
        )

    student = db.query(Student).filter(
        Student.id == data.student_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    assessment = Assessment(**data.model_dump())
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return {
        "success": True,
        "message": "Marks saved",
        "assessment_id": assessment.id
    }


# Academic Analytics
@router.get("/analytics/{student_id}")
def get_academic_analytics(
    student_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    assessments = db.query(Assessment).filter(
        Assessment.student_id == student_id
    ).all()

    attendance = db.query(Attendance).filter(
        Attendance.student_id == student_id
    ).all()

    total_classes = len(attendance)
    present = sum(
        1 for record in attendance if record.status == "Present"
    )

    attendance_pct = (
        round(present / total_classes * 100, 2)
        if total_classes else 0
    )

    average = (
        round(
            sum(
                a.marks_obtained / a.max_marks * 100
                for a in assessments
            ) / len(assessments),
            2
        )
        if assessments else 0
    )

    risk_reasons = []

    if total_classes > 0 and attendance_pct < 75:
        risk_reasons.append("Attendance below 75%")

    if assessments and average < 40:
        risk_reasons.append("Academic performance below 40%")

    if not attendance and not assessments:
        risk_status = "Insufficient Data"
    else:
        risk_status = "At Risk" if risk_reasons else "Safe"

    return {
        "student_id": student.id,
        "student_name": student.full_name,
        "attendance_percentage": attendance_pct,
        "average_marks_percentage": average,
        "assessments_count": len(assessments),
        "risk_status": risk_status,
        "risk_reasons": risk_reasons
    }
