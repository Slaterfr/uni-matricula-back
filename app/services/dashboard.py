from sqlmodel import Session, select, func
from typing import List
from app.models.student import Student
from app.models.professor import Professor
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.period import Period
from app.schemas.dashboard import DashboardResponse, ActivityItem, PeriodStatItem

def get_dashboard_stats(db: Session) -> DashboardResponse:
    """
    Recopila las estadísticas globales (conteos), la actividad reciente
    de estudiantes, profesores y matrículas, y el desglose de matrículas por período.
    """
    # 1. Obtener conteos rápidos de base de datos
    students_count = db.scalar(select(func.count()).select_from(Student)) or 0
    professors_count = db.scalar(select(func.count()).select_from(Professor)) or 0
    courses_count = db.scalar(select(func.count()).select_from(Course)) or 0
    enrollments_count = db.scalar(select(func.count()).select_from(Enrollment)) or 0

    # 2. Obtener estadísticas por período académico
    periods = db.exec(select(Period)).all()
    enrollments_by_period = []
    for p in periods:
        count = db.scalar(select(func.count(Enrollment.id)).where(Enrollment.period_id == p.id)) or 0
        enrollments_by_period.append(PeriodStatItem(period_name=p.name, enrollments_count=count))

    def parse_period_name(item: PeriodStatItem):
        roman_to_num = {"I": 1, "II": 2, "III": 3, "IV": 4}
        parts = item.period_name.strip().split()
        if len(parts) >= 2:
            roman, year_str = parts[0], parts[-1]
            try:
                year = int(year_str)
                num = roman_to_num.get(roman, 0)
                return (year, num)
            except ValueError:
                return (0, 0)
        return (0, 0)
    
    enrollments_by_period.sort(key=parse_period_name)

    recent_activity: List[ActivityItem] = []

    # 3. Matrículas recientes (últimas 5)
    enrollments_statement = select(Enrollment).order_by(Enrollment.created_at.desc()).limit(5)
    recent_enrollments = db.exec(enrollments_statement).all()
    for enr in recent_enrollments:
        if enr.student and enr.course:
            period_name = enr.period.name if enr.period else "N/A"
            recent_activity.append(
                ActivityItem(
                    id=f"enr-{enr.id}",
                    type="enrollment",
                    description=f"Matrícula de {enr.student.name} en el curso {enr.course.name} ({period_name})",
                    timestamp=enr.created_at
                )
            )

    # 4. Estudiantes recientes (últimos 5)
    students_statement = select(Student).order_by(Student.created_at.desc()).limit(5)
    recent_students = db.exec(students_statement).all()
    for stud in recent_students:
        recent_activity.append(
            ActivityItem(
                id=f"stud-{stud.id}",
                type="student",
                description=f"Estudiante {stud.name} registrado con carnet {stud.carnet}",
                timestamp=stud.created_at
            )
        )

    # 5. Profesores recientes (últimos 5)
    professors_statement = select(Professor).order_by(Professor.created_at.desc()).limit(5)
    recent_professors = db.exec(professors_statement).all()
    for prof in recent_professors:
        recent_activity.append(
            ActivityItem(
                id=f"prof-{prof.id}",
                type="professor",
                description=f"Profesor {prof.name} registrado en la especialidad {prof.specialty}",
                timestamp=prof.created_at
            )
        )

    # Ordenar por fecha descendente y tomar los 10 más recientes
    recent_activity.sort(key=lambda x: x.timestamp, reverse=True)
    recent_activity = recent_activity[:10]

    return DashboardResponse(
        students_count=students_count,
        professors_count=professors_count,
        courses_count=courses_count,
        enrollments_count=enrollments_count,
        recent_activity=recent_activity,
        enrollments_by_period=enrollments_by_period
    )
