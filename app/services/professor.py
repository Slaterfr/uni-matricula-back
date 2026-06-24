import uuid
from typing import List
from fastapi import HTTPException, status
from sqlmodel import Session

from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.professor import Professor
from app.repositories.user import user_repository
from app.repositories.professor import professor_repository
from app.schemas.professor import ProfessorCreate, ProfessorUpdate, ProfessorResponse

def create_professor(db: Session, *, professor_in: ProfessorCreate) -> Professor:
    """
    Crea un profesor y su cuenta de usuario transaccionalmente.
    La contraseña predeterminada es "Temporal123!".
    """
    # 1. Validar correo único
    if user_repository.get_by_email(db, email=professor_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado.",
        )

    # 2. Crear usuario
    user_db = User(
        email=professor_in.email,
        hashed_password=get_password_hash("Temporal123!"),
        role=UserRole.PROFESSOR,
        is_active=True
    )
    db.add(user_db)
    db.flush()

    # 3. Crear profesor
    professor_db = Professor(
        user_id=user_db.id,
        name=professor_in.name,
        specialty=professor_in.specialty
    )
    db.add(professor_db)
    db.commit()
    db.refresh(professor_db)
    return professor_db

def get_professor_by_id(db: Session, professor_id: uuid.UUID) -> Professor:
    """
    Obtiene un profesor por su ID.
    """
    professor = professor_repository.get(db, id=professor_id)
    if not professor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profesor no encontrado."
        )
    return professor

def get_all_professors(db: Session, skip: int = 0, limit: int = 100) -> List[Professor]:
    """
    Retorna todos los profesores.
    """
    return professor_repository.get_multi(db, skip=skip, limit=limit)

def update_professor(db: Session, professor_id: uuid.UUID, professor_in: ProfessorUpdate) -> Professor:
    """
    Actualiza la información de un profesor y su correo asociado en User.
    """
    professor = get_professor_by_id(db, professor_id)
    user = professor.user

    # Validar y actualizar correo si cambia
    if professor_in.email is not None and professor_in.email != user.email:
        existing_user = user_repository.get_by_email(db, email=professor_in.email)
        if existing_user and existing_user.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está registrado por otro usuario.",
            )
        user.email = professor_in.email
        db.add(user)

    # Actualizar campos específicos del profesor
    professor_data = professor_in.model_dump(exclude={"email"}, exclude_unset=True)
    for field, value in professor_data.items():
        setattr(professor, field, value)
    
    db.add(professor)
    db.commit()
    db.refresh(professor)
    return professor

def delete_professor(db: Session, professor_id: uuid.UUID) -> Professor:
    """
    Elimina al profesor y su cuenta en cascada.
    """
    professor = get_professor_by_id(db, professor_id)
    user = professor.user
    
    db.delete(user)
    db.commit()
    return professor

def to_professor_response(professor: Professor) -> ProfessorResponse:
    """
    Formatea el objeto Profesor al esquema de respuesta.
    """
    return ProfessorResponse(
        id=professor.id,
        user_id=professor.user_id,
        name=professor.name,
        email=professor.user.email,
        specialty=professor.specialty
    )
