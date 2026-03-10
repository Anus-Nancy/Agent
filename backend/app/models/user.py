from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserRole(str, Enum):
    STUDENT = "student"
    STAFF = "staff"
    ADMIN = "admin"
    SENIOR_OFFICER = "senior_officer"
    DEPARTMENT_HEAD = "department_head"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.STUDENT, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    complaints = relationship("Complaint", back_populates="student", foreign_keys="Complaint.student_id")
