"""Pydantic schemas for Issue Updates & Comments."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.user import UserResponse


class IssueUpdateBase(BaseModel):
    """Base fields for an issue update."""

    status: str = Field(..., json_schema_extra={"example": "IN_PROGRESS"})
    comment: Optional[str] = Field(None, json_schema_extra={"example": "Road maintenance crew dispatched to site."})
    updated_by: Optional[int] = Field(None, json_schema_extra={"example": 1})


class IssueUpdateCreate(IssueUpdateBase):
    """Schema for adding an update or comment to an issue."""
    pass


class IssueUpdateResponse(BaseModel):
    """Schema for serialized issue update record."""

    id: int
    issue_id: int
    status: str
    comment: Optional[str] = None
    updated_by: Optional[int] = None
    created_at: datetime
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)
