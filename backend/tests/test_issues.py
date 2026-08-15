"""Tests for /api/issues REST endpoints including Safe Image Upload (Prompt 4)."""

import io
import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)

# Helper sample image bytes
SAMPLE_PNG_BYTES = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
SAMPLE_JPG_BYTES = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01"\
                   b"\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00"\
                   b"\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xbf\x00\xff\xd9"


# ==========================================================
# Prompt 4: Safe Image Upload Tests
# ==========================================================

def test_valid_image_upload():
    """Test 1: Valid image upload generating unique filename and storing in backend/uploads/."""
    file_payload = {
        "image": ("pothole_photo.png", io.BytesIO(SAMPLE_PNG_BYTES), "image/png"),
    }
    response = client.post("/api/issues/upload", files=file_payload)
    assert response.status_code == 201
    data = response.json()

    assert "filename" in data
    assert "image_path" in data
    assert data["image_path"].startswith("/uploads/")
    assert data["filename"].endswith(".png")
    # Verify unique filename generated (not original filename)
    assert data["filename"] != "pothole_photo.png"

    # Verify physical file existence in backend/uploads/
    upload_dir = os.path.abspath(settings.UPLOAD_DIR)
    file_path = os.path.join(upload_dir, data["filename"])
    assert os.path.exists(file_path)

    # Test safe retrieval of the uploaded image by filename
    retrieval_res = client.get(f"/api/issues/images/{data['filename']}")
    assert retrieval_res.status_code == 200
    assert len(retrieval_res.content) > 0


def test_invalid_file_type_upload():
    """Test 2: Reject unsupported file formats (.txt, .exe, .sh, etc.)."""
    file_payload = {
        "image": ("malicious_script.sh", io.BytesIO(b"#!/bin/bash\necho hack"), "text/x-shellscript"),
    }
    response = client.post("/api/issues/upload", files=file_payload)
    assert response.status_code == 400
    error_msg = response.json()["detail"]
    assert "Unsupported file format" in error_msg or "Allowed" in error_msg


def test_missing_image_handling():
    """Test 3: Missing image gracefully sets image_path to None and returns 404 for image stream."""
    # Create issue with no image attached
    payload = {
        "title": "Broken Streetlamp No Photo",
        "description": "The lamp post on 3rd avenue is not turning on.",
        "latitude": 37.7750,
        "longitude": -122.4180,
    }
    create_res = client.post("/api/issues", json=payload)
    assert create_res.status_code == 201
    issue_id = create_res.json()["id"]
    assert create_res.json()["image_path"] is None

    # Safe retrieval should return 404 since no image was attached
    img_res = client.get(f"/api/issues/{issue_id}/image")
    assert img_res.status_code == 404


def test_issue_creation_with_image_multipart():
    """Test 4: Issue creation with simultaneous image file upload (multipart/form-data)."""
    form_data = {
        "title": "Damaged Sidewalk with Photo",
        "description": "Concrete slabs pushed up by tree roots creating trip hazard.",
        "latitude": "37.7812",
        "longitude": "-122.4130",
        "category": "Sidewalks",
        "address": "888 Howard Street",
    }
    file_payload = {
        "image": ("sidewalk.jpg", io.BytesIO(SAMPLE_JPG_BYTES), "image/jpeg"),
    }

    response = client.post("/api/issues/with-image", data=form_data, files=file_payload)
    assert response.status_code == 201
    data = response.json()

    assert data["id"] is not None
    assert data["title"] == form_data["title"]
    assert data["status"] == "REPORTED"
    assert data["priority"] == "MEDIUM"
    assert data["image_path"] is not None
    assert data["image_path"].startswith("/uploads/")
    assert data["image_path"].endswith(".jpg")


def test_issue_retrieval_containing_image_information():
    """Test 5: Issue retrieval containing image metadata and safe image file streaming."""
    # 1. Create issue with image
    form_data = {
        "title": "Overflowing Public Garbage Bin",
        "description": "Trash overflowing onto sidewalk near the park entrance.",
        "latitude": "37.7840",
        "longitude": "-122.4080",
        "category": "Sanitation",
    }
    file_payload = {
        "image": ("trash.png", io.BytesIO(SAMPLE_PNG_BYTES), "image/png"),
    }
    create_res = client.post("/api/issues/with-image", data=form_data, files=file_payload)
    assert create_res.status_code == 201
    issue_id = create_res.json()["id"]
    image_path = create_res.json()["image_path"]

    # 2. Retrieve issue by ID and check image fields
    get_res = client.get(f"/api/issues/{issue_id}")
    assert get_res.status_code == 200
    issue_data = get_res.json()
    assert issue_data["image_path"] == image_path
    assert issue_data["image"] == image_path

    # 3. Retrieve image file safely via dedicated endpoint
    stream_res = client.get(f"/api/issues/{issue_id}/image")
    assert stream_res.status_code == 200
    assert len(stream_res.content) == len(SAMPLE_PNG_BYTES)


# ==========================================================
# Prompt 3: Core API Tests
# ==========================================================

def test_successful_issue_creation():
    """Test successful issue creation via POST /api/issues."""
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
    assert data["status"] == "REPORTED"
    assert data["priority"] == "MEDIUM"

    assert "updates" in data
    assert len(data["updates"]) >= 1
    assert data["updates"][0]["status"] == "REPORTED"


def test_invalid_issue_data_missing_fields():
    """Test validation errors when required fields are missing."""
    payload = {"title": "Missing details"}
    response = client.post("/api/issues", json=payload)
    assert response.status_code == 422


def test_invalid_issue_data_out_of_range_coordinates():
    """Test validation fails when latitude or longitude are out of range."""
    payload_bad_lat = {
        "title": "Invalid Latitude Issue",
        "description": "Testing invalid latitude value",
        "latitude": 120.0,
        "longitude": -122.4194,
    }
    res_lat = client.post("/api/issues", json=payload_bad_lat)
    assert res_lat.status_code == 422


def test_retrieving_issues_list():
    """Test GET /api/issues returns clean list with coordinates."""
    response = client.get("/api/issues")
    assert response.status_code == 200
    issues = response.json()
    assert isinstance(issues, list)
    assert len(issues) >= 1

    first_issue = issues[0]
    assert "id" in first_issue
    assert "latitude" in first_issue
    assert "longitude" in first_issue
    assert "status" in first_issue


def test_retrieving_single_issue_with_status_history():
    """Test GET /api/issues/{issue_id} returns details and status history."""
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

    get_res = client.get(f"/api/issues/{issue_id}")
    assert get_res.status_code == 200
    fetched = get_res.json()

    assert fetched["id"] == issue_id
    assert fetched["status"] == "REPORTED"
    assert len(fetched["updates"]) >= 1


def test_issue_not_found():
    """Test retrieving non-existent issue returns HTTP 404."""
    response = client.get("/api/issues/999999")
    assert response.status_code == 404
