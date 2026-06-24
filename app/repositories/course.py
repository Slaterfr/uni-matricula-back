from typing import Optional
from sqlmodel import Session, select
from app.repositories.base import BaseRepository
from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate

class CourseRepository(BaseRepository[Course, CourseCreate, CourseUpdate]):
    def get_by_code(self, db: Session, *, code: str) -> Optional[Course]:
        """
        Busca un curso por su código único (ej: INF-101).
        """
        statement = select(Course).where(Course.code == code)
        return db.exec(statement).first()

course_repository = CourseRepository(Course)
