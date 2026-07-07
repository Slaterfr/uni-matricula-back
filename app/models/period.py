import uuid
from typing import List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.enrollment import Enrollment

class Period(SQLModel, table=True):
    __tablename__ = "periods"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    name: str = Field(unique=True, index=True, nullable=False) # e.g., "I 2026", "II 2026"
    is_active: bool = Field(default=True, nullable=False)

    # Relación uno-a-muchos con matrículas
    enrollments: List["Enrollment"] = Relationship(back_populates="period")
