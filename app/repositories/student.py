from typing import Optional
import uuid
from sqlmodel import Session, select
from app.repositories.base import BaseRepository
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate

class StudentRepository(BaseRepository[Student, StudentCreate, StudentUpdate]):
    def get_by_carnet(self, db: Session, *, carnet: str) -> Optional[Student]:
        """
        Busca un estudiante por su carnet único.
        """
        statement = select(Student).where(Student.carnet == carnet)
        return db.exec(statement).first()

    def get_by_user_id(self, db: Session, *, user_id: uuid.UUID) -> Optional[Student]:
        """
        Busca un estudiante asociado a un ID de usuario.
        """
        statement = select(Student).where(Student.user_id == user_id)
        return db.exec(statement).first()

student_repository = StudentRepository(Student)
