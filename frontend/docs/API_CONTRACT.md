# CIVICFIX — Backend-Aligned REST API Contract

This document outlines the API contract between the CIVICFIX frontend (`js/api.js`) and the FastAPI backend.

Base URL: `http://localhost:8000/api`

---

## 1. Issue Object Model Schema

```json
{
  "id": 1,
  "title": "Hazardous Deep Pothole on MG Road",
  "description": "Large 8-inch deep crater in the right lane near City Mall.",
  "category": "Pothole",
  "status": "REPORTED",
  "priority": "MEDIUM",
  "latitude": 12.9716,
  "longitude": 77.5946,
  "address": "MG Road, Opposite Metro Station Gate 2, Bengaluru",
  "image_path": "https://example.com/pothole.jpg",
  "ai_summary": "High-risk roadway crater creating traffic hazard.",
  "ai_category": "Road Damage",
  "ai_priority": "HIGH",
  "ai_suggested_action": "Deploy asphalt patch team within 12 hours.",
  "created_by": 1,
  "assigned_to": null,
  "created_at": "2026-08-15T08:00:00Z",
  "updated_at": "2026-08-15T08:00:00Z"
}
```

### Defaults:
* `status`: `"REPORTED"` (Enum: `"REPORTED"`, `"IN_REVIEW"`, `"IN_PROGRESS"`, `"RESOLVED"`, `"REJECTED"`)
* `priority`: `"MEDIUM"` (Enum: `"LOW"`, `"MEDIUM"`, `"HIGH"`, `"CRITICAL"`)

---

## 2. IssueUpdate (Audit Trail) Schema

```json
{
  "id": 1,
  "issue_id": 1,
  "status": "REPORTED",
  "comment": "Citizen submitted report with geotagged photo.",
  "updated_by": 1,
  "created_at": "2026-08-15T08:00:00Z"
}
```

---

## 3. Endpoints Specification

### 3.1 `GET /api/issues`
Retrieve list of civic issues with optional query filters.

* **Query Parameters**:
  * `status` (string, optional)
  * `category` (string, optional)
  * `priority` (string, optional)
  * `search` (string, optional)
  * `created_by` (integer, optional)
* **Frontend Method**: `api.getIssues(filters)`
* **Response `200 OK`**:
  ```json
  [
    {
      "id": 1,
      "title": "Hazardous Deep Pothole on MG Road",
      "category": "Pothole",
      "status": "REPORTED",
      "priority": "HIGH",
      "latitude": 12.9716,
      "longitude": 77.5946,
      "created_at": "2026-08-15T08:00:00Z"
    }
  ]
  ```

---

### 3.2 `GET /api/issues/{id}`
Fetch full single issue record including its complete audit trail updates.

* **Path Parameter**: `id` (integer)
* **Frontend Method**: `api.getIssueById(id)`
* **Response `200 OK`**:
  ```json
  {
    "id": 1,
    "title": "Hazardous Deep Pothole on MG Road",
    "description": "Large crater damaging vehicles.",
    "category": "Pothole",
    "status": "IN_PROGRESS",
    "priority": "HIGH",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "address": "MG Road, Bengaluru",
    "image_path": "https://example.com/pothole.jpg",
    "ai_summary": "High-risk roadway crater creating traffic hazard.",
    "ai_category": "Road Damage",
    "ai_priority": "HIGH",
    "ai_suggested_action": "Deploy asphalt patch team within 12 hours.",
    "created_by": 1,
    "assigned_to": 3,
    "created_at": "2026-08-14T08:15:00Z",
    "updated_at": "2026-08-14T11:30:00Z",
    "updates": [
      {
        "id": 1,
        "issue_id": 1,
        "status": "REPORTED",
        "comment": "Citizen submitted report.",
        "updated_by": 1,
        "created_at": "2026-08-14T08:15:00Z"
      },
      {
        "id": 2,
        "issue_id": 1,
        "status": "IN_PROGRESS",
        "comment": "Maintenance crew dispatched.",
        "updated_by": 3,
        "created_at": "2026-08-14T11:30:00Z"
      }
    ]
  }
  ```

---

### 3.3 `POST /api/issues`
Resident submits a new civic issue report.

* **Frontend Method**: `api.createIssue(issueData)`
* **Request Body (`IssueCreate`)**:
  ```json
  {
    "title": "Hazardous Deep Pothole on MG Road",
    "description": "Deep crater damaging vehicles near crosswalk.",
    "category": "Pothole",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "address": "MG Road, Bengaluru",
    "image_path": "data:image/jpeg;base64,...",
    "priority": "MEDIUM",
    "created_by": 1
  }
  ```
* **Response `201 Created`**: Returns created `Issue` object.

---

### 3.4 `PATCH /api/issues/{id}/status`
Administrator updates the status/priority of an issue and appends an `IssueUpdate` audit entry.

* **Path Parameter**: `id` (integer)
* **Frontend Method**: `api.updateIssueStatus(id, status, comment, updated_by)`
* **Request Body**:
  ```json
  {
    "status": "IN_PROGRESS",
    "priority": "HIGH",
    "comment": "Road repair crew dispatched to site with cold mix asphalt.",
    "updated_by": 3
  }
  ```
* **Response `200 OK`**: Returns updated `Issue` object.

---

### 3.5 `POST /api/ai/analyze`
Generative AI analysis on incoming issue reports.

* **Frontend Method**: `api.analyzeIssue(issue)`
* **Request Body**:
  ```json
  {
    "title": "Deep road crater",
    "description": "8-inch hole damaging vehicle tires",
    "category": "Pothole",
    "image_path": null
  }
  ```
* **Response `200 OK`**:
  ```json
  {
    "ai_summary": "Roadway surface crater creating potential traffic hazard and vehicular damage.",
    "ai_category": "Roads & Potholes",
    "ai_priority": "HIGH",
    "ai_suggested_action": "Deploy road maintenance asphalt patch crew with safety cones within 24 hours."
  }
  ```

---

### 3.6 `GET /api/admin/stats` (or `GET /api/issues/stats/summary`)
Aggregated statistics for the Municipal Administrator dashboard.

* **Frontend Method**: `api.getDashboardStats()`
* **Response `200 OK`**:
  ```json
  {
    "total_issues": 12,
    "by_status": {
      "REPORTED": 5,
      "IN_REVIEW": 2,
      "IN_PROGRESS": 3,
      "RESOLVED": 2,
      "REJECTED": 0
    },
    "by_category": {
      "Pothole": 6,
      "Streetlight": 4,
      "Water Leakage": 2
    },
    "by_priority": {
      "LOW": 2,
      "MEDIUM": 6,
      "HIGH": 3,
      "CRITICAL": 1
    }
  }
  ```
