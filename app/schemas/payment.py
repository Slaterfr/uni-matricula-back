import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.payment import PaymentStatus

class PaymentBase(BaseModel):
    student_id: uuid.UUID
    amount: float
    status: PaymentStatus = PaymentStatus.PENDING

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    student_id: Optional[uuid.UUID] = None
    amount: Optional[float] = None
    status: Optional[PaymentStatus] = None

class PaymentRead(PaymentBase):
    id: uuid.UUID
    date: datetime
    student_name: Optional[str] = None
    student_carnet: Optional[str] = None

    model_config = {
        "from_attributes": True
    }
