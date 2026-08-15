"""AI Triage Analysis Router for Civic Issues."""

from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from app.config import settings

router = APIRouter(prefix="/ai", tags=["AI Triage"])


class AIAnalyzeRequest(BaseModel):
    title: str
    description: str
    category: Optional[str] = None
    image_path: Optional[str] = None


class AIAnalyzeResponse(BaseModel):
    ai_summary: str
    ai_category: str
    ai_priority: str
    ai_suggested_action: str


@router.post("/analyze", response_model=AIAnalyzeResponse, summary="Perform Generative AI triage on an issue report")
def analyze_issue(request: AIAnalyzeRequest) -> AIAnalyzeResponse:
    """
    Analyzes civic report text using Groq LLM if API key is provided,
    or returns intelligent municipal heuristic categorization.
    """
    title_lower = request.title.lower()
    desc_lower = request.description.lower()
    combined = f"{title_lower} {desc_lower}"

    # If GROQ_API_KEY is configured, we can invoke Groq API
    if settings.GROQ_API_KEY:
        try:
            from groq import Groq
            client = Groq(api_key=settings.GROQ_API_KEY)
            prompt = f"""
You are an expert municipal civic operations AI for CIVICFIX.
Analyze this citizen report:
Title: {request.title}
Description: {request.description}
Reported Category: {request.category or 'Unknown'}

Return a JSON with:
- ai_summary: 1 concise sentence summarizing the severity and problem
- ai_category: best category (Pothole, Streetlight, Water Leakage, Garbage, Drainage, Road Damage, Other)
- ai_priority: (CRITICAL, HIGH, MEDIUM, LOW)
- ai_suggested_action: concrete municipal dispatch recommendation
"""
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=settings.GROQ_MODEL,
                response_format={"type": "json_object"}
            )
            import json
            parsed = json.loads(chat_completion.choices[0].message.content)
            return AIAnalyzeResponse(
                ai_summary=parsed.get("ai_summary", "Civic issue logged for inspection."),
                ai_category=parsed.get("ai_category", request.category or "Other"),
                ai_priority=parsed.get("ai_priority", "MEDIUM"),
                ai_suggested_action=parsed.get("ai_suggested_action", "Assign field technician for verification.")
            )
        except Exception:
            pass  # Fallback to local rule-based heuristic

    # Smart Rule-Based Municipal Heuristic Triage
    if any(w in combined for w in ["pothole", "crater", "asphalt", "bump"]):
        ai_cat = "Pothole"
        ai_prio = "HIGH" if any(w in combined for w in ["deep", "hazard", "skid", "accident", "damage", "danger"]) else "MEDIUM"
        ai_sum = "Roadway surface crater creating potential traffic hazard and vehicular damage."
        ai_act = "Deploy road maintenance asphalt patch crew with safety cones within 24 hours."
    elif any(w in combined for w in ["light", "dark", "lamp", "pole", "bulb", "electric"]):
        ai_cat = "Streetlight"
        ai_prio = "HIGH" if any(w in combined for w in ["junction", "crossroad", "crime", "darkness"]) else "MEDIUM"
        ai_sum = "Streetlight fixture outage impairing nighttime visibility and pedestrian safety."
        ai_act = "Dispatch electrical line technician to inspect wiring and replace LED module."
    elif any(w in combined for w in ["water", "leak", "pipe", "burst", "flood", "drain", "drainage"]):
        ai_cat = "Water Leakage" if "pipe" in combined or "leak" in combined else "Drainage"
        ai_prio = "HIGH" if any(w in combined for w in ["burst", "flooding", "clean water", "overflow"]) else "MEDIUM"
        ai_sum = "Municipal water/drainage infrastructure failure causing localized overflow."
        ai_act = "Isolate sector distribution valve and replace damaged pipe coupling."
    elif any(w in combined for w in ["garbage", "waste", "trash", "dump", "bin", "smell", "stink"]):
        ai_cat = "Garbage"
        ai_prio = "HIGH" if any(w in combined for w in ["blocking", "days", "stray", "hazard"]) else "MEDIUM"
        ai_sum = "Accumulation of uncollected solid waste obstructing public walkway."
        ai_act = "Dispatch municipal waste compactor truck and sanitize collection bay."
    else:
        ai_cat = request.category or "Other"
        ai_prio = "MEDIUM"
        ai_sum = f"Civic report regarding {request.title} logged for municipal inspection."
        ai_act = "Assign zonal ward inspector for on-site assessment."

    return AIAnalyzeResponse(
        ai_summary=ai_sum,
        ai_category=ai_cat,
        ai_priority=ai_prio,
        ai_suggested_action=ai_act
    )
