import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr

class StudentBase(BaseModel):
    carnet: str
    name: str
    phone: str
    status: str = "active"

class StudentCreate(BaseModel):
    carnet: str
    name: str
    email: EmailStr
    phone: str

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: Optional[str] = None

class StudentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    carnet: str
    name: str
    email: EmailStr
    phone: str
    status: str

    class Config:
        from_attributes = True
