from pydantic import BaseModel
from typing import List
from datetime import datetime

class ActivityItem(BaseModel):
    id: str
    type: str  # 'student', 'professor', 'course', 'enrollment'
    description: str
    timestamp: datetime

class DashboardResponse(BaseModel):
    students_count: int
    professors_count: int
    courses_count: int
    enrollments_count: int
    recent_activity: List[ActivityItem]
