"""Dedicated AI Service using Groq for Civic Issue Analysis."""

import json
import logging
import re
from typing import Optional, Dict, Any
import httpx
from app.config import settings
from app.schemas.issue import AIAnalysisResult

logger = logging.getLogger("civicfix.ai_service")

ALLOWED_CATEGORIES = [
    "Road Damage",
    "Garbage/Waste",
    "Street Light",
    "Drainage",
    "Water Leakage",
    "Public Safety",
    "Other",
]

ALLOWED_PRIORITIES = ["LOW", "MEDIUM", "HIGH"]

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"


class AIService:
    """Service handling generative AI issue analysis via Groq."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self._api_key = api_key
        self._model = model

    @property
    def api_key(self) -> str:
        return self._api_key or settings.GROQ_API_KEY or ""

    @property
    def model(self) -> str:
        return self._model or settings.GROQ_MODEL or "llama-3.3-70b-versatile"

    def get_fallback(self, description: str) -> AIAnalysisResult:
        """Standard fallback response when Groq is unavailable, unconfigured, or returns invalid data."""
        return AIAnalysisResult(
            category="Other",
            priority="MEDIUM",
            summary=description.strip() if description else "Civic issue reported.",
            suggested_action="Review the reported issue manually.",
            ai_status="fallback",
        )

    def _normalize_category(self, raw_category: Optional[str]) -> str:
        """Validate and normalize category against allowed values."""
        if not raw_category:
            return "Other"
        raw = raw_category.strip().lower()
        for cat in ALLOWED_CATEGORIES:
            if cat.lower() == raw:
                return cat

        # Fuzzy category mapping for resilience
        if any(w in raw for w in ["road", "pothole", "pavement", "crack", "asphalt", "sidewalk", "traffic safety"]):
            return "Road Damage"
        if any(w in raw for w in ["garbage", "trash", "waste", "litter", "debris", "dump", "rubbish", "sanitation", "bin"]):
            return "Garbage/Waste"
        if any(w in raw for w in ["light", "lamp", "dark", "illumination", "bulb", "streetlight"]):
            return "Street Light"
        if any(w in raw for w in ["drain", "drainage", "sewer", "flood", "gutter", "storm"]):
            return "Drainage"
        if any(w in raw for w in ["leak", "burst", "water", "pipe", "hydrant", "sprinkler"]):
            return "Water Leakage"
        if any(w in raw for w in ["safety", "hazard", "vandalism", "crime", "danger", "wire", "cable", "tree", "fire"]):
            return "Public Safety"

        return "Other"

    def _normalize_priority(self, raw_priority: Optional[str]) -> str:
        """Validate and normalize priority against allowed values."""
        if not raw_priority:
            return "MEDIUM"
        raw = raw_priority.strip().upper()
        if raw in ALLOWED_PRIORITIES:
            return raw
        if "HIGH" in raw or "CRITICAL" in raw or "URGENT" in raw or "EMERGENCY" in raw:
            return "HIGH"
        if "LOW" in raw or "MINOR" in raw:
            return "LOW"
        return "MEDIUM"

    def _parse_ai_json(self, response_text: str, original_description: str) -> AIAnalysisResult:
        """Extract and parse structured JSON from raw model text into predictable Pydantic structure."""
        try:
            clean_text = response_text.strip()
            if "```" in clean_text:
                match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", clean_text)
                if match:
                    clean_text = match.group(1).strip()

            start = clean_text.find("{")
            end = clean_text.rfind("}")
            if start != -1 and end != -1:
                clean_text = clean_text[start : end + 1]

            data = json.loads(clean_text)
            if not isinstance(data, dict):
                raise ValueError("Parsed JSON is not a key-value dictionary")

            category = self._normalize_category(data.get("category"))
            priority = self._normalize_priority(data.get("priority"))
            summary = str(data.get("summary", "")).strip() or original_description
            suggested_action = str(data.get("suggested_action", "")).strip() or "Review the reported issue manually."

            return AIAnalysisResult(
                category=category,
                priority=priority,
                summary=summary,
                suggested_action=suggested_action,
                ai_status="success",
            )
        except Exception as e:
            logger.warning(f"Failed to parse AI response into structure: {e}")
            return self.get_fallback(original_description)

    def analyze_issue(self, title: str, description: str) -> AIAnalysisResult:
        """
        Synchronously analyzes a civic issue description using Groq LLM.
        Returns validated AIAnalysisResult with ai_status='success' or 'fallback'.
        """
        api_key = self.api_key
        if not api_key or not api_key.strip():
            logger.info("GROQ_API_KEY not configured. Falling back to default analysis.")
            return self.get_fallback(description)

        prompt = (
            f"You are the AI triage engine for CivicFix municipal platform.\n"
            f"Analyze this civic issue report and provide a JSON response with:\n"
            f"- category: Exactly one of {json.dumps(ALLOWED_CATEGORIES)}\n"
            f"- priority: Exactly one of {json.dumps(ALLOWED_PRIORITIES)}\n"
            f"- summary: A concise 1-2 sentence overview of the issue.\n"
            f"- suggested_action: Recommended operational action for city administration.\n\n"
            f"Title: {title}\n"
            f"Description: {description}\n\n"
            f"Return ONLY valid JSON."
        )

        headers = {
            "Authorization": f"Bearer {api_key.strip()}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a municipal triage AI. You output ONLY valid JSON matching the requested structure.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "max_tokens": 350,
            "response_format": {"type": "json_object"},
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(GROQ_ENDPOINT, json=payload, headers=headers)
                if response.status_code != 200:
                    logger.warning(f"Groq API returned HTTP {response.status_code}")
                    return self.get_fallback(description)

                resp_data = response.json()
                content = (
                    resp_data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )
                return self._parse_ai_json(content, description)
        except Exception as e:
            logger.warning(f"Groq API communication error: {e}")
            return self.get_fallback(description)


ai_service = AIService()
