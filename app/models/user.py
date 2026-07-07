import uuid
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.professor import Professor
    from app.models.role import Role

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    email: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    role_id: uuid.UUID = Field(foreign_key="roles.id", nullable=False)
    is_active: bool = Field(default=True, nullable=False)

    # Relación de vuelta con Role
    role: Optional["Role"] = Relationship(back_populates="users")

    # Relaciones 1-a-1 usando back_populates
    student: Optional["Student"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"}
    )
    professor: Optional["Professor"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"}
    )
