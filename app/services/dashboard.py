from sqlmodel import Session, select, func
from typing import List
from app.models.student import Student
from app.models.professor import Professor
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.schemas.dashboard import DashboardResponse, ActivityItem

def get_dashboard_stats(db: Session) -> DashboardResponse:
    """
    Recopila las estadísticas globales (conteos) y la actividad reciente
    de estudiantes, profesores y matrículas.
    """
    # 1. Obtener conteos rápidos de base de datos
    students_count = db.scalar(select(func.count()).select_from(Student)) or 0
    professors_count = db.scalar(select(func.count()).select_from(Professor)) or 0
    courses_count = db.scalar(select(func.count()).select_from(Course)) or 0
    enrollments_count = db.scalar(select(func.count()).select_from(Enrollment)) or 0

    recent_activity: List[ActivityItem] = []

    # 2. Matrículas recientes (últimas 5)
    enrollments_statement = select(Enrollment).order_by(Enrollment.created_at.desc()).limit(5)
    recent_enrollments = db.exec(enrollments_statement).all()
    for enr in recent_enrollments:
        if enr.student and enr.course:
            recent_activity.append(
                ActivityItem(
                    id=f"enr-{enr.id}",
                    type="enrollment",
                    description=f"Matrícula de {enr.student.name} en el curso {enr.course.name} ({enr.period})",
                    timestamp=enr.created_at
                )
            )

    # 3. Estudiantes recientes (últimos 5)
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

    # 4. Profesores recientes (últimos 5)
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
        recent_activity=recent_activity
    )
