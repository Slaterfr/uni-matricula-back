import uuid
from typing import List
from fastapi import HTTPException, status
from sqlmodel import Session

from app.models.enrollment import Enrollment
from app.repositories.enrollment import enrollment_repository
from app.repositories.student import student_repository
from app.repositories.course import course_repository
from app.schemas.enrollment import EnrollmentCreate, EnrollmentUpdate, EnrollmentResponse

def create_enrollment(db: Session, *, enrollment_in: EnrollmentCreate) -> Enrollment:
    """
    Registra una matrícula. Valida que existan el estudiante y el curso, y que no exista duplicado.
    """
    # 1. Validar estudiante
    student = student_repository.get(db, id=enrollment_in.student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado."
        )

    # 2. Validar curso
    course = course_repository.get(db, id=enrollment_in.course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curso no encontrado."
        )

    # 3. Validar duplicados de matrícula en el mismo periodo
    existing = enrollment_repository.get_by_student_and_course(
        db,
        student_id=enrollment_in.student_id,
        course_id=enrollment_in.course_id,
        period=enrollment_in.period
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El estudiante ya está matriculado en el curso {course.name} para el período {enrollment_in.period}."
        )

    enrollment_db = Enrollment(
        student_id=enrollment_in.student_id,
        course_id=enrollment_in.course_id,
        period=enrollment_in.period
    )
    db.add(enrollment_db)
    db.commit()
    db.refresh(enrollment_db)
    return enrollment_db

def get_enrollment_by_id(db: Session, enrollment_id: uuid.UUID) -> Enrollment:
    """
    Obtiene una matrícula por ID.
    """
    enrollment = enrollment_repository.get(db, id=enrollment_id)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matrícula no encontrada."
        )
    return enrollment

def get_all_enrollments(db: Session, skip: int = 0, limit: int = 100) -> List[Enrollment]:
    """
    Retorna la lista de todas las matrículas.
    """
    return enrollment_repository.get_multi(db, skip=skip, limit=limit)

def update_enrollment(db: Session, enrollment_id: uuid.UUID, enrollment_in: EnrollmentUpdate) -> Enrollment:
    """
    Actualiza la matrícula validando que existan las entidades actualizadas y no cause duplicidad.
    """
    enrollment = get_enrollment_by_id(db, enrollment_id)

    student_id = enrollment_in.student_id or enrollment.student_id
    course_id = enrollment_in.course_id or enrollment.course_id
    period = enrollment_in.period or enrollment.period

    if enrollment_in.student_id is not None and enrollment_in.student_id != enrollment.student_id:
        if not student_repository.get(db, id=enrollment_in.student_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado."
            )

    if enrollment_in.course_id is not None and enrollment_in.course_id != enrollment.course_id:
        if not course_repository.get(db, id=enrollment_in.course_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Curso no encontrado."
            )

    # Validar duplicado si cambia algo
    if (enrollment_in.student_id is not None or
        enrollment_in.course_id is not None or
        enrollment_in.period is not None):
        existing = enrollment_repository.get_by_student_and_course(
            db, student_id=student_id, course_id=course_id, period=period
        )
        if existing and existing.id != enrollment.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El estudiante ya está matriculado en este curso para el período {period}."
            )

    enrollment_data = enrollment_in.model_dump(exclude_unset=True)
    for field, value in enrollment_data.items():
        setattr(enrollment, field, value)

    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment

def delete_enrollment(db: Session, enrollment_id: uuid.UUID) -> Enrollment:
    """
    Elimina una matrícula.
    """
    enrollment = get_enrollment_by_id(db, enrollment_id)
    db.delete(enrollment)
    db.commit()
    return enrollment

def to_enrollment_response(enrollment: Enrollment) -> EnrollmentResponse:
    """
    Formatea el objeto Matrícula al esquema EnrollmentResponse.
    """
    return EnrollmentResponse(
        id=enrollment.id,
        student_id=enrollment.student_id,
        student_name=enrollment.student.name,
        student_carnet=enrollment.student.carnet,
        course_id=enrollment.course_id,
        course_name=enrollment.course.name,
        course_code=enrollment.course.code,
        period=enrollment.period
    )
