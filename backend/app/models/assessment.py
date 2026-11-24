from datetime import date
from sqlalchemy import Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    subject: Mapped[str] = mapped_column(String(100), nullable=False)
    marks_obtained: Mapped[float] = mapped_column(Float, nullable=False)
    max_marks: Mapped[float] = mapped_column(Float, default=100.0)
    assessment_date: Mapped[date] = mapped_column(Date, default=date.today)
