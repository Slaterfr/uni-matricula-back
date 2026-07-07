import uuid
from typing import Optional
from pydantic import BaseModel

class EnrollmentBase(BaseModel):
    period_id: uuid.UUID

class EnrollmentCreate(BaseModel):
    student_id: uuid.UUID
    course_id: uuid.UUID
    period_id: uuid.UUID

class EnrollmentUpdate(BaseModel):
    student_id: Optional[uuid.UUID] = None
    course_id: Optional[uuid.UUID] = None
    period_id: Optional[uuid.UUID] = None
    grade: Optional[float] = None

class EnrollmentResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    student_name: str
    student_carnet: str
    course_id: uuid.UUID
    course_name: str
    course_code: str
    period_id: uuid.UUID
    period: Optional[str] = None
    grade: Optional[float] = None

    class Config:
        from_attributes = True
