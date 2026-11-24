
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.auth import get_current_admin
from app.models.student import Student
from app.models.attendance import Attendance
from app.models.assessment import Assessment
from app.schemas.student import StudentCreate, StudentResponse

router = APIRouter(prefix="/students", tags=["Students"])


# Add Student
@router.post("/", response_model=StudentResponse)
def create_student(
    data: StudentCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    existing = db.query(Student).filter(
        (Student.roll_number == data.roll_number) |
        (Student.email == data.email)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Student already exists")

    student = Student(**data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


# Get All Students
@router.get("/", response_model=list[StudentResponse])
def get_students(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    return db.query(Student).order_by(Student.id).all()


# Update Student
@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    data: StudentCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    duplicate = db.query(Student).filter(
        Student.id != student_id,
        (Student.roll_number == data.roll_number) |
        (Student.email == data.email)
    ).first()

    if duplicate:
        raise HTTPException(
            status_code=400,
            detail="Roll number or email already exists"
        )

    for key, value in data.model_dump().items():
        setattr(student, key, value)

    db.commit()
    db.refresh(student)
    return student


# Delete Student
@router.delete("/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    db.query(Attendance).filter(
        Attendance.student_id == student_id
    ).delete(synchronize_session=False)

    db.query(Assessment).filter(
        Assessment.student_id == student_id
    ).delete(synchronize_session=False)

    db.delete(student)
    db.commit()

    return {
        "success": True,
        "message": "Student and related records deleted successfully"
    }
