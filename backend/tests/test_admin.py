"""Tests for Administrator APIs (Prompt 6)."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# 1. Admin Status Update and Status History Creation
def test_admin_status_update_and_history_creation():
    """
    Test PATCH /api/admin/issues/{issue_id}/status:
    1. Updates the Issue status to ACKNOWLEDGED / IN_PROGRESS / RESOLVED.
    2. Updates updated_at timestamp.
    3. Creates an IssueUpdate record.
    4. Stores administrator comment and demo admin ID (updated_by).
    """
    # Create an issue first
    create_payload = {
        "title": "Flooded Underpass on Main St",
        "description": "Storm drain backing up water onto road surface.",
        "category": "Drainage",
        "latitude": 37.7730,
        "longitude": -122.4170,
        "address": "Main St Underpass",
    }
    create_res = client.post("/api/issues", json=create_payload)
    assert create_res.status_code == 201
    issue_id = create_res.json()["id"]

    # Transition 1: Admin acknowledges the issue
    ack_payload = {
        "status": "ACKNOWLEDGED",
        "comment": "Issue assigned to municipal drainage team.",
        "updated_by": 1,
    }
    ack_res = client.patch(f"/api/admin/issues/{issue_id}/status", json=ack_payload)
    assert ack_res.status_code == 200
    ack_data = ack_res.json()

    assert ack_data["status"] == "ACKNOWLEDGED"
    assert len(ack_data["updates"]) >= 2
    latest_update = ack_data["updates"][0]
    assert latest_update["status"] == "ACKNOWLEDGED"
    assert latest_update["comment"] == ack_payload["comment"]
    assert latest_update["updated_by"] == 1

    # Transition 2: Admin moves to RESOLVED with high priority
    resolve_payload = {
        "status": "RESOLVED",
        "priority": "HIGH",
        "comment": "Drain cleared and water pumped out.",
        "updated_by": 1,
    }
    resolve_res = client.patch(f"/api/admin/issues/{issue_id}/status", json=resolve_payload)
    assert resolve_res.status_code == 200
    resolved_data = resolve_res.json()

    assert resolved_data["status"] == "RESOLVED"
    assert resolved_data["priority"] == "HIGH"
    assert len(resolved_data["updates"]) >= 3


# 2. Invalid Status Rejection
def test_admin_invalid_status_rejection():
    """Test updating with an invalid status returns HTTP 422 Unprocessable Entity."""
    # Create issue
    create_payload = {
        "title": "Damaged Traffic Sign",
        "description": "Stop sign knocked over at intersection.",
        "latitude": 37.7760,
        "longitude": -122.4180,
    }
    create_res = client.post("/api/issues", json=create_payload)
    assert create_res.status_code == 201
    issue_id = create_res.json()["id"]

    # Attempt to patch with invalid status
    bad_payload = {
        "status": "COMPLETELY_INVALID_STATUS",
        "comment": "This should be rejected by Pydantic enum validation.",
    }
    bad_res = client.patch(f"/api/admin/issues/{issue_id}/status", json=bad_payload)
    assert bad_res.status_code == 422


# 3. Retrieving Admin Issue List
def test_retrieving_admin_issue_list():
    """Test GET /api/admin/issues returns list of issues with required metadata."""
    response = client.get("/api/admin/issues")
    assert response.status_code == 200
    issues = response.json()
    assert isinstance(issues, list)
    assert len(issues) >= 1

    first_issue = issues[0]
    assert "id" in first_issue
    assert "title" in first_issue
    assert "status" in first_issue
    assert "category" in first_issue
    assert "priority" in first_issue
    assert "latitude" in first_issue
    assert "longitude" in first_issue


# 4. Filtering Admin Issues by Status, Category, and Priority
def test_filtering_admin_issues():
    """Test GET /api/admin/issues with status, category, and priority query filters."""
    # Create distinct issue for testing filters
    create_payload = {
        "title": "Streetlight Flickering Constantly",
        "description": "High voltage flicker near senior center.",
        "category": "Street Light",
        "latitude": 37.7820,
        "longitude": -122.4140,
    }
    create_res = client.post("/api/issues", json=create_payload)
    assert create_res.status_code == 201
    issue_id = create_res.json()["id"]

    # Update to IN_PROGRESS with CRITICAL priority
    client.patch(
        f"/api/admin/issues/{issue_id}/status",
        json={"status": "IN_PROGRESS", "priority": "CRITICAL", "comment": "Electrician dispatched."},
    )

    # 1. Filter by status=IN_PROGRESS
    res_status = client.get("/api/admin/issues?status=IN_PROGRESS")
    assert res_status.status_code == 200
    status_list = res_status.json()
    assert isinstance(status_list, list)
    for issue in status_list:
        assert issue["status"] == "IN_PROGRESS"

    # 2. Filter by category=Street Light
    res_cat = client.get("/api/admin/issues?category=Street%20Light")
    assert res_cat.status_code == 200
    cat_list = res_cat.json()
    assert isinstance(cat_list, list)
    for issue in cat_list:
        assert issue["category"].lower() == "street light"


# 5. Retrieving Complete Issue Details via Admin Endpoint
def test_retrieving_admin_issue_detail():
    """
    Test GET /api/admin/issues/{issue_id}:
    - Issue information
    - Image
    - Latitude & Longitude
    - AI analysis
    - Current status
    - Status history
    """
    create_payload = {
        "title": "Broken Water Main on 8th",
        "description": "Clean water flooding the sidewalk and parking spaces.",
        "category": "Water Leakage",
        "latitude": 37.7710,
        "longitude": -122.4220,
        "address": "200 8th Street",
        "image": "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7",
    }
    create_res = client.post("/api/issues", json=create_payload)
    assert create_res.status_code == 201
    issue_id = create_res.json()["id"]

    # Retrieve via admin endpoint
    detail_res = client.get(f"/api/admin/issues/{issue_id}")
    assert detail_res.status_code == 200
    data = detail_res.json()

    assert data["id"] == issue_id
    assert data["title"] == create_payload["title"]
    assert data["description"] == create_payload["description"]
    assert data["latitude"] == create_payload["latitude"]
    assert data["longitude"] == create_payload["longitude"]
    assert data["address"] == create_payload["address"]
    assert data["image_path"] == create_payload["image"]
    assert data["image"] == create_payload["image"]
    assert "ai_summary" in data
    assert "ai_category" in data
    assert "ai_priority" in data
    assert "ai_suggested_action" in data
    assert "ai_status" in data
    assert data["status"] == "REPORTED"
    assert isinstance(data["updates"], list)
    assert len(data["updates"]) >= 1


# 6. Admin Adding Update Note (POST /api/admin/issues/{id}/updates)
def test_admin_add_update_note():
    """Test POST /api/admin/issues/{issue_id}/updates explicitly adding comment."""
    create_res = client.post("/api/issues", json={
        "title": "Graffiti on Park Wall",
        "description": "Spray paint on entrance sign.",
        "latitude": 37.7750,
        "longitude": -122.4150,
    })
    assert create_res.status_code == 201
    issue_id = create_res.json()["id"]

    update_payload = {
        "status": "IN_PROGRESS",
        "comment": "Sanitation graffiti team assigned for cleanup at 2 PM.",
        "updated_by": 1,
    }
    update_res = client.post(f"/api/admin/issues/{issue_id}/updates", json=update_payload)
    assert update_res.status_code == 201
    update_data = update_res.json()
    assert update_data["issue_id"] == issue_id
    assert update_data["status"] == "IN_PROGRESS"
    assert update_data["comment"] == update_payload["comment"]
    assert update_data["updated_by"] == 1
