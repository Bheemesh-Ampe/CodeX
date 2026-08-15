"""Comprehensive backend verification script for CivicFix."""

import io
from fastapi.testclient import TestClient
from app.main import app

def run_verification():
    client = TestClient(app)

    print("[1/8] Testing Health Endpoint...")
    r = client.get("/api/health")
    assert r.status_code == 200, f"Health failed: {r.status_code}"
    print(f"      Status: {r.json()['status']} | DB: {r.json()['database']}")

    print("[2/8] Testing Demo Data Seeding...")
    r = client.post("/api/issues/seed?force=true")
    assert r.status_code == 200
    print(f"      Seeded Count: {r.json()['count']}")

    print("[3/8] Testing Resident Issue Reporting (JSON)...")
    issue_payload = {
        "title": "Major Pothole on 5th Ave",
        "description": "Tire bursting pothole causing heavy traffic.",
        "category": "Road Damage",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "address": "500 5th Ave",
    }
    r = client.post("/api/issues", json=issue_payload)
    assert r.status_code == 201
    issue_id = r.json()["id"]
    print(f"      Created Issue ID: {issue_id} | Status: {r.json()['status']} | AI Status: {r.json()['ai_status']}")

    print("[4/8] Testing Multipart Issue Creation with Image Upload...")
    img_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    form_data = {
        "title": "Broken Streetlamp with Photo",
        "description": "Streetlamp went dark outside apartment complex.",
        "latitude": "37.7812",
        "longitude": "-122.4130",
        "category": "Street Light",
    }
    files = {"image": ("lamp.png", io.BytesIO(img_bytes), "image/png")}
    r = client.post("/api/issues/with-image", data=form_data, files=files)
    assert r.status_code == 201
    img_issue_id = r.json()["id"]
    img_path = r.json()["image_path"]
    print(f"      Uploaded Issue ID: {img_issue_id} | Image Path: {img_path}")

    print("[5/8] Testing Safe Image Streaming...")
    r = client.get(f"/api/issues/{img_issue_id}/image")
    assert r.status_code == 200
    print(f"      Image streamed bytes: {len(r.content)}")

    print("[6/8] Testing Administrator Review & Action...")
    r = client.patch(f"/api/admin/issues/{img_issue_id}/status", json={
        "status": "IN_PROGRESS",
        "priority": "HIGH",
        "comment": "Maintenance electrician assigned to replace ballast.",
    })
    assert r.status_code == 200
    assert r.json()["status"] == "IN_PROGRESS"
    print(f"      Transitioned Status to: {r.json()['status']} | Updates Count: {len(r.json()['updates'])}")

    print("[7/8] Testing Admin Issue List & Filtering...")
    r = client.get("/api/admin/issues?status=IN_PROGRESS")
    assert r.status_code == 200
    print(f"      Found IN_PROGRESS issues: {len(r.json())}")

    print("[8/8] Testing OpenAPI & Swagger Docs...")
    r = client.get("/api/openapi.json")
    assert r.status_code == 200
    print(f"      OpenAPI routes registered: {len(r.json()['paths'])}")

    print("\n======================================================")
    print("   ALL BACKEND VERIFICATION CHECKS PASSED (100% OK)")
    print("======================================================")

if __name__ == "__main__":
    run_verification()
