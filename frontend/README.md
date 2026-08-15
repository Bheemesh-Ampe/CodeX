# CIVICFIX — Frontend Application

A clean, beginner-friendly web frontend for **CIVICFIX** — an intelligent civic issue reporting and municipal resolution platform.

Built using pure **HTML5, CSS3, and Vanilla JavaScript** with no complex frameworks.

---

## 📁 Directory Structure

```
frontend/
│
├── index.html              # Resident Homepage & Portal Overview
├── report.html             # Resident Issue Reporting Flow (Photo, Location, AI)
├── issues.html             # Public Community Issues List
├── issue-details.html      # Individual Issue Detail & Timeline View
│
├── admin/                  # Municipal Administrator Portal
│   ├── dashboard.html      # Aggregated Analytics & KPI Metrics
│   ├── issues.html         # Administrator Issue Data Table & Filters
│   ├── issue-details.html  # Status Transition & Progress Comments
│   └── map.html            # City-wide Geographic Cluster Map
│
├── css/
│   ├── style.css           # Common design tokens, layout, header, and buttons
│   ├── resident.css        # Resident forms, previews, and banner styling
│   └── admin.css           # Admin dark theme, metrics cards, and tables
│
├── js/
│   ├── api.js              # Centralized REST API communication client
│   ├── main.js             # Global navigation controller & active states
│   ├── report.js           # Issue reporting form handler
│   ├── issues.js           # Public issue list renderer
│   ├── issue-details.js    # Single issue details & history handler
│   ├── admin-dashboard.js  # Dashboard metric cards & charts loader
│   ├── admin-issues.js     # Admin issue table & filter handler
│   ├── admin-issue-details.js # Admin status update & action handler
│   └── admin-map.js        # Leaflet map pins & clustering handler
│
├── data/
│   └── mock-data.js        # Safe offline sample data matching backend schemas
│
├── assets/
│   └── images/             # Static icons, logos, and sample issue photos
│
├── docs/
│   └── API_CONTRACT.md     # FastAPI REST API contract and endpoint docs
│
└── README.md               # Frontend guide and documentation
```

---

## 🚀 How to Run the Frontend

1. **Direct File Open**:
   Open `frontend/index.html` directly in any standard modern web browser (Chrome, Edge, Firefox, Safari).

2. **Using Python Local HTTP Server**:
   ```bash
   cd frontend
   python -m http.server 3000
   ```
   Open `http://localhost:3000` in your browser.

3. **Using VS Code Live Server**:
   Right click on `index.html` → **"Open with Live Server"**.

---

## 🔗 Route Map & Navigation

* **Resident Portal**:
  * [index.html](file:///d:/Hackthon/CodeX/frontend/index.html) → Home
  * [report.html](file:///d:/Hackthon/CodeX/frontend/report.html) → Report a Civic Issue
  * [issues.html](file:///d:/Hackthon/CodeX/frontend/issues.html) → Browse Public Issues
  * [issue-details.html](file:///d:/Hackthon/CodeX/frontend/issue-details.html) → Issue Details View
* **Administrator Portal**:
  * [admin/dashboard.html](file:///d:/Hackthon/CodeX/frontend/admin/dashboard.html) → Admin Overview Dashboard
  * [admin/issues.html](file:///d:/Hackthon/CodeX/frontend/admin/issues.html) → Manage Community Issues
  * [admin/issue-details.html](file:///d:/Hackthon/CodeX/frontend/admin/issue-details.html) → Admin Action Panel
  * [admin/map.html](file:///d:/Hackthon/CodeX/frontend/admin/map.html) → Geographic Distribution Map
