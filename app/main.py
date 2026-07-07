from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import engine
from app.core.security import get_password_hash
from app.models.user import User
from app.models.role import Role
from app.routers import auth, student, professor, course, enrollment, dashboard, period, payment, role, user, grade

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events. Se encarga de sembrar los roles por defecto y el usuario Administrador inicial.
    """
    try:
        with Session(engine) as session:
            # 1. Sembrar roles si no existen
            roles_to_seed = ["admin", "professor", "student"]
            role_map = {}
            for role_name in roles_to_seed:
                role_exists = session.exec(
                    select(Role).where(Role.name == role_name)
                ).first()
                if not role_exists:
                    new_role = Role(name=role_name, description=f"Rol de {role_name}")
                    session.add(new_role)
                    session.commit()
                    session.refresh(new_role)
                    role_map[role_name] = new_role
                else:
                    role_map[role_name] = role_exists
            
            # 2. Sembrar el administrador inicial
            admin_role = role_map["admin"]
            admin_exists = session.exec(
                select(User).where(User.role_id == admin_role.id)
            ).first()
            if not admin_exists:
                admin_user = User(
                    email="admin@universidad.com",
                    hashed_password=get_password_hash("admin123"),
                    role_id=admin_role.id,
                    is_active=True
                )
                session.add(admin_user)
                session.commit()
                print("====================================================")
                print("ADMINISTRADOR INICIAL CREADO:")
                print("Correo: admin@universidad.com")
                print("Contraseña: admin123")
                print("====================================================")
    except Exception as e:
        print(f"Error al sembrar roles o administrador inicial: {e}")
        
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para el Sistema de Gestión Académica Universitaria (MVP)",
    version="1.0.0",
    lifespan=lifespan
)

# Habilitar CORS para permitir llamadas desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción se debe limitar a los dominios del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticación"])
app.include_router(student.router, prefix="/api/v1/students", tags=["Estudiantes"])
app.include_router(professor.router, prefix="/api/v1/professors", tags=["Profesores"])
app.include_router(course.router, prefix="/api/v1/courses", tags=["Cursos"])
app.include_router(enrollment.router, prefix="/api/v1/enrollments", tags=["Matrículas"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(period.router, prefix="/api/v1/periods", tags=["Períodos"])
app.include_router(payment.router, prefix="/api/v1/payments", tags=["Pagos"])
app.include_router(role.router, prefix="/api/v1/roles", tags=["Roles"])
app.include_router(user.router, prefix="/api/v1/users", tags=["Usuarios"])
app.include_router(grade.router, prefix="/api/v1/grades", tags=["Calificaciones"])

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Bienvenido al Sistema de Gestión Académica Universitaria API"
    }
