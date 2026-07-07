import uuid
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session

from app.core.database import get_db
from app.core.deps import RoleChecker, get_current_user
from app.models.user import User
from app.repositories.student import student_repository
from app.schemas.payment import PaymentCreate, PaymentUpdate, PaymentRead
from app.services import payment as payment_service

router = APIRouter()

# Restricciones de roles
admin_required = Depends(RoleChecker(["admin"]))
any_user = Depends(get_current_user)

@router.post("", response_model=PaymentRead, status_code=status.HTTP_201_CREATED, dependencies=[admin_required])
def register_new_payment(
    payment_in: PaymentCreate,
    db: Session = Depends(get_db)
):
    """
    Registra un pago realizado por un estudiante. Solo administradores.
    """
    payment = payment_service.create_payment(db, payment_in=payment_in)
    return payment_service.to_payment_read(payment)

@router.get("", response_model=List[PaymentRead])
def read_payments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = any_user
):
    """
    Obtiene la lista de pagos.
    Administradores ven todos los pagos.
    Estudiantes solo ven sus propios pagos.
    Profesores no tienen acceso.
    """
    role_name = current_user.role.name if current_user.role else "student"
    
    if role_name == "admin":
        payments = payment_service.get_all_payments(db, skip=skip, limit=limit)
    elif role_name == "student":
        student = student_repository.get_by_user_id(db, user_id=current_user.id)
        if not student:
            return []
        payments = payment_service.get_student_payments(db, student_id=student.id, skip=skip, limit=limit)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Los profesores no tienen acceso al historial de pagos."
        )
        
    return [payment_service.to_payment_read(p) for p in payments]

@router.put("/{payment_id}", response_model=PaymentRead, dependencies=[admin_required])
def update_payment_detail(
    payment_id: uuid.UUID,
    payment_in: PaymentUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos de un pago. Solo administradores.
    """
    payment = payment_service.update_payment(db, payment_id=payment_id, payment_in=payment_in)
    return payment_service.to_payment_read(payment)

@router.delete("/{payment_id}", response_model=PaymentRead, dependencies=[admin_required])
def delete_payment_by_id(
    payment_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Elimina un registro de pago. Solo administradores.
    """
    payment = payment_service.delete_payment(db, payment_id=payment_id)
    return payment_service.to_payment_read(payment)
