from typing import Optional
from sqlmodel import Session, select
from app.repositories.base import BaseRepository
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate

class RoleRepository(BaseRepository[Role, RoleCreate, RoleUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Role]:
        statement = select(Role).where(Role.name == name)
        return db.exec(statement).first()

role_repository = RoleRepository(Role)
