import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.professor import Professor
    from app.models.enrollment import Enrollment

class Course(SQLModel, table=True):
    __tablename__ = "courses"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    code: str = Field(unique=True, index=True, nullable=False)
    name: str = Field(nullable=False)
    credits: int = Field(nullable=False)
    professor_id: Optional[uuid.UUID] = Field(foreign_key="professors.id", nullable=True)

    # Relación de vuelta a Professor (Muchos cursos pueden tener el mismo profesor)
    professor: Optional["Professor"] = Relationship(back_populates="courses")

    # Relación 1-a-muchos con Enrollment
    enrollments: List["Enrollment"] = Relationship(
        back_populates="course",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
