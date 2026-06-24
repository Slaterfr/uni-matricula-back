from typing import Optional
import uuid
from sqlmodel import Session, select
from app.repositories.base import BaseRepository
from app.models.professor import Professor
from app.schemas.professor import ProfessorCreate, ProfessorUpdate

class ProfessorRepository(BaseRepository[Professor, ProfessorCreate, ProfessorUpdate]):
    def get_by_user_id(self, db: Session, *, user_id: uuid.UUID) -> Optional[Professor]:
        """
        Busca un profesor asociado a un ID de usuario.
        """
        statement = select(Professor).where(Professor.user_id == user_id)
        return db.exec(statement).first()

professor_repository = ProfessorRepository(Professor)
