import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column, DateTime, func

if TYPE_CHECKING:
    from app.models.student import Student

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"

class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    student_id: uuid.UUID = Field(foreign_key="students.id", nullable=False)
    amount: float = Field(nullable=False)
    status: PaymentStatus = Field(default=PaymentStatus.PENDING, nullable=False)
    date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False
        )
    )

    # Relación de vuelta con Estudiante
    student: Optional["Student"] = Relationship(back_populates="payments")
