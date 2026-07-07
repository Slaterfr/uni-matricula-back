import uuid
from typing import List
from fastapi import HTTPException, status
from sqlmodel import Session

from app.models.period import Period
from app.repositories.period import period_repository
from app.schemas.period import PeriodCreate, PeriodUpdate

def create_period(db: Session, *, period_in: PeriodCreate) -> Period:
    # Validar que el nombre no esté registrado
    if period_repository.get_by_name(db, name=period_in.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El período '{period_in.name}' ya está registrado.",
        )
    
    # Si se marca como activo, desactivar los demás períodos
    if period_in.is_active:
        active_period = period_repository.get_active(db)
        if active_period:
            active_period.is_active = False
            db.add(active_period)

    period_db = period_repository.create(db, obj_in=period_in)
    return period_db

def get_period_by_id(db: Session, period_id: uuid.UUID) -> Period:
    period = period_repository.get(db, id=period_id)
    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Período académico no encontrado."
        )
    return period

def get_all_periods(db: Session, skip: int = 0, limit: int = 100) -> List[Period]:
    return period_repository.get_multi(db, skip=skip, limit=limit)

def get_active_period(db: Session) -> Period:
    period = period_repository.get_active(db)
    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay ningún período académico activo."
        )
    return period

def update_period(db: Session, period_id: uuid.UUID, period_in: PeriodUpdate) -> Period:
    period = get_period_by_id(db, period_id)

    # Validar cambio de nombre
    if period_in.name is not None and period_in.name != period.name:
        existing = period_repository.get_by_name(db, name=period_in.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El período '{period_in.name}' ya existe.",
            )

    # Si se activa este período, desactivar el actual activo
    if period_in.is_active:
        active_period = period_repository.get_active(db)
        if active_period and active_period.id != period.id:
            active_period.is_active = False
            db.add(active_period)

    updated_period = period_repository.update(db, db_obj=period, obj_in=period_in)
    return updated_period

def delete_period(db: Session, period_id: uuid.UUID) -> Period:
    period = get_period_by_id(db, period_id)
    # Validar si tiene matrículas asociadas antes de borrar
    if len(period.enrollments) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar el período porque tiene matrículas asociadas."
        )
    return period_repository.remove(db, id=period_id)
