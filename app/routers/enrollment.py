import uuid
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session

from app.core.database import get_db
from app.core.deps import RoleChecker, get_current_user
from app.models.user import User
from app.schemas.enrollment import EnrollmentCreate, EnrollmentUpdate, EnrollmentResponse
from app.services import enrollment as enrollment_service
from app.repositories.student import student_repository
from app.repositories.enrollment import enrollment_repository

router = APIRouter()

admin_required = Depends(RoleChecker(["admin"]))
any_user = Depends(get_current_user)

@router.post("", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def create_new_enrollment(
    enrollment_in: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = any_user
):
    """
    Registra una nueva matrícula.
    Administradores pueden matricular a cualquier estudiante.
    Estudiantes solo pueden matricularse a sí mismos.
    Profesores no tienen acceso.
    """
    # Si es un estudiante, validar que se matricule a sí mismo
    if current_user.role.name == "student":
        student = student_repository.get_by_user_id(db, user_id=current_user.id)
        if not student or student.id != enrollment_in.student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo tienes permiso para matricularte a ti mismo."
            )
        # Forzar que el estado del estudiante sea activo
        if student.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tu cuenta de estudiante está inactiva y no puedes matricularte."
            )
    elif current_user.role.name == "professor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Los profesores no están autorizados para registrar matrículas."
        )

    enrollment = enrollment_service.create_enrollment(db, enrollment_in=enrollment_in)
    return enrollment_service.to_enrollment_response(enrollment)

@router.get("", response_model=List[EnrollmentResponse])
def read_enrollments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = any_user
):
    """
    Obtiene el listado de matrículas.
    Administradores y Profesores ven todas.
    Estudiantes solo ven sus propias matrículas.
    """
    if current_user.role.name == "student":
        student = student_repository.get_by_user_id(db, user_id=current_user.id)
        if not student:
            return []
        enrollments = enrollment_repository.get_by_student(db, student_id=student.id)
    else:
        # Administrador y Profesores
        enrollments = enrollment_service.get_all_enrollments(db, skip=skip, limit=limit)
        
    return [enrollment_service.to_enrollment_response(e) for e in enrollments]

@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
def read_enrollment_detail(
    enrollment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = any_user
):
    """
    Obtiene el detalle de una matrícula.
    Accesible por administradores, profesores o el estudiante propietario de la matrícula.
    """
    enrollment = enrollment_service.get_enrollment_by_id(db, enrollment_id=enrollment_id)
    
    if current_user.role.name == "student":
        student = student_repository.get_by_user_id(db, user_id=current_user.id)
        if not student or enrollment.student_id != student.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver esta matrícula."
            )
            
    return enrollment_service.to_enrollment_response(enrollment)

@router.put("/{enrollment_id}", response_model=EnrollmentResponse, dependencies=[admin_required])
def update_enrollment_detail(
    enrollment_id: uuid.UUID,
    enrollment_in: EnrollmentUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos de una matrícula.
    Solo accesible por administradores.
    """
    updated = enrollment_service.update_enrollment(db, enrollment_id=enrollment_id, enrollment_in=enrollment_in)
    return enrollment_service.to_enrollment_response(updated)

@router.delete("/{enrollment_id}", response_model=EnrollmentResponse)
def delete_enrollment_by_id(
    enrollment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = any_user
):
    """
    Elimina (desinscribe) una matrícula.
    Accesible por administradores o por el estudiante propietario.
    """
    enrollment = enrollment_service.get_enrollment_by_id(db, enrollment_id=enrollment_id)
    
    if current_user.role.name == "student":
        student = student_repository.get_by_user_id(db, user_id=current_user.id)
        if not student or enrollment.student_id != student.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puedes eliminar tus propias matrículas."
            )
    elif current_user.role.name == "professor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Los profesores no pueden desinscribir matrículas."
        )

    deleted = enrollment_service.delete_enrollment(db, enrollment_id=enrollment_id)
    return enrollment_service.to_enrollment_response(deleted)
