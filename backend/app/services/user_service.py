"""Service layer for User operations."""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate


class UserService:
    """Service handling database queries and operations for Users."""

    def create(self, db: Session, user_in: UserCreate) -> User:
        """Create a new user."""
        user = User(
            name=user_in.name,
            email=user_in.email,
            role=user_in.role.value if hasattr(user_in.role, "value") else str(user_in.role),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Fetch a user by ID."""
        return db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Fetch a user by email."""
        return db.query(User).filter(User.email == email).first()

    def get_multi(
        self,
        db: Session,
        role: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """List users with optional role filtering."""
        query = db.query(User)
        if role:
            query = query.filter(User.role == role)
        return query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()


user_service = UserService()
