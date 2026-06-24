import uuid
from typing import List
from fastapi import HTTPException, status
from sqlmodel import Session

from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.student import Student
from app.repositories.user import user_repository
from app.repositories.student import student_repository
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse

def create_student(db: Session, *, student_in: StudentCreate) -> Student:
    """
    Crea un estudiante y su correspondiente cuenta de usuario de forma transaccional.
    La contraseña por defecto es el número de carnet del estudiante.
    """
    # 1. Validar que el correo no esté registrado
    if user_repository.get_by_email(db, email=student_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado.",
        )
    
    # 2. Validar que el carnet no esté registrado
    if student_repository.get_by_carnet(db, carnet=student_in.carnet):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El carnet de estudiante ya está registrado.",
        )

    # 3. Crear registro del usuario
    user_db = User(
        email=student_in.email,
        hashed_password=get_password_hash(student_in.carnet),
        role=UserRole.STUDENT,
        is_active=True
    )
    db.add(user_db)
    db.flush()  # Obtener el ID generado para el usuario

    # 4. Crear el estudiante enlazado a ese usuario
    student_db = Student(
        user_id=user_db.id,
        carnet=student_in.carnet,
        name=student_in.name,
        phone=student_in.phone,
        status="active"
    )
    db.add(student_db)
    db.commit()
    db.refresh(student_db)
    return student_db

def get_student_by_id(db: Session, student_id: uuid.UUID) -> Student:
    """
    Obtiene un estudiante por ID, lanza 404 si no existe.
    """
    student = student_repository.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado."
        )
    return student

def get_all_students(db: Session, skip: int = 0, limit: int = 100) -> List[Student]:
    """
    Retorna la lista de todos los estudiantes.
    """
    return student_repository.get_multi(db, skip=skip, limit=limit)

def update_student(db: Session, student_id: uuid.UUID, student_in: StudentUpdate) -> Student:
    """
    Actualiza la información del estudiante y, si es necesario, su correo en el modelo User.
    """
    student = get_student_by_id(db, student_id)
    user = student.user

    # Validar y actualizar correo si se solicita un cambio
    if student_in.email is not None and student_in.email != user.email:
        existing_user = user_repository.get_by_email(db, email=student_in.email)
        if existing_user and existing_user.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está registrado por otro usuario.",
            )
        user.email = student_in.email
        db.add(user)

    # Actualizar los demás campos del estudiante
    student_data = student_in.model_dump(exclude={"email"}, exclude_unset=True)
    for field, value in student_data.items():
        setattr(student, field, value)
    
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

def delete_student(db: Session, student_id: uuid.UUID) -> Student:
    """
    Elimina al estudiante y su correspondiente cuenta de usuario en cascada.
    """
    student = get_student_by_id(db, student_id)
    user = student.user
    
    # Eliminar el User. Debido a cascade delete-orphan, se eliminará el Student asociado
    db.delete(user)
    db.commit()
    return student

def to_student_response(student: Student) -> StudentResponse:
    """
    Formatea el objeto Student al esquema StudentResponse.
    """
    return StudentResponse(
        id=student.id,
        user_id=student.user_id,
        carnet=student.carnet,
        name=student.name,
        email=student.user.email,
        phone=student.phone,
        status=student.status
    )
