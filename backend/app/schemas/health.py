"""Health check Pydantic schemas."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class HealthResponse(BaseModel):
    """Schema for health endpoint response."""

    status: str = Field(..., json_schema_extra={"example": "healthy"})
    app_name: str = Field(..., json_schema_extra={"example": "CivicFix"})
    version: str = Field(..., json_schema_extra={"example": "0.1.0"})
    database: str = Field(..., json_schema_extra={"example": "connected"})
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)
