
from datetime import datetime
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    full_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
