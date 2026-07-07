import uuid
from typing import List
from sqlmodel import Session, select
from app.repositories.base import BaseRepository
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentUpdate

class PaymentRepository(BaseRepository[Payment, PaymentCreate, PaymentUpdate]):
    def get_multi_by_student(self, db: Session, *, student_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Payment]:
        statement = select(Payment).where(Payment.student_id == student_id).offset(skip).limit(limit)
        return db.exec(statement).all()

payment_repository = PaymentRepository(Payment)
