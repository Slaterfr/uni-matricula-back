import uuid
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session

from app.core.database import get_db
from app.core.deps import RoleChecker, get_current_user
from app.models.user import User
from app.schemas.professor import ProfessorCreate, ProfessorUpdate, ProfessorResponse
from app.services import professor as professor_service

router = APIRouter()

# Restricciones de roles
admin_required = Depends(RoleChecker(["admin"]))
any_user = Depends(get_current_user)

@router.post("", response_model=ProfessorResponse, status_code=status.HTTP_201_CREATED, dependencies=[admin_required])
def create_new_professor(
    professor_in: ProfessorCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo profesor y su cuenta de usuario.
    Solo accesible por administradores.
    """
    professor = professor_service.create_professor(db, professor_in=professor_in)
    return professor_service.to_professor_response(professor)

@router.get("", response_model=List[ProfessorResponse], dependencies=[any_user])
def read_professors(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de profesores.
    Accesible por cualquier usuario autenticado (para que estudiantes puedan ver el profesor de un curso).
    """
    professors = professor_service.get_all_professors(db, skip=skip, limit=limit)
    return [professor_service.to_professor_response(p) for p in professors]

@router.get("/{professor_id}", response_model=ProfessorResponse, dependencies=[any_user])
def read_professor_detail(
    professor_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Obtiene el detalle de un profesor.
    Accesible por cualquier usuario autenticado.
    """
    professor = professor_service.get_professor_by_id(db, professor_id=professor_id)
    return professor_service.to_professor_response(professor)

@router.put("/{professor_id}", response_model=ProfessorResponse)
def update_professor_detail(
    professor_id: uuid.UUID,
    professor_in: ProfessorUpdate,
    db: Session = Depends(get_db),
    current_user: User = any_user
):
    """
    Actualiza la información de un profesor.
    Accesible por administradores, o el propio profesor.
    """
    professor = professor_service.get_professor_by_id(db, professor_id=professor_id)
    
    # Restricción: Profesores modifican sus propios datos, administradores cualquiera.
    role_name = current_user.role.name if current_user.role else "professor"
    if role_name == "professor" and professor.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar a otro profesor."
        )
    elif role_name == "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Los estudiantes no tienen permisos de modificación."
        )
        
    updated = professor_service.update_professor(db, professor_id=professor_id, professor_in=professor_in)
    return professor_service.to_professor_response(updated)

@router.delete("/{professor_id}", response_model=ProfessorResponse, dependencies=[admin_required])
def delete_professor_by_id(
    professor_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Elimina a un profesor y su usuario asociado.
    Solo accesible por administradores.
    """
    deleted = professor_service.delete_professor(db, professor_id=professor_id)
    return professor_service.to_professor_response(deleted)
