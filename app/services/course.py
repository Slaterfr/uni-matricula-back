import uuid
from typing import List
from fastapi import HTTPException, status
from sqlmodel import Session

from app.models.course import Course
from app.repositories.course import course_repository
from app.repositories.professor import professor_repository
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse

def create_course(db: Session, *, course_in: CourseCreate) -> Course:
    """
    Crea un curso validando que el código sea único y el profesor exista.
    """
    # 1. Validar que el código sea único
    if course_repository.get_by_code(db, code=course_in.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código de curso ya está registrado."
        )
    
    # 2. Validar profesor si se provee
    if course_in.professor_id is not None:
        prof = professor_repository.get(db, id=course_in.professor_id)
        if not prof:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profesor no encontrado."
            )

    course_db = Course(
        code=course_in.code,
        name=course_in.name,
        credits=course_in.credits,
        max_capacity=course_in.max_capacity,
        professor_id=course_in.professor_id
    )
    db.add(course_db)
    db.commit()
    db.refresh(course_db)
    return course_db

def get_course_by_id(db: Session, course_id: uuid.UUID) -> Course:
    """
    Obtiene un curso por su ID.
    """
    course = course_repository.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curso no encontrado."
        )
    return course

def get_all_courses(db: Session, skip: int = 0, limit: int = 100) -> List[Course]:
    """
    Retorna la lista de todos los cursos.
    """
    return course_repository.get_multi(db, skip=skip, limit=limit)

def update_course(db: Session, course_id: uuid.UUID, course_in: CourseUpdate) -> Course:
    """
    Actualiza la información de un curso.
    """
    course = get_course_by_id(db, course_id)

    # Validar código nuevo si cambia
    if course_in.code is not None and course_in.code != course.code:
        existing = course_repository.get_by_code(db, code=course_in.code)
        if existing and existing.id != course.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El código de curso ya está registrado por otro curso."
            )

    # Validar profesor nuevo si cambia
    if course_in.professor_id is not None and course_in.professor_id != course.professor_id:
        prof = professor_repository.get(db, id=course_in.professor_id)
        if not prof:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profesor no encontrado."
            )

    course_data = course_in.model_dump(exclude_unset=True)
    for field, value in course_data.items():
        setattr(course, field, value)
    
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def delete_course(db: Session, course_id: uuid.UUID) -> Course:
    """
    Elimina un curso.
    """
    course = get_course_by_id(db, course_id)
    db.delete(course)
    db.commit()
    return course

def to_course_response(course: Course) -> CourseResponse:
    """
    Formatea el objeto Curso al esquema CourseResponse, resolviendo el nombre del profesor.
    """
    prof_name = course.professor.name if course.professor else None
    return CourseResponse(
        id=course.id,
        code=course.code,
        name=course.name,
        credits=course.credits,
        max_capacity=course.max_capacity,
        professor_id=course.professor_id,
        professor_name=prof_name
    )
