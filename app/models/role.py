import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User

class Role(SQLModel, table=True):
    __tablename__ = "roles"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    name: str = Field(unique=True, index=True, nullable=False)
    description: Optional[str] = Field(default=None, nullable=True)

    # Relación uno-a-muchos con usuarios
    users: List["User"] = Relationship(back_populates="role")
