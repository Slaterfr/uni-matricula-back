import uuid
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session

from app.core.database import get_db
from app.core.deps import RoleChecker
from app.repositories.role import role_repository
from app.schemas.role import RoleCreate, RoleUpdate, RoleRead

router = APIRouter()

# Restricciones de roles
admin_required = Depends(RoleChecker(["admin"]))

@router.post("", response_model=RoleRead, status_code=status.HTTP_201_CREATED, dependencies=[admin_required])
def create_role(
    role_in: RoleCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo rol en la base de datos. Solo administradores.
    """
    if role_repository.get_by_name(db, name=role_in.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El rol '{role_in.name}' ya existe."
        )
    return role_repository.create(db, obj_in=role_in)

@router.get("", response_model=List[RoleRead], dependencies=[admin_required])
def read_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtiene el listado de roles del sistema. Solo administradores.
    """
    return role_repository.get_multi(db, skip=skip, limit=limit)

@router.get("/{role_id}", response_model=RoleRead, dependencies=[admin_required])
def read_role(
    role_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Obtiene el detalle de un rol por ID. Solo administradores.
    """
    role = role_repository.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    return role

@router.put("/{role_id}", response_model=RoleRead, dependencies=[admin_required])
def update_role(
    role_id: uuid.UUID,
    role_in: RoleUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza la información de un rol. Solo administradores.
    """
    role = role_repository.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    if role.name in ["admin", "professor", "student"] and role_in.name is not None and role_in.name != role.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pueden renombrar los roles básicos del sistema (admin, professor, student)."
        )
    return role_repository.update(db, db_obj=role, obj_in=role_in)

@router.delete("/{role_id}", response_model=RoleRead, dependencies=[admin_required])
def delete_role(
    role_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Elimina un rol de la base de datos. Solo administradores.
    """
    role = role_repository.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    if role.name in ["admin", "professor", "student"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pueden eliminar los roles básicos del sistema (admin, professor, student)."
        )
    return role_repository.remove(db, id=role_id)
