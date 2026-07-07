import uuid
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session, select

from app.core.database import get_db
from app.core.deps import RoleChecker
from app.core.security import get_password_hash
from app.models.user import User
from app.models.role import Role
from app.repositories.user import user_repository
from app.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter()

# Restricciones de roles
admin_required = Depends(RoleChecker(["admin"]))

def to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        role_id=user.role_id,
        role_name=user.role.name if user.role else None,
        is_active=user.is_active
    )

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, dependencies=[admin_required])
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo usuario en el sistema. Solo administradores.
    """
    if user_repository.get_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado."
        )
    
    # Validar que el rol exista
    role_exists = db.get(Role, user_in.role_id)
    if not role_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El rol especificado no existe."
        )

    db_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role_id=user_in.role_id,
        is_active=user_in.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return to_user_response(db_user)

@router.get("", response_model=List[UserResponse], dependencies=[admin_required])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtiene el listado de todos los usuarios del sistema. Solo administradores.
    """
    users = user_repository.get_multi(db, skip=skip, limit=limit)
    return [to_user_response(u) for u in users]

@router.get("/{user_id}", response_model=UserResponse, dependencies=[admin_required])
def read_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Obtiene el detalle de un usuario por ID. Solo administradores.
    """
    user = user_repository.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return to_user_response(user)

@router.put("/{user_id}", response_model=UserResponse, dependencies=[admin_required])
def update_user(
    user_id: uuid.UUID,
    user_in: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza la información de un usuario. Solo administradores.
    """
    user = user_repository.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    # Validar cambio de email
    if user_in.email is not None and user_in.email != user.email:
        existing = user_repository.get_by_email(db, email=user_in.email)
        if existing and existing.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está registrado por otro usuario."
            )
        user.email = user_in.email

    # Validar rol si se actualiza
    if user_in.role_id is not None and user_in.role_id != user.role_id:
        role_exists = db.get(Role, user_in.role_id)
        if not role_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El rol especificado no existe."
            )
        user.role_id = user_in.role_id

    # Actualizar estado si se provee
    if user_in.is_active is not None:
        user.is_active = user_in.is_active

    # Actualizar contraseña si se provee
    if user_in.password is not None:
        user.hashed_password = get_password_hash(user_in.password)

    db.add(user)
    db.commit()
    db.refresh(user)
    return to_user_response(user)

@router.delete("/{user_id}", response_model=UserResponse, dependencies=[admin_required])
def delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Elimina un usuario del sistema. Solo administradores.
    """
    user = user_repository.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return to_user_response(user_repository.remove(db, id=user_id))
