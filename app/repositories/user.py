from typing import Optional
from sqlmodel import Session, select
from app.repositories.base import BaseRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        Busca un usuario por su dirección de correo electrónico.
        """
        statement = select(User).where(User.email == email)
        return db.exec(statement).first()

user_repository = UserRepository(User)
