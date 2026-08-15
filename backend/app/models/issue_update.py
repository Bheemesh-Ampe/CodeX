"""SQLAlchemy IssueUpdate Model."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base


class IssueUpdate(Base):
    """Represents a status transition, progress update, or comment on an issue."""

    __tablename__ = "issue_updates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    issue_id = Column(Integer, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True)
    comment = Column(Text, nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    issue = relationship("Issue", back_populates="updates")
    user = relationship("User", back_populates="issue_updates")

    def __repr__(self) -> str:
        return f"<IssueUpdate id={self.id} issue_id={self.issue_id} status={self.status!r}>"
