import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.database import get_db
from app.core.deps import RoleChecker, get_current_user
from app.models.user import User
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from app.services import student as student_service

router = APIRouter()

# Restricciones de roles
admin_required = Depends(RoleChecker(["admin"]))
staff_required = Depends(RoleChecker(["admin", "professor"]))
any_user = Depends(get_current_user)

@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED, dependencies=[admin_required])
def create_new_student(
    student_in: StudentCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo estudiante y su cuenta de usuario.
    Solo accesible por administradores.
    """
    student = student_service.create_student(db, student_in=student_in)
    return student_service.to_student_response(student)

@router.get("", response_model=List[StudentResponse], dependencies=[staff_required])
def read_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de estudiantes.
    Accesible por administradores y profesores.
    """
    students = student_service.get_all_students(db, skip=skip, limit=limit)
    return [student_service.to_student_response(s) for s in students]

@router.get("/{student_id}", response_model=StudentResponse)
def read_student_detail(
    student_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = any_user
):
    """
    Obtiene el detalle de un estudiante.
    Accesible por administradores, profesores, y el propio estudiante.
    """
    student = student_service.get_student_by_id(db, student_id=student_id)
    
    # Si es rol estudiante, verificar que solo pueda ver su propia información
    if current_user.role.value == "student" and student.user_id != current_user.id:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver la información de otro estudiante."
        )
        
    return student_service.to_student_response(student)

@router.put("/{student_id}", response_model=StudentResponse)
def update_student_detail(
    student_id: uuid.UUID,
    student_in: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = any_user
):
    """
    Actualiza la información de un estudiante.
    Accesible por administradores, o el estudiante mismo (para sus propios datos).
    """
    student = student_service.get_student_by_id(db, student_id=student_id)
    
    # Restricción: Estudiantes solo modifican sus propios datos, administradores cualquiera.
    # Profesores no pueden modificar estudiantes.
    if current_user.role.value == "student" and student.user_id != current_user.id:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar a otro estudiante."
        )
    elif current_user.role.value == "professor":
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Los profesores no tienen permisos de modificación."
        )
        
    updated = student_service.update_student(db, student_id=student_id, student_in=student_in)
    return student_service.to_student_response(updated)

@router.delete("/{student_id}", response_model=StudentResponse, dependencies=[admin_required])
def delete_student_by_id(
    student_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Elimina a un estudiante y su usuario asociado.
    Solo accesible por administradores.
    """
    deleted = student_service.delete_student(db, student_id=student_id)
    return student_service.to_student_response(deleted)
