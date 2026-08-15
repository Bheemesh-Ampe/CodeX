"""Tests for /api/issues and /api/users REST endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_user_creation_and_listing():
    """Test creating and listing users."""
    user_data = {
        "name": "David Resident",
        "email": "david.test@civicfix.org",
        "role": "resident",
    }
    response = client.post("/api/users", json=user_data)
    assert response.status_code in [201, 400]  # 400 if already created in previous run

    list_res = client.get("/api/users")
    assert list_res.status_code == 200
    users = list_res.json()
    assert isinstance(users, list)
    assert len(users) >= 1


def test_create_and_get_issue_with_history():
    """Test resident reporting an issue and verifying auto-created IssueUpdate."""
    payload = {
        "title": "Water Leak on 5th Street",
        "description": "Clean water bubbling up through road asphalt.",
        "category": "Water & Drainage",
        "latitude": 37.7850,
        "longitude": -122.4050,
        "address": "500 5th Street",
        "priority": "HIGH",
    }
    create_res = client.post("/api/issues", json=payload)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["id"] is not None
    assert created["title"] == payload["title"]
    assert created["status"] == "REPORTED"  # Default status per prompt 2
    assert created["priority"] == "HIGH"
    assert created["latitude"] == 37.7850
    assert created["longitude"] == -122.4050
    assert len(created["updates"]) >= 1  # Initial status update recorded
    assert created["updates"][0]["status"] == "REPORTED"

    issue_id = created["id"]

    # Retrieve issue details
    get_res = client.get(f"/api/issues/{issue_id}")
    assert get_res.status_code == 200
    fetched = get_res.json()
    assert fetched["id"] == issue_id


def test_admin_update_issue_status_and_audit_log():
    """Test updating issue status and verifying audit trail addition."""
    # Create issue
    payload = {
        "title": "Damaged guardrail",
        "description": "Vehicle crashed into guardrail on exit ramp.",
        "category": "Road & Traffic Safety",
        "latitude": 37.7700,
        "longitude": -122.4100,
    }
    create_res = client.post("/api/issues", json=payload)
    assert create_res.status_code == 201
    issue_id = create_res.json()["id"]

    # Admin updates status to IN_PROGRESS
    status_update = {
        "status": "IN_PROGRESS",
        "priority": "CRITICAL",
        "comment": "Highway patrol notified and crew on route.",
    }
    patch_res = client.patch(f"/api/issues/{issue_id}/status", json=status_update)
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated["status"] == "IN_PROGRESS"
    assert updated["priority"] == "CRITICAL"
    assert len(updated["updates"]) >= 2  # REPORTED + IN_PROGRESS


def test_add_issue_comment_update():
    """Test explicitly appending a comment to an issue."""
    payload = {
        "title": "Graffiti on Public Library Wall",
        "description": "Spray paint on the east side facade.",
        "category": "Graffiti & Vandalism",
        "latitude": 37.7800,
        "longitude": -122.4150,
    }
    create_res = client.post("/api/issues", json=payload)
    assert create_res.status_code == 201
    issue_id = create_res.json()["id"]

    # Add comment
    comment_payload = {
        "status": "IN_REVIEW",
        "comment": "Cleaning crew scheduled for tomorrow morning.",
    }
    comment_res = client.post(f"/api/issues/{issue_id}/updates", json=comment_payload)
    assert comment_res.status_code == 201
    comment_data = comment_res.json()
    assert comment_data["comment"] == comment_payload["comment"]
    assert comment_data["status"] == "IN_REVIEW"


def test_issues_stats_summary():
    """Test stats summary endpoint."""
    res = client.get("/api/issues/stats/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_issues" in data
    assert "by_status" in data
    assert "by_category" in data
    assert "by_priority" in data
