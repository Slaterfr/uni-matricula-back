from typing import Optional
from sqlmodel import Session, select
from app.repositories.base import BaseRepository
from app.models.period import Period
from app.schemas.period import PeriodCreate, PeriodUpdate

class PeriodRepository(BaseRepository[Period, PeriodCreate, PeriodUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Period]:
        statement = select(Period).where(Period.name == name)
        return db.exec(statement).first()

    def get_active(self, db: Session) -> Optional[Period]:
        statement = select(Period).where(Period.is_active == True)
        return db.exec(statement).first()

period_repository = PeriodRepository(Period)
