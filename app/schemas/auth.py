import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    email: str
    user_id: uuid.UUID
    profile_id: Optional[uuid.UUID] = None

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
