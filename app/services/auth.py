from fastapi import HTTPException, status
from sqlmodel import Session

from app.core.security import verify_password, create_access_token
from app.repositories.user import user_repository
from app.schemas.auth import LoginRequest, Token

def authenticate_user(db: Session, *, login_data: LoginRequest) -> Token:
    """
    Autentica un usuario.
    Verifica que el email exista, la contraseña coincida y que el usuario esté activo.
    Retorna los datos del Token (JWT + metadata).
    """
    user = user_repository.get_by_email(db, email=login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
        )
    
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La cuenta del usuario está inactiva.",
        )
    
    # Resolver profile_id según el rol utilizando las relaciones del modelo User
    profile_id = None
    role_name = user.role.name if user.role else "student"
    if role_name == "student" and user.student:
        profile_id = user.student.id
    elif role_name == "professor" and user.professor:
        profile_id = user.professor.id

    # El payload del JWT llevará el email (sub) y el rol
    access_token = create_access_token(subject=user.email, role=role_name)
    
    return Token(
        access_token=access_token,
        role=role_name,
        email=user.email,
        user_id=user.id,
        profile_id=profile_id
    )
