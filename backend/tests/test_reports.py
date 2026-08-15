"""Unit tests for legacy Reports API endpoints (backwards compatibility)."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_legacy_create_and_get_report():
    """Test legacy /api/reports routing to Issue creation."""
    payload = {
        "title": "Broken bench at Central Park",
        "description": "The wooden planks on the bench are broken and dangerous to sit on.",
        "category": "Public Parks & Greenery",
        "latitude": 37.7795,
        "longitude": -122.4180,
        "address": "Central Park Playground",
    }
    response = client.post("/api/reports", json=payload)
    assert response.status_code == 201
    created = response.json()
    assert created["id"] is not None
    assert created["title"] == payload["title"]
    assert created["latitude"] == 37.7795
    assert created["longitude"] == -122.4180
    assert created["status"] == "REPORTED"
    assert created["priority"] == "MEDIUM"

    report_id = created["id"]

    get_response = client.get(f"/api/reports/{report_id}")
    assert get_response.status_code == 200
    fetched = get_response.json()
    assert fetched["id"] == report_id


def test_legacy_admin_update_report_status():
    """Test legacy /api/reports/{id}/status endpoint."""
    payload = {
        "title": "Blocked Storm Drain Legacy",
        "description": "Leaves and debris blocking the drain during heavy rains.",
        "category": "Water & Drainage",
        "latitude": 37.7600,
        "longitude": -122.4300,
    }
    create_res = client.post("/api/reports", json=payload)
    assert create_res.status_code == 201
    report_id = create_res.json()["id"]

    status_update = {
        "status": "IN_PROGRESS",
        "priority": "HIGH",
        "comment": "Crew dispatched",
    }
    patch_res = client.patch(f"/api/reports/{report_id}/status", json=status_update)
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated["status"] == "IN_PROGRESS"
    assert updated["priority"] == "HIGH"


def test_legacy_list_and_stats():
    """Test legacy listing and summary endpoints."""
    list_res = client.get("/api/reports?limit=10")
    assert list_res.status_code == 200
    assert isinstance(list_res.json(), list)

    stats_res = client.get("/api/reports/stats/summary")
    assert stats_res.status_code == 200
