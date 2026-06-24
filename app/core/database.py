from sqlmodel import create_engine, Session
from app.core.config import settings

# El engine de SQLModel para conectarse a la base de datos
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Cambiar a True si se quiere ver el log de SQL en consola
    pool_pre_ping=True if not settings.DATABASE_URL.startswith("sqlite") else False,
    connect_args=connect_args
)

def get_db():
    with Session(engine) as session:
        yield session
