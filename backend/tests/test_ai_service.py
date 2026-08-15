"""Unit and integration tests for Groq AI Service and AI-enhanced issue creation (Prompt 5)."""

import json
from unittest.mock import patch, MagicMock
import httpx
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ai_service import AIService, ai_service, ALLOWED_CATEGORIES, ALLOWED_PRIORITIES
from app.schemas.issue import AIAnalysisResult

client = TestClient(app)


# 1. Successful AI Response
def test_successful_ai_response():
    """Test AI service parsing a valid Groq response."""
    service = AIService(api_key="gsk_test_mock_key")

    mock_groq_json = {
        "category": "Road Damage",
        "priority": "HIGH",
        "summary": "Deep pothole damaging car tires on main road.",
        "suggested_action": "Dispatch emergency road crew to patch pothole.",
    }
    mock_api_payload = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(mock_groq_json),
                }
            }
        ]
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_api_payload

    with patch("httpx.Client.post", return_value=mock_response):
        result = service.analyze_issue(
            title="Massive crater on 4th Ave",
            description="Deep pothole on 4th Ave popping vehicle tires.",
        )

        assert isinstance(result, AIAnalysisResult)
        assert result.category == "Road Damage"
        assert result.priority == "HIGH"
        assert result.summary == mock_groq_json["summary"]
        assert result.suggested_action == mock_groq_json["suggested_action"]
        assert result.ai_status == "success"


# 2. Malformed AI Response
def test_malformed_ai_response():
    """Test AI service handling corrupted or invalid JSON output from the model."""
    service = AIService(api_key="gsk_test_mock_key")

    # Corrupted JSON string
    mock_api_payload = {
        "choices": [
            {
                "message": {
                    "content": "Here is the analysis: {category: 'Broken', priority: HIGH, summary: incomplete...",
                }
            }
        ]
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_api_payload

    with patch("httpx.Client.post", return_value=mock_response):
        original_desc = "Streetlight is completely off at night near the school."
        result = service.analyze_issue(
            title="Broken Light",
            description=original_desc,
        )

        assert isinstance(result, AIAnalysisResult)
        assert result.category == "Other"
        assert result.priority == "MEDIUM"
        assert result.summary == original_desc
        assert result.suggested_action == "Review the reported issue manually."
        assert result.ai_status == "fallback"


# 3. Groq Unavailable (HTTP 500 / Network Error)
def test_groq_unavailable_http_error():
    """Test AI service handling Groq server 503 error."""
    service = AIService(api_key="gsk_test_mock_key")

    mock_response = MagicMock()
    mock_response.status_code = 503

    with patch("httpx.Client.post", return_value=mock_response):
        original_desc = "Clogged storm drain causing street flooding."
        result = service.analyze_issue(
            title="Flooded street",
            description=original_desc,
        )

        assert result.ai_status == "fallback"
        assert result.category == "Other"
        assert result.priority == "MEDIUM"
        assert result.summary == original_desc
        assert result.suggested_action == "Review the reported issue manually."


def test_groq_unavailable_network_exception():
    """Test AI service handling connection timeouts or network failures."""
    service = AIService(api_key="gsk_test_mock_key")

    with patch("httpx.Client.post", side_effect=httpx.ConnectError("Connection refused")):
        original_desc = "Fallen tree blocking intersection."
        result = service.analyze_issue(
            title="Fallen tree",
            description=original_desc,
        )

        assert result.ai_status == "fallback"
        assert result.category == "Other"
        assert result.priority == "MEDIUM"
        assert result.summary == original_desc


# 4. Fallback Behavior (No API Key)
def test_fallback_behavior_no_api_key():
    """Test fallback when GROQ_API_KEY is unset or empty."""
    service = AIService(api_key="")
    original_desc = "Graffiti on subway entrance wall."

    result = service.analyze_issue(
        title="Graffiti report",
        description=original_desc,
    )

    assert result.ai_status == "fallback"
    assert result.category == "Other"
    assert result.priority == "MEDIUM"
    assert result.summary == original_desc
    assert result.suggested_action == "Review the reported issue manually."


# 5. Allowed Categories and Priorities Validation
def test_allowed_categories_and_priorities_normalization():
    """Test category and priority normalization against allowed lists."""
    service = AIService()

    # Valid categories
    for cat in ALLOWED_CATEGORIES:
        assert service._normalize_category(cat) == cat
        assert service._normalize_category(cat.lower()) == cat

    # Fuzzy category normalization
    assert service._normalize_category("pothole in middle of street") == "Road Damage"
    assert service._normalize_category("overflowing trash bin") == "Garbage/Waste"
    assert service._normalize_category("water pipe burst") == "Water Leakage"
    assert service._normalize_category("streetlight outage") == "Street Light"
    assert service._normalize_category("unknown strange item") == "Other"

    # Priorities
    for prio in ALLOWED_PRIORITIES:
        assert service._normalize_priority(prio) == prio
        assert service._normalize_priority(prio.lower()) == prio
    assert service._normalize_priority("CRITICAL") == "HIGH"
    assert service._normalize_priority("unknown") == "MEDIUM"


# 6. End-to-End Issue Creation with AI Enrichment
def test_issue_creation_with_ai_success():
    """Test POST /api/issues endpoint enriched with successful AI triage."""
    mock_ai_output = AIAnalysisResult(
        category="Public Safety",
        priority="HIGH",
        summary="Exposed high voltage electrical wire hanging over sidewalk.",
        suggested_action="Dispatch emergency electrical utility crew immediately.",
        ai_status="success",
    )

    with patch.object(ai_service, "analyze_issue", return_value=mock_ai_output):
        payload = {
            "title": "Exposed Power Wire",
            "description": "Live electric wire hanging down near the playground.",
            "latitude": 37.7790,
            "longitude": -122.4190,
            "address": "Playground on 7th St",
        }
        response = client.post("/api/issues", json=payload)
        assert response.status_code == 201
        data = response.json()

        assert data["ai_status"] == "success"
        assert data["ai_category"] == "Public Safety"
        assert data["ai_priority"] == "HIGH"
        assert data["ai_summary"] == mock_ai_output.summary
        assert data["ai_suggested_action"] == mock_ai_output.suggested_action
        assert data["category"] == "Public Safety"
        assert data["priority"] == "HIGH"


def test_issue_creation_with_ai_fallback():
    """Test POST /api/issues continues working normally when AI service is unavailable."""
    original_desc = "Garbage scattered across the alleyway."
    mock_fallback_output = AIAnalysisResult(
        category="Other",
        priority="MEDIUM",
        summary=original_desc,
        suggested_action="Review the reported issue manually.",
        ai_status="fallback",
    )

    with patch.object(ai_service, "analyze_issue", return_value=mock_fallback_output):
        payload = {
            "title": "Alleyway Trash",
            "description": original_desc,
            "latitude": 37.7810,
            "longitude": -122.4150,
        }
        response = client.post("/api/issues", json=payload)
        assert response.status_code == 201
        data = response.json()

        assert data["ai_status"] == "fallback"
        assert data["ai_category"] == "Other"
        assert data["ai_priority"] == "MEDIUM"
        assert data["ai_summary"] == original_desc
        assert data["ai_suggested_action"] == "Review the reported issue manually."
