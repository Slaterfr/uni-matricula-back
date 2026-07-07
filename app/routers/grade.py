import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.deps import RoleChecker, get_current_user
from app.models.user import User
from app.models.enrollment import Enrollment
from app.repositories.student import student_repository
from app.schemas.enrollment import EnrollmentResponse
from app.services import enrollment as enrollment_service

router = APIRouter()

# Restricciones de roles
staff_required = Depends(RoleChecker(["admin", "professor"]))
any_user = Depends(get_current_user)

class GradeUpdate(BaseModel):
    grade: float = Field(..., ge=0.0, le=100.0, description="Calificación final del curso (0-100)")

@router.get("", response_model=List[EnrollmentResponse])
def read_grades(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = any_user
):
    """
    Obtiene el listado de calificaciones (matrículas con su nota correspondiente).
    Administradores ven todos.
    Profesores solo ven los estudiantes inscritos en sus cursos asignados.
    Estudiantes solo ven sus calificaciones propias.
    """
    role_name = current_user.role.name if current_user.role else "student"
    
    if role_name == "student":
        student = student_repository.get_by_user_id(db, user_id=current_user.id)
        if not student:
            return []
        statement = select(Enrollment).where(Enrollment.student_id == student.id).offset(skip).limit(limit)
        enrollments = db.exec(statement).all()
    elif role_name == "professor":
        from app.repositories.professor import professor_repository
        from app.models.course import Course
        professor = professor_repository.get_by_user_id(db, user_id=current_user.id)
        if not professor:
            return []
        statement = (
            select(Enrollment)
            .join(Course)
            .where(Course.professor_id == professor.id)
            .offset(skip)
            .limit(limit)
        )
        enrollments = db.exec(statement).all()
    else:
        statement = select(Enrollment).offset(skip).limit(limit)
        enrollments = db.exec(statement).all()
        
    return [enrollment_service.to_enrollment_response(e) for e in enrollments]

@router.put("/{enrollment_id}", response_model=EnrollmentResponse)
def record_grade(
    enrollment_id: uuid.UUID,
    grade_in: GradeUpdate,
    db: Session = Depends(get_db),
    current_user: User = any_user
):
    """
    Registra o actualiza la nota final de una matrícula.
    Administradores pueden calificar todo.
    Profesores solo pueden calificar alumnos de sus propios cursos asignados.
    """
    # Validar rol y permisos de staff
    role_name = current_user.role.name if current_user.role else "student"
    if role_name not in ["admin", "professor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene suficientes privilegios para acceder a este recurso."
        )

    enrollment = enrollment_service.get_enrollment_by_id(db, enrollment_id=enrollment_id)
    
    if role_name == "professor":
        from app.repositories.professor import professor_repository
        professor = professor_repository.get_by_user_id(db, user_id=current_user.id)
        if not professor or enrollment.course.professor_id != professor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para calificar estudiantes de este curso."
            )
            
    enrollment.grade = grade_in.grade
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment_service.to_enrollment_response(enrollment)
