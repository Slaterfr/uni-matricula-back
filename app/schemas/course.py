import uuid
from typing import Optional
from pydantic import BaseModel

class CourseBase(BaseModel):
    code: str
    name: str
    credits: int

class CourseCreate(BaseModel):
    code: str
    name: str
    credits: int
    professor_id: Optional[uuid.UUID] = None

class CourseUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    credits: Optional[int] = None
    professor_id: Optional[uuid.UUID] = None

class CourseResponse(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    credits: int
    professor_id: Optional[uuid.UUID] = None
    professor_name: Optional[str] = None

    class Config:
        from_attributes = True
