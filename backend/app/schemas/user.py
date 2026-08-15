"""Pydantic schemas for Users."""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
import re


class UserRole(str, Enum):
    """Roles available for users."""

    RESIDENT = "resident"
    ADMIN = "admin"


class UserBase(BaseModel):
    """Base user schema."""

    name: str = Field(..., min_length=2, max_length=100, json_schema_extra={"example": "Jane Resident"})
    email: str = Field(..., json_schema_extra={"example": "resident@civicfix.org"})
    role: UserRole = Field(default=UserRole.RESIDENT, json_schema_extra={"example": UserRole.RESIDENT})

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("Invalid email address format")
        return v


class UserCreate(UserBase):
    """Schema for registering or seeding a user."""
    pass


class UserResponse(UserBase):
    """Schema for user output."""

    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
