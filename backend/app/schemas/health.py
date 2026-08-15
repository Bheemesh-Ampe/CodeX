"""Health check Pydantic schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Schema for health endpoint response."""

    status: str = Field(..., example="healthy")
    app_name: str = Field(..., example="CivicFix")
    version: str = Field(..., example="0.1.0")
    database: str = Field(..., example="connected")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
