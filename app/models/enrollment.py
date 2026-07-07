import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column, DateTime, func

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.course import Course
    from app.models.period import Period

class Enrollment(SQLModel, table=True):
    __tablename__ = "enrollments"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    student_id: uuid.UUID = Field(foreign_key="students.id", nullable=False)
    course_id: uuid.UUID = Field(foreign_key="courses.id", nullable=False)
    period_id: uuid.UUID = Field(foreign_key="periods.id", nullable=False)
    grade: Optional[float] = Field(default=None, nullable=True)
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False
        )
    )

    # Relaciones de vuelta
    student: Optional["Student"] = Relationship(back_populates="enrollments")
    course: Optional["Course"] = Relationship(back_populates="enrollments")
    period: Optional["Period"] = Relationship(back_populates="enrollments")
