"""SQLAlchemy User Model."""

from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base


class UserRole(str, Enum):
    """User roles within CivicFix."""

    RESIDENT = "resident"
    ADMIN = "admin"


class User(Base):
    """Represents a platform user (Resident or City Administrator)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    role = Column(String(20), default=UserRole.RESIDENT.value, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    issues_created = relationship(
        "Issue",
        foreign_keys="Issue.created_by",
        back_populates="creator",
        cascade="all, delete-orphan",
    )
    issues_assigned = relationship(
        "Issue",
        foreign_keys="Issue.assigned_to",
        back_populates="assignee",
    )
    issue_updates = relationship(
        "IssueUpdate",
        foreign_keys="IssueUpdate.updated_by",
        back_populates="user",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} name={self.name!r} role={self.role!r}>"
