/**
 * ==============================================================================
 * CIVICFIX — Safe Sample / Mock Data Store (data/mock-data.js)
 * ==============================================================================
 * Standardized database mock models matching FastAPI SQLAlchemy schema.
 * Persists to localStorage to retain submitted reports across page navigations.
 */

// Initial Seed Users (Resident & Admin)
const MOCK_USERS = [
  {
    id: 1,
    name: "Aarav Sharma",
    email: "aarav.resident@civicfix.org",
    role: "resident",
    created_at: "2026-08-01T09:00:00Z"
  },
  {
    id: 2,
    name: "Priya Patel",
    email: "priya.resident@civicfix.org",
    role: "resident",
    created_at: "2026-08-02T10:30:00Z"
  },
  {
    id: 3,
    name: "Admin Officer Rajesh",
    email: "rajesh.admin@civicfix.org",
    role: "admin",
    created_at: "2026-07-15T08:00:00Z"
  }
];

// Initial Seed Issues
const INITIAL_MOCK_ISSUES = [
  {
    id: 1,
    title: "Hazardous Deep Pothole on MG Road",
    description: "Large 8-inch deep crater in the right lane near City Mall. Two two-wheelers skidded this morning.",
    category: "Pothole",
    status: "IN_PROGRESS",
    priority: "HIGH",
    latitude: 12.9716,
    longitude: 77.5946,
    address: "MG Road, Opposite Metro Station Gate 2, Bengaluru",
    image_path: "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?auto=format&fit=crop&w=600&q=80",
    ai_summary: "High-risk roadway crater creating acute traffic congestion and accident hazard for two-wheelers.",
    ai_category: "Road Damage",
    ai_priority: "HIGH",
    ai_suggested_action: "Deploy asphalt patch team with emergency road cones within 12 hours.",
    created_by: 1,
    assigned_to: 3,
    created_at: "2026-08-14T08:15:00Z",
    updated_at: "2026-08-14T11:30:00Z"
  },
  {
    id: 2,
    title: "Broken Streetlight at 5th Main Cross",
    description: "Light pole #42 has been flickering and completely off for the last 3 days. Area is completely dark at night.",
    category: "Streetlight",
    status: "REPORTED",
    priority: "MEDIUM",
    latitude: 12.9750,
    longitude: 77.6010,
    address: "5th Main Cross, Indiranagar, Bengaluru",
    image_path: "https://images.unsplash.com/photo-1508873696983-2df5293cb32f?auto=format&fit=crop&w=600&q=80",
    ai_summary: "Electrical fixture outage reducing nighttime pedestrian safety on residential crossroad.",
    ai_category: "Streetlight",
    ai_priority: "MEDIUM",
    ai_suggested_action: "Schedule line inspector to check wiring and replace LED luminaire module.",
    created_by: 2,
    assigned_to: null,
    created_at: "2026-08-15T06:45:00Z",
    updated_at: "2026-08-15T06:45:00Z"
  },
  {
    id: 3,
    title: "Burst Water Pipeline Flooding Footpath",
    description: "Drinking water pipe connection leaking heavily, creating a pool of clean water across the sidewalk.",
    category: "Water Leakage",
    status: "RESOLVED",
    priority: "HIGH",
    latitude: 12.9690,
    longitude: 77.5890,
    address: "12th Cross, Shanti Nagar, Bengaluru",
    image_path: "https://images.unsplash.com/photo-1541888946425-d0fbb18086f6?auto=format&fit=crop&w=600&q=80",
    ai_summary: "Municipal supply line rupture causing potable water wastage and sidewalk erosion.",
    ai_category: "Water Leakage",
    ai_priority: "HIGH",
    ai_suggested_action: "Shut off sector valve and replace damaged pipe coupling immediately.",
    created_by: 1,
    assigned_to: 3,
    created_at: "2026-08-13T14:20:00Z",
    updated_at: "2026-08-14T09:00:00Z"
  },
  {
    id: 4,
    title: "Uncollected Overflowing Garbage Dump",
    description: "Public bin on 3rd Avenue has been overflowing for 4 days, blocking the pedestrian walkway and attracting strays.",
    category: "Garbage",
    status: "REPORTED",
    priority: "MEDIUM",
    latitude: 12.9780,
    longitude: 77.5990,
    address: "3rd Avenue, Near Community Park, Bengaluru",
    image_path: null,
    ai_summary: "Solid waste accumulation posing sanitation risks and pedestrian obstruction.",
    ai_category: "Garbage",
    ai_priority: "MEDIUM",
    ai_suggested_action: "Dispatch municipal waste collection compactor truck and sanitize container bay.",
    created_by: 2,
    assigned_to: null,
    created_at: "2026-08-15T09:00:00Z",
    updated_at: "2026-08-15T09:00:00Z"
  }
];

// Initial Seed Issue Updates (Audit trail)
const INITIAL_MOCK_UPDATES = [
  {
    id: 1,
    issue_id: 1,
    status: "REPORTED",
    comment: "Citizen submitted report with geotagged photo.",
    updated_by: 1,
    created_at: "2026-08-14T08:15:00Z"
  },
  {
    id: 2,
    issue_id: 1,
    status: "IN_PROGRESS",
    comment: "Road maintenance crew dispatched to site for quick cold-mix asphalt patch.",
    updated_by: 3,
    created_at: "2026-08-14T11:30:00Z"
  },
  {
    id: 3,
    issue_id: 2,
    status: "REPORTED",
    comment: "Resident registered issue.",
    updated_by: 2,
    created_at: "2026-08-15T06:45:00Z"
  },
  {
    id: 4,
    issue_id: 3,
    status: "REPORTED",
    comment: "Resident report submitted.",
    updated_by: 1,
    created_at: "2026-08-13T14:20:00Z"
  },
  {
    id: 5,
    issue_id: 3,
    status: "IN_PROGRESS",
    comment: "Water board team deployed valve isolation.",
    updated_by: 3,
    created_at: "2026-08-13T16:00:00Z"
  },
  {
    id: 6,
    issue_id: 3,
    status: "RESOLVED",
    comment: "Pipe joint sealed and pressure tested. Footpath cleared.",
    updated_by: 3,
    created_at: "2026-08-14T09:00:00Z"
  },
  {
    id: 7,
    issue_id: 4,
    status: "REPORTED",
    comment: "Resident filed sanitation report.",
    updated_by: 2,
    created_at: "2026-08-15T09:00:00Z"
  }
];

// Persistent storage using localStorage with fallback
function loadStoredIssues() {
  try {
    const raw = localStorage.getItem('civicfix_issues');
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    }
  } catch (e) {
    console.warn('Could not read from localStorage:', e);
  }
  return JSON.parse(JSON.stringify(INITIAL_MOCK_ISSUES));
}

function loadStoredUpdates() {
  try {
    const raw = localStorage.getItem('civicfix_updates');
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    }
  } catch (e) {
    console.warn('Could not read from localStorage:', e);
  }
  return JSON.parse(JSON.stringify(INITIAL_MOCK_UPDATES));
}

// In-Memory & LocalStorage mutable storage
let mockIssuesStore = loadStoredIssues();
let mockUpdatesStore = loadStoredUpdates();

// Global export for mock-api layer
window.MOCK_USERS = MOCK_USERS;
window.mockIssuesStore = mockIssuesStore;
window.mockUpdatesStore = mockUpdatesStore;

window.saveMockStore = function() {
  try {
    localStorage.setItem('civicfix_issues', JSON.stringify(window.mockIssuesStore));
    localStorage.setItem('civicfix_updates', JSON.stringify(window.mockUpdatesStore));
  } catch (e) {
    console.warn('Could not save to localStorage:', e);
  }
};
