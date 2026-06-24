from fastapi import APIRouter, Depends, Request
from sqlmodel import Session
from app.core.database import get_db
from app.schemas.auth import LoginRequest, Token
from app.services.auth import authenticate_user

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Endpoint de Login.
    Soporta peticiones JSON (desde el frontend de React) y peticiones Form Data (desde Swagger UI/Postman).
    """
    try:
        # Intentar leer como JSON (React)
        body = await request.json()
        login_data = LoginRequest(email=body.get("email"), password=body.get("password"))
    except Exception:
        # Si falla, intentar como Form Data (Swagger UI)
        form_data = await request.form()
        email = form_data.get("username")
        password = form_data.get("password")
        login_data = LoginRequest(email=email, password=password)

    return authenticate_user(db, login_data=login_data)
