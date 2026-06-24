import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr

class ProfessorBase(BaseModel):
    name: str
    specialty: str

class ProfessorCreate(BaseModel):
    name: str
    email: EmailStr
    specialty: str

class ProfessorUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    specialty: Optional[str] = None

class ProfessorResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    email: EmailStr
    specialty: str

    class Config:
        from_attributes = True
