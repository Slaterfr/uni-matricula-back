import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column, DateTime, func

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.course import Course

class Professor(SQLModel, table=True):
    __tablename__ = "professors"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, unique=True)
    name: str = Field(nullable=False)
    specialty: str = Field(nullable=False)
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False
        )
    )

    # Relación 1-a-1 de vuelta a User
    user: Optional["User"] = Relationship(back_populates="professor")

    # Relación 1-a-muchos con Course
    courses: List["Course"] = Relationship(
        back_populates="professor",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
