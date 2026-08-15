"""Pydantic schemas for Civic Issues and AI Analysis."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
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


class AIAnalysisResult(BaseModel):
    """Structured result returned by Groq AI service."""

    category: str = Field(..., json_schema_extra={"example": "Road Damage"})
    priority: str = Field(..., json_schema_extra={"example": "HIGH"})
    summary: str = Field(..., json_schema_extra={"example": "Severe pothole damaging vehicles."})
    suggested_action: str = Field(..., json_schema_extra={"example": "Dispatch road maintenance team for emergency asphalt patching."})
    ai_status: str = Field(default="success", json_schema_extra={"example": "success"})  # "success" or "fallback"

    model_config = ConfigDict(from_attributes=True)


class IssueBase(BaseModel):
    """Base fields for a civic issue."""

    title: str = Field(
        ...,
        min_length=3,
        max_length=200,
        json_schema_extra={"example": "Large Pothole on Elm St"},
    )
    description: str = Field(
        ...,
        min_length=5,
        json_schema_extra={"example": "Deep crater damaging tires near the crosswalk."},
    )
    category: str = Field(
        default="Other",
        json_schema_extra={"example": "Pothole"},
    )
    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        json_schema_extra={"example": 37.7749},
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        json_schema_extra={"example": -122.4194},
    )
    address: Optional[str] = Field(
        None,
        json_schema_extra={"example": "742 Elm Street, Downtown"},
    )
    image_path: Optional[str] = Field(
        None,
        json_schema_extra={"example": "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7"},
    )
    image: Optional[str] = Field(
        None,
        json_schema_extra={"example": "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7"},
    )

    @field_validator("title", "description")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        if isinstance(v, str):
            val = v.strip()
            if not val:
                raise ValueError("Field cannot be empty or blank whitespace")
            return val
        return v

    @model_validator(mode="before")
    @classmethod
    def sync_image_fields(cls, data):
        if isinstance(data, dict):
            # If image is passed instead of image_path, populate image_path
            if data.get("image") and not data.get("image_path"):
                data["image_path"] = data["image"]
            elif data.get("image_path") and not data.get("image"):
                data["image"] = data["image_path"]
        return data


class IssueCreate(IssueBase):
    """Schema for reporting a new issue by a resident."""

    category: Optional[str] = Field(default="Other")
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
    image: Optional[str] = None
    assigned_to: Optional[int] = None
    ai_summary: Optional[str] = None
    ai_category: Optional[str] = None
    ai_priority: Optional[str] = None
    ai_suggested_action: Optional[str] = None
    ai_status: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def sync_update_image(cls, data):
        if isinstance(data, dict):
            if data.get("image") and not data.get("image_path"):
                data["image_path"] = data["image"]
        return data


class IssueStatusUpdate(BaseModel):
    """Schema for status changes and adding progress comments."""

    status: IssueStatus = Field(..., json_schema_extra={"example": IssueStatus.IN_PROGRESS})
    priority: Optional[IssuePriority] = Field(None, json_schema_extra={"example": IssuePriority.HIGH})
    comment: Optional[str] = Field(None, json_schema_extra={"example": "Road maintenance crew dispatched to site."})
    updated_by: Optional[int] = Field(None, json_schema_extra={"example": 1}, description="Admin/User ID making the update")


class IssueResponse(IssueBase):
    """Serialized representation of an Issue with coordinates, status, AI metadata, and audit history."""

    id: int
    status: str
    priority: str
    image_path: Optional[str] = None
    image: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_category: Optional[str] = None
    ai_priority: Optional[str] = None
    ai_suggested_action: Optional[str] = None
    ai_status: Optional[str] = "fallback"
    created_by: Optional[int] = None
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    creator: Optional[UserResponse] = None
    assignee: Optional[UserResponse] = None
    updates: List[IssueUpdateResponse] = []

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def populate_image(self):
        if self.image_path and not self.image:
            self.image = self.image_path
        return self


class IssueListResponse(BaseModel):
    """Paginated list envelope for issues."""

    total: int
    items: List[IssueResponse]

    model_config = ConfigDict(from_attributes=True)


class IssueStatsResponse(BaseModel):
    """Aggregate breakdown of issues for administrator dashboard."""

    total_issues: int
    by_status: Dict[str, int]
    by_category: Dict[str, int]
    by_priority: Dict[str, int]

    model_config = ConfigDict(from_attributes=True)
