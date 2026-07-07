from pydantic import BaseModel
from typing import List
from datetime import datetime

class ActivityItem(BaseModel):
    id: str
    type: str  # 'student', 'professor', 'course', 'enrollment'
    description: str
    timestamp: datetime

class PeriodStatItem(BaseModel):
    period_name: str
    enrollments_count: int

class DashboardResponse(BaseModel):
    students_count: int
    professors_count: int
    courses_count: int
    enrollments_count: int
    recent_activity: List[ActivityItem]
    enrollments_by_period: List[PeriodStatItem] = []
