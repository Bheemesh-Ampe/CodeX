"""API routes for AI Triage Analysis."""

from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.ai_service import ai_service
from app.schemas.issue import AIAnalysisResult

router = APIRouter(prefix="/ai", tags=["AI Triage"])


class AIAnalyzeRequest(BaseModel):
    """Schema for live AI triage preview request."""

    title: Optional[str] = ""
    description: str = Field(..., min_length=1, description="Resident issue description")
    category: Optional[str] = None
    image_path: Optional[str] = None


@router.post(
    "/analyze",
    response_model=AIAnalysisResult,
    summary="Analyze civic issue with Groq AI",
    description="Analyzes resident issue text and returns category, priority, concise summary, and suggested administrative action.",
)
def analyze_civic_issue(request: AIAnalyzeRequest) -> AIAnalysisResult:
    """Perform on-demand AI triage analysis via Groq."""
    return ai_service.analyze_issue(
        title=request.title or "Civic Issue",
        description=request.description,
    )
