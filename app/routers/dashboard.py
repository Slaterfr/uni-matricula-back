from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_db
from app.core.deps import RoleChecker
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard import get_dashboard_stats

router = APIRouter()

# Solo administradores y profesores pueden ver el dashboard de métricas generales
dashboard_required = Depends(RoleChecker(["admin", "professor"]))

@router.get("", response_model=DashboardResponse, dependencies=[dashboard_required])
def read_dashboard_statistics(db: Session = Depends(get_db)):
    """
    Retorna métricas generales y la actividad reciente para el panel de control.
    """
    return get_dashboard_stats(db)
