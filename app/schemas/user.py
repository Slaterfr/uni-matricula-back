import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    role_id: uuid.UUID
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role_id: Optional[uuid.UUID] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    role_id: uuid.UUID
    role_name: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True
