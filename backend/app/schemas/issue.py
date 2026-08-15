"""Pydantic schemas for Civic Issues."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, field_validator
from app.schemas.user import UserResponse
from app.schemas.issue_update import IssueUpdateResponse


class IssueStatus(str, Enum):
    """Supported statuses for an issue."""

    REPORTED = "REPORTED"
    IN_REVIEW = "IN_REVIEW"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"


class IssuePriority(str, Enum):
    """Priority levels for an issue."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IssueBase(BaseModel):
    """Base fields for a civic issue."""

    title: str = Field(..., min_length=3, max_length=200, example="Large Pothole on Elm St")
    description: str = Field(..., min_length=5, example="Deep crater damaging tires near the crosswalk.")
    category: str = Field(default="Other", example="Pothole")
    latitude: float = Field(..., ge=-90.0, le=90.0, example=37.7749)
    longitude: float = Field(..., ge=-180.0, le=180.0, example=-122.4194)
    address: Optional[str] = Field(None, example="742 Elm Street, Downtown")
    image_path: Optional[str] = Field(None, example="https://images.unsplash.com/photo-1515162816999-a0c47dc192f7")

    @field_validator("title", "description")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


class IssueCreate(IssueBase):
    """Schema for reporting a new issue."""

    priority: Optional[IssuePriority] = Field(default=IssuePriority.MEDIUM)
    created_by: Optional[int] = Field(None, description="User ID of the reporter")


class IssueUpdateSchema(BaseModel):
    """Schema for updating issue fields."""

    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=5)
    category: Optional[str] = None
    status: Optional[IssueStatus] = None
    priority: Optional[IssuePriority] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    address: Optional[str] = None
    image_path: Optional[str] = None
    assigned_to: Optional[int] = None
    ai_summary: Optional[str] = None
    ai_category: Optional[str] = None
    ai_priority: Optional[str] = None
    ai_suggested_action: Optional[str] = None


class IssueStatusUpdate(BaseModel):
    """Schema for status changes and adding progress comments."""

    status: IssueStatus = Field(..., example=IssueStatus.IN_PROGRESS)
    priority: Optional[IssuePriority] = Field(None, example=IssuePriority.HIGH)
    comment: Optional[str] = Field(None, example="Road maintenance crew dispatched to site.")
    updated_by: Optional[int] = Field(None, example=1, description="Admin/User ID making the update")


class IssueResponse(IssueBase):
    """Serialized representation of an Issue."""

    id: int
    status: str
    priority: str
    image_path: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_category: Optional[str] = None
    ai_priority: Optional[str] = None
    ai_suggested_action: Optional[str] = None
    created_by: Optional[int] = None
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    creator: Optional[UserResponse] = None
    assignee: Optional[UserResponse] = None
    updates: List[IssueUpdateResponse] = []

    class Config:
        from_attributes = True


class IssueListResponse(BaseModel):
    """Paginated list of issues."""

    total: int
    items: List[IssueResponse]


class IssueStatsResponse(BaseModel):
    """Aggregate breakdown of issues for administrator dashboard."""

    total_issues: int
    by_status: Dict[str, int]
    by_category: Dict[str, int]
    by_priority: Dict[str, int]
