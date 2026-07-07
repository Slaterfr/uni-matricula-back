import uuid
from typing import Optional
from pydantic import BaseModel

class PeriodBase(BaseModel):
    name: str
    is_active: bool = True

class PeriodCreate(PeriodBase):
    pass

class PeriodUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class PeriodRead(PeriodBase):
    id: uuid.UUID

    model_config = {
        "from_attributes": True
    }
