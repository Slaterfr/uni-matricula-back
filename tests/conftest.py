import os
# Configurar una base de datos SQLite local para pruebas antes de que se cargue la configuración de la app
os.environ["DATABASE_URL"] = "sqlite:///testing.db"

import pytest
from sqlmodel import SQLModel, Session, create_engine
from app.core.database import get_db, engine
from app.main import app


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_db_override():
        return session
    
    # Sobrescribir la dependencia del generador de BD
    app.dependency_overrides[get_db] = get_db_override
    
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        yield client
        
    app.dependency_overrides.clear()
