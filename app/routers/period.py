import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.database import get_db
from app.core.deps import RoleChecker, get_current_user
from app.schemas.period import PeriodCreate, PeriodUpdate, PeriodRead
from app.services import period as period_service

router = APIRouter()

# Restricciones de roles
admin_required = Depends(RoleChecker(["admin"]))
staff_required = Depends(RoleChecker(["admin", "professor"]))
any_user = Depends(get_current_user)

@router.post("", response_model=PeriodRead, status_code=status.HTTP_201_CREATED, dependencies=[admin_required])
def create_new_period(
    period_in: PeriodCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo período académico. Solo administradores.
    """
    return period_service.create_period(db, period_in=period_in)

@router.get("", response_model=List[PeriodRead], dependencies=[any_user])
def read_periods(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Lista todos los períodos académicos. Cualquier usuario logueado.
    """
    return period_service.get_all_periods(db, skip=skip, limit=limit)

@router.get("/active", response_model=PeriodRead, dependencies=[any_user])
def read_active_period(
    db: Session = Depends(get_db)
):
    """
    Obtiene el período académico activo actual.
    """
    return period_service.get_active_period(db)

@router.get("/{period_id}", response_model=PeriodRead, dependencies=[any_user])
def read_period_detail(
    period_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Obtiene el detalle de un período.
    """
    return period_service.get_period_by_id(db, period_id=period_id)

@router.put("/{period_id}", response_model=PeriodRead, dependencies=[admin_required])
def update_period_detail(
    period_id: uuid.UUID,
    period_in: PeriodUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza la información de un período. Solo administradores.
    """
    return period_service.update_period(db, period_id=period_id, period_in=period_in)

@router.delete("/{period_id}", response_model=PeriodRead, dependencies=[admin_required])
def delete_period_by_id(
    period_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Elimina un período académico (si no tiene matrículas). Solo administradores.
    """
    return period_service.delete_period(db, period_id=period_id)
