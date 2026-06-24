from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import engine
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.routers import auth, student, professor, course, enrollment, dashboard

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events. Se encarga de sembrar el usuario Administrador inicial
    si la tabla está vacía o no hay administradores.
    """
    # Intentar sembrar un usuario admin inicial si no existe
    try:
        with Session(engine) as session:
            admin_exists = session.exec(
                select(User).where(User.role == UserRole.ADMIN)
            ).first()
            if not admin_exists:
                admin_user = User(
                    email="admin@universidad.com",
                    hashed_password=get_password_hash("admin123"),
                    role=UserRole.ADMIN,
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
        print(f"Error al sembrar el usuario administrador inicial: {e}")
        
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

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Bienvenido al Sistema de Gestión Académica Universitaria API"
    }
