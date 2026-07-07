import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column, DateTime, func

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.enrollment import Enrollment
    from app.models.payment import Payment

class Student(SQLModel, table=True):
    __tablename__ = "students"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, unique=True)
    carnet: str = Field(unique=True, index=True, nullable=False)
    name: str = Field(nullable=False)
    phone: str = Field(nullable=False)
    status: str = Field(default="active", nullable=False) # e.g. "active", "inactive"
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False
        )
    )

    # Relación 1-a-1 de vuelta a User
    user: Optional["User"] = Relationship(back_populates="student")

    # Relación 1-a-muchos con Enrollment
    enrollments: List["Enrollment"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    # Relación 1-a-muchos con Payment
    payments: List["Payment"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
