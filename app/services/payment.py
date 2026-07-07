import uuid
from typing import List, Optional
from fastapi import HTTPException, status
from sqlmodel import Session

from app.models.payment import Payment, PaymentStatus
from app.repositories.payment import payment_repository
from app.repositories.student import student_repository
from app.schemas.payment import PaymentCreate, PaymentUpdate

def create_payment(db: Session, *, payment_in: PaymentCreate) -> Payment:
    # 1. Validar que el estudiante exista
    student = student_repository.get(db, id=payment_in.student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado."
        )

    # 2. Registrar el pago
    payment_db = payment_repository.create(db, obj_in=payment_in)
    return payment_db

def get_payment_by_id(db: Session, payment_id: uuid.UUID) -> Payment:
    payment = payment_repository.get(db, id=payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de pago no encontrado."
        )
    return payment

def get_all_payments(db: Session, skip: int = 0, limit: int = 100) -> List[Payment]:
    return payment_repository.get_multi(db, skip=skip, limit=limit)

def get_student_payments(db: Session, *, student_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Payment]:
    return payment_repository.get_multi_by_student(db, student_id=student_id, skip=skip, limit=limit)

def update_payment(db: Session, payment_id: uuid.UUID, payment_in: PaymentUpdate) -> Payment:
    payment = get_payment_by_id(db, payment_id)
    return payment_repository.update(db, db_obj=payment, obj_in=payment_in)

def delete_payment(db: Session, payment_id: uuid.UUID) -> Payment:
    payment = get_payment_by_id(db, payment_id)
    return payment_repository.remove(db, id=payment_id)

from app.schemas.payment import PaymentRead

def to_payment_read(payment: Payment) -> PaymentRead:
    return PaymentRead(
        id=payment.id,
        student_id=payment.student_id,
        amount=payment.amount,
        status=payment.status,
        date=payment.date,
        student_name=payment.student.name if payment.student else None,
        student_carnet=payment.student.carnet if payment.student else None
    )
