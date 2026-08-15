"""Tests for /api/issues REST endpoints conforming to Prompt 3 requirements."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# 1. Successful Issue Creation
def test_successful_issue_creation():
    """
    Test successful issue creation via POST /api/issues with all required & optional fields:
    - Validates request payload
    - Saves to SQLite
    - Sets status to REPORTED
    - Sets default priority to MEDIUM
    - Returns HTTP 201 with created issue
    """
    payload = {
        "title": "Severe Pothole on Market Street",
        "description": "Deep pothole causing hazard for cyclists and vehicles near the bus stop.",
        "category": "Pothole",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "address": "123 Market St, San Francisco, CA",
        "image": "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7",
    }
    response = client.post("/api/issues", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["id"] is not None
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["category"] == "Pothole"
    assert data["latitude"] == 37.7749
    assert data["longitude"] == -122.4194
    assert data["address"] == payload["address"]
    assert data["image_path"] == payload["image"]
    assert data["image"] == payload["image"]
    assert data["status"] == "REPORTED"
    assert data["priority"] == "MEDIUM"

    # Verify initial status history is created
    assert "updates" in data
    assert len(data["updates"]) >= 1
    assert data["updates"][0]["status"] == "REPORTED"


def test_successful_issue_creation_minimal_fields():
    """Test issue creation with only mandatory fields."""
    payload = {
        "title": "Broken Streetlight",
        "description": "Streetlight flickers and goes dark during the night.",
        "latitude": 37.7800,
        "longitude": -122.4200,
    }
    response = client.post("/api/issues", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["id"] is not None
    assert data["title"] == payload["title"]
    assert data["status"] == "REPORTED"
    assert data["priority"] == "MEDIUM"
    assert data["category"] == "Other"
    assert data["latitude"] == 37.7800
    assert data["longitude"] == -122.4200
    assert data["address"] is None


# 2. Invalid Issue Data Validation (Pydantic)
def test_invalid_issue_data_missing_fields():
    """Test validation errors when required fields are missing."""
    # Missing description and coordinates
    payload = {
        "title": "Missing details",
    }
    response = client.post("/api/issues", json=payload)
    assert response.status_code == 422
    errors = response.json().get("detail", [])
    missing_fields = {err["loc"][-1] for err in errors}
    assert "description" in missing_fields
    assert "latitude" in missing_fields
    assert "longitude" in missing_fields


def test_invalid_issue_data_out_of_range_coordinates():
    """Test validation fails when latitude or longitude are out of geographic range."""
    # Invalid latitude > 90
    payload_bad_lat = {
        "title": "Invalid Latitude Issue",
        "description": "Testing invalid latitude value",
        "latitude": 120.0,
        "longitude": -122.4194,
    }
    res_lat = client.post("/api/issues", json=payload_bad_lat)
    assert res_lat.status_code == 422

    # Invalid longitude < -180
    payload_bad_lon = {
        "title": "Invalid Longitude Issue",
        "description": "Testing invalid longitude value",
        "latitude": 37.7749,
        "longitude": -200.0,
    }
    res_lon = client.post("/api/issues", json=payload_bad_lon)
    assert res_lon.status_code == 422


def test_invalid_issue_data_blank_strings():
    """Test validation fails when title or description is empty or whitespace only."""
    payload = {
        "title": "   ",
        "description": "   ",
        "latitude": 37.7749,
        "longitude": -122.4194,
    }
    response = client.post("/api/issues", json=payload)
    assert response.status_code == 422


# 3. Retrieving Issues (GET /api/issues)
def test_retrieving_issues_list():
    """
    Test GET /api/issues:
    - Returns a list of issues
    - Includes latitude and longitude
    - Excludes unnecessary internal database information
    """
    response = client.get("/api/issues")
    assert response.status_code == 200
    issues = response.json()
    assert isinstance(issues, list)
    assert len(issues) >= 1

    first_issue = issues[0]
    assert "id" in first_issue
    assert "title" in first_issue
    assert "description" in first_issue
    assert "latitude" in first_issue
    assert "longitude" in first_issue
    assert "status" in first_issue
    assert "priority" in first_issue
    assert isinstance(first_issue["latitude"], (int, float))
    assert isinstance(first_issue["longitude"], (int, float))


def test_retrieving_issues_with_filters():
    """Test GET /api/issues with status and category query filters."""
    # Create distinct issue for filtering
    unique_cat = "Graffiti Special Filter"
    payload = {
        "title": "Filter Test Issue",
        "description": "Issue specifically for testing query filters.",
        "category": unique_cat,
        "latitude": 37.7600,
        "longitude": -122.4400,
    }
    create_res = client.post("/api/issues", json=payload)
    assert create_res.status_code == 201

    # Filter by category
    res_cat = client.get(f"/api/issues?category={unique_cat}")
    assert res_cat.status_code == 200
    cat_issues = res_cat.json()
    assert isinstance(cat_issues, list)
    assert len(cat_issues) >= 1
    for item in cat_issues:
        assert item["category"].lower() == unique_cat.lower()

    # Filter by status
    res_status = client.get("/api/issues?status=REPORTED")
    assert res_status.status_code == 200
    status_issues = res_status.json()
    assert isinstance(status_issues, list)
    for item in status_issues:
        assert item["status"] == "REPORTED"


# 4. Retrieving a Single Issue (GET /api/issues/{issue_id})
def test_retrieving_single_issue_with_status_history():
    """
    Test GET /api/issues/{issue_id}:
    - Returns complete issue details
    - Includes complete status history
    """
    payload = {
        "title": "Fallen Tree Branch on sidewalk",
        "description": "Large branch obstructing the public sidewalk.",
        "category": "Trees & Vegetation",
        "latitude": 37.7720,
        "longitude": -122.4250,
        "address": "400 Oak Street",
    }
    create_res = client.post("/api/issues", json=payload)
    assert create_res.status_code == 201
    issue_id = create_res.json()["id"]

    # Fetch by ID
    get_res = client.get(f"/api/issues/{issue_id}")
    assert get_res.status_code == 200
    fetched = get_res.json()

    assert fetched["id"] == issue_id
    assert fetched["title"] == payload["title"]
    assert fetched["description"] == payload["description"]
    assert fetched["latitude"] == payload["latitude"]
    assert fetched["longitude"] == payload["longitude"]
    assert fetched["address"] == payload["address"]
    assert fetched["status"] == "REPORTED"
    assert fetched["priority"] == "MEDIUM"

    # Status history verification
    assert "updates" in fetched
    assert isinstance(fetched["updates"], list)
    assert len(fetched["updates"]) >= 1
    assert fetched["updates"][0]["status"] == "REPORTED"


# 5. Issue Not Found (GET /api/issues/{issue_id})
def test_issue_not_found():
    """Test retrieving non-existent issue returns HTTP 404."""
    non_existent_id = 999999
    response = client.get(f"/api/issues/{non_existent_id}")
    assert response.status_code == 404
    error = response.json()
    assert "detail" in error
    assert str(non_existent_id) in error["detail"]


# Additional workflow tests
def test_admin_update_issue_status_and_audit_log():
    """Test updating issue status and verifying audit trail addition."""
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
    assert len(updated["updates"]) >= 2


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
