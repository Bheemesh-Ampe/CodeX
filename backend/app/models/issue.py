"""SQLAlchemy Issue Model."""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Index, desc
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base


class Issue(Base):
    """Represents a civic issue reported in CivicFix."""

    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(100), default="Other", nullable=False, index=True)
    
    # Sensible defaults per Prompt 2 requirements
    status = Column(String(50), default="REPORTED", nullable=False, index=True)
    priority = Column(String(50), default="MEDIUM", nullable=False, index=True)

    # Geographic location for frontend map rendering and spatial queries
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    address = Column(String(255), nullable=True)

    # Photograph / media file path
    image_path = Column(String(500), nullable=True)

    # Generative AI analysis fields (Groq integration)
    ai_summary = Column(Text, nullable=True)
    ai_category = Column(String(100), nullable=True)
    ai_priority = Column(String(50), nullable=True)
    ai_suggested_action = Column(Text, nullable=True)
    ai_status = Column(String(50), default="fallback", nullable=True)

    # User relationships
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    creator = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="issues_created",
    )
    assignee = relationship(
        "User",
        foreign_keys=[assigned_to],
        back_populates="issues_assigned",
    )
    updates = relationship(
        "IssueUpdate",
        back_populates="issue",
        cascade="all, delete-orphan",
        order_by="desc(IssueUpdate.id)",
    )

    # Table indexes for high-performance querying
    __table_args__ = (
        Index("ix_issues_location", "latitude", "longitude"),
        Index("ix_issues_status_category", "status", "category"),
    )

    def __repr__(self) -> str:
        return f"<Issue id={self.id} title={self.title!r} status={self.status!r}>"
