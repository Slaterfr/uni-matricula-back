from typing import Optional, List
import uuid
from sqlmodel import Session, select
from app.repositories.base import BaseRepository
from app.models.enrollment import Enrollment
from app.schemas.enrollment import EnrollmentCreate, EnrollmentUpdate

class EnrollmentRepository(BaseRepository[Enrollment, EnrollmentCreate, EnrollmentUpdate]):
    def get_by_student_and_course(
        self, db: Session, *, student_id: uuid.UUID, course_id: uuid.UUID, period_id: uuid.UUID
    ) -> Optional[Enrollment]:
        """
        Busca si ya existe una matrícula del estudiante en el curso para un período específico.
        """
        statement = select(Enrollment).where(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id,
            Enrollment.period_id == period_id
        )
        return db.exec(statement).first()

    def get_by_student(self, db: Session, *, student_id: uuid.UUID) -> List[Enrollment]:
        """
        Obtiene el listado de matrículas de un estudiante.
        """
        statement = select(Enrollment).where(Enrollment.student_id == student_id)
        return db.exec(statement).all()

enrollment_repository = EnrollmentRepository(Enrollment)
