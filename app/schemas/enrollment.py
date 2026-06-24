import uuid
from typing import Optional
from pydantic import BaseModel

class EnrollmentBase(BaseModel):
    period: str

class EnrollmentCreate(BaseModel):
    student_id: uuid.UUID
    course_id: uuid.UUID
    period: str

class EnrollmentUpdate(BaseModel):
    student_id: Optional[uuid.UUID] = None
    course_id: Optional[uuid.UUID] = None
    period: Optional[str] = None

class EnrollmentResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    student_name: str
    student_carnet: str
    course_id: uuid.UUID
    course_name: str
    course_code: str
    period: str

    class Config:
        from_attributes = True
