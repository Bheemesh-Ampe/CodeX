/**
 * ==============================================================================
 * CIVICFIX — Live FastAPI Backend Connected API Client (js/api.js)
 * ==============================================================================
 * Connects the Vanilla JS frontend directly to the FastAPI REST backend:
 * Base URL: http://localhost:8000/api
 * 
 * Features:
 * - Direct HTTP Fetch to FastAPI backend endpoints.
 * - Automatic payload serialization and error handling.
 * - Unwraps paginated responses ({ total, items } -> items).
 * - Automatic resilient fallback to localStorage mock store if backend is offline.
 */

const API_BASE_URL = 'http://localhost:8000/api';

const api = {
  /**
   * Internal fetch wrapper communicating with FastAPI.
   */
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    const response = await fetch(url, config);

    if (response.status === 204) {
      return null;
    }

    const data = await response.json();

    if (!response.ok) {
      const errorMessage = data.detail || `HTTP Error ${response.status}`;
      throw new Error(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage));
    }

    return data;
  },

  /**
   * Health Check: Verifies live connection to FastAPI backend & SQLite DB.
   * GET /api/health
   */
  async checkHealth() {
    try {
      return await this.request('/health');
    } catch (error) {
      console.warn('FastAPI backend health check failed:', error.message);
      return { status: 'offline', error: error.message };
    }
  },

  /**
   * 1. Get List of Civic Issues (with optional filters).
   * GET /api/issues
   * 
   * @param {object} [filters={}] - { status, category, priority, search, created_by }
   * @returns {Promise<Array<object>>}
   */
  async getIssues(filters = {}) {
    try {
      const query = new URLSearchParams();
      if (filters.status) query.append('status', filters.status);
      if (filters.category) query.append('category', filters.category);
      if (filters.priority) query.append('priority', filters.priority);
      if (filters.search) query.append('search', filters.search);
      if (filters.created_by) query.append('created_by', filters.created_by);

      const qs = query.toString() ? `?${query.toString()}` : '';
      const response = await this.request(`/issues${qs}`);

      let list = [];
      // FastAPI returns { total: N, items: [...] } or array
      if (response && Array.isArray(response.items)) {
        list = response.items;
      } else if (Array.isArray(response)) {
        list = response;
      }

      // Sync fetched live issues to local fallback store
      if (list.length > 0 && window.mockIssuesStore) {
        list.forEach((item) => {
          const idx = window.mockIssuesStore.findIndex((m) => m.id === item.id);
          if (idx >= 0) {
            window.mockIssuesStore[idx] = { ...window.mockIssuesStore[idx], ...item };
          } else {
            window.mockIssuesStore.unshift(item);
          }
        });
        if (window.saveMockStore) window.saveMockStore();
      }

      return list;
    } catch (error) {
      console.warn('Connecting to live backend failed for getIssues, using local store fallback:', error.message);
      return this._mockGetIssues(filters);
    }
  },

  /**
   * 2. Get Single Issue by ID (with updates audit trail).
   * GET /api/issues/{id}
   * 
   * @param {number|string} id - Issue ID
   * @returns {Promise<object>}
   */
  async getIssueById(id) {
    const numericId = typeof id === 'string' && id.startsWith('CF-')
      ? parseInt(id.replace('CF-', '')) - 1000
      : parseInt(id);

    try {
      const issue = await this.request(`/issues/${numericId}`);
      if (issue && window.mockIssuesStore) {
        const idx = window.mockIssuesStore.findIndex((m) => m.id === issue.id);
        if (idx >= 0) window.mockIssuesStore[idx] = { ...window.mockIssuesStore[idx], ...issue };
        else window.mockIssuesStore.unshift(issue);
        if (window.saveMockStore) window.saveMockStore();
      }
      return issue;
    } catch (error) {
      console.warn(`Connecting to live backend failed for getIssueById(${numericId}), using local store:`, error.message);
      return this._mockGetIssueById(numericId);
    }
  },

  /**
   * 3. Submit a New Civic Issue (Resident).
   * POST /api/issues
   * 
   * @param {object} issueData - { title, description, category, latitude, longitude, address, image_path, priority, ai_summary, ai_category, ai_priority, ai_suggested_action, created_by }
   * @returns {Promise<object>}
   */
  async createIssue(issueData) {
    const payload = {
      title: (issueData.title || '').trim(),
      description: (issueData.description || '').trim(),
      category: issueData.category || "Other",
      latitude: parseFloat(issueData.latitude),
      longitude: parseFloat(issueData.longitude),
      address: issueData.address ? issueData.address.trim() : null,
      image_path: issueData.image_path || null,
      priority: issueData.priority || "MEDIUM",
      ai_summary: issueData.ai_summary || null,
      ai_category: issueData.ai_category || null,
      ai_priority: issueData.ai_priority || null,
      ai_suggested_action: issueData.ai_suggested_action || null,
      created_by: issueData.created_by || 1
    };

    try {
      const created = await this.request('/issues', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
      console.log('✅ Created issue in FastAPI backend:', created);
      // Also cache in local store for seamless UI persistence
      this._cacheIssue(created);
      return created;
    } catch (error) {
      console.warn('Connecting to live backend failed for createIssue, saving to local store:', error.message);
      return this._mockCreateIssue(payload);
    }
  },

  /**
   * 4. Update Issue Status & Add Audit Update (Admin).
   * PATCH /api/issues/{id}/status
   * 
   * @param {number|string} id - Issue ID
   * @param {string} status - New status ("REPORTED", "IN_REVIEW", "ASSIGNED", "IN_PROGRESS", "RESOLVED", "REJECTED")
   * @param {string} [comment=""] - Action note
   * @param {number} [updated_by=3] - Admin Officer ID
   * @returns {Promise<object>}
   */
  async updateIssueStatus(id, status, comment = "", updated_by = 3) {
    const numericId = typeof id === 'string' && id.startsWith('CF-')
      ? parseInt(id.replace('CF-', '')) - 1000
      : parseInt(id);

    const payload = {
      status: status,
      comment: comment || `Status transitioned to ${status}.`,
      updated_by: updated_by
    };

    try {
      const updated = await this.request(`/issues/${numericId}/status`, {
        method: 'PATCH',
        body: JSON.stringify(payload)
      });
      console.log('✅ Updated issue in FastAPI backend:', updated);
      this._cacheIssue(updated);
      return updated;
    } catch (error) {
      console.warn(`Connecting to live backend failed for updateIssueStatus(${numericId}), using local store:`, error.message);
      return this._mockUpdateIssueStatus(numericId, status, comment, updated_by);
    }
  },

  /**
   * 5. Get Aggregate Statistics for Administrator Dashboard.
   * GET /api/issues/stats/summary
   * 
   * @returns {Promise<object>}
   */
  async getDashboardStats() {
    try {
      const stats = await this.request('/issues/stats/summary');
      return stats;
    } catch (error) {
      console.warn('Connecting to live backend failed for getDashboardStats, computing from local store:', error.message);
      return this._mockGetDashboardStats();
    }
  },

  /**
   * 6. AI Triage Analysis.
   * POST /api/ai/analyze
   * 
   * @param {object} issue - { title, description, category, image_path }
   * @returns {Promise<object>}
   */
  async analyzeIssue(issue) {
    try {
      const result = await this.request('/ai/analyze', {
        method: 'POST',
        body: JSON.stringify({
          title: issue.title || "",
          description: issue.description || "",
          category: issue.category || null,
          image_path: issue.image_path || null
        })
      });
      return result;
    } catch (error) {
      console.warn('Connecting to backend AI endpoint failed, using local AI triage heuristic:', error.message);
      return this._mockAnalyzeIssue(issue);
    }
  },

  _cacheIssue(issue) {
    if (!window.mockIssuesStore) window.mockIssuesStore = [];
    const idx = window.mockIssuesStore.findIndex((i) => i.id === issue.id);
    if (idx >= 0) {
      window.mockIssuesStore[idx] = { ...window.mockIssuesStore[idx], ...issue };
    } else {
      window.mockIssuesStore.unshift(issue);
    }
    if (window.saveMockStore) window.saveMockStore();
  },

  // ============================================================================
  // Safe Offline / Fallback In-Memory & LocalStorage Handlers
  // ============================================================================
  _mockGetIssues(filters = {}) {
    let results = window.mockIssuesStore ? [...window.mockIssuesStore] : [];
    if (filters.status) results = results.filter((i) => i.status === filters.status);
    if (filters.category) results = results.filter((i) => i.category === filters.category);
    if (filters.priority) results = results.filter((i) => i.priority === filters.priority);
    if (filters.created_by) results = results.filter((i) => i.created_by === Number(filters.created_by));
    if (filters.search) {
      const q = filters.search.toLowerCase();
      results = results.filter((i) =>
        (i.title && i.title.toLowerCase().includes(q)) ||
        (i.description && i.description.toLowerCase().includes(q)) ||
        (i.address && i.address.toLowerCase().includes(q))
      );
    }
    return results.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  },

  _mockGetIssueById(id) {
    const issue = (window.mockIssuesStore || []).find((i) => i.id === id);
    if (!issue) throw new Error(`Issue #${id} not found.`);
    const updates = (window.mockUpdatesStore || [])
      .filter((u) => u.issue_id === id)
      .sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
    return { ...issue, updates: updates };
  },

  _mockCreateIssue(payload) {
    const now = new Date().toISOString();
    const newId = (window.mockIssuesStore && window.mockIssuesStore.length > 0)
      ? Math.max(...window.mockIssuesStore.map((i) => Number(i.id) || 0)) + 1
      : 1;

    const newIssue = {
      id: newId,
      status: "REPORTED",
      created_at: now,
      updated_at: now,
      ...payload
    };

    if (!window.mockIssuesStore) window.mockIssuesStore = [];
    window.mockIssuesStore.unshift(newIssue);

    if (!window.mockUpdatesStore) window.mockUpdatesStore = [];
    window.mockUpdatesStore.push({
      id: window.mockUpdatesStore.length + 1,
      issue_id: newId,
      status: "REPORTED",
      comment: "Citizen submitted civic report with geotagged location.",
      updated_by: newIssue.created_by,
      created_at: now
    });

    if (window.saveMockStore) window.saveMockStore();

    return { ...newIssue, updates: [window.mockUpdatesStore[window.mockUpdatesStore.length - 1]] };
  },

  _mockUpdateIssueStatus(id, status, comment, updated_by) {
    const issueIndex = (window.mockIssuesStore || []).findIndex((i) => i.id === id);
    if (issueIndex === -1) throw new Error(`Issue #${id} not found.`);

    const now = new Date().toISOString();
    window.mockIssuesStore[issueIndex].status = status;
    window.mockIssuesStore[issueIndex].updated_at = now;

    if (!window.mockUpdatesStore) window.mockUpdatesStore = [];
    window.mockUpdatesStore.push({
      id: window.mockUpdatesStore.length + 1,
      issue_id: id,
      status: status,
      comment: comment,
      updated_by: updated_by,
      created_at: now
    });

    if (window.saveMockStore) window.saveMockStore();

    return this._mockGetIssueById(id);
  },

  _mockGetDashboardStats() {
    const issues = window.mockIssuesStore || [];
    const total_issues = issues.length;
    const by_status = { REPORTED: 0, IN_REVIEW: 0, ASSIGNED: 0, IN_PROGRESS: 0, RESOLVED: 0, REJECTED: 0 };
    const by_category = {};
    const by_priority = { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 };

    issues.forEach((issue) => {
      by_status[issue.status] = (by_status[issue.status] || 0) + 1;
      const cat = issue.category || "Other";
      by_category[cat] = (by_category[cat] || 0) + 1;
      const prio = issue.priority || "MEDIUM";
      by_priority[prio] = (by_priority[prio] || 0) + 1;
    });

    return { total_issues, by_status, by_category, by_priority };
  },

  _mockAnalyzeIssue(issue) {
    const text = `${issue.title || ''} ${issue.description || ''}`.toLowerCase();
    let aiCategory = issue.category || "Other";
    let aiPriority = "MEDIUM";
    let aiSummary = "Civic complaint logged for municipal inspection.";
    let aiAction = "Assign field inspector for on-site assessment.";

    if (text.includes("pothole") || text.includes("crater") || text.includes("road")) {
      aiCategory = "Pothole";
      aiPriority = (text.includes("deep") || text.includes("hazard") || text.includes("skid") || text.includes("danger")) ? "HIGH" : "MEDIUM";
      aiSummary = "Roadway surface crater creating potential traffic hazard and vehicular damage.";
      aiAction = "Deploy road maintenance asphalt patch crew with safety cones within 24 hours.";
    } else if (text.includes("light") || text.includes("dark") || text.includes("lamp") || text.includes("electric")) {
      aiCategory = "Streetlight";
      aiPriority = "MEDIUM";
      aiSummary = "Streetlight fixture outage impairing nighttime visibility and pedestrian safety.";
      aiAction = "Dispatch electrical line technician to inspect wiring and replace LED module.";
    } else if (text.includes("water") || text.includes("leak") || text.includes("pipe")) {
      aiCategory = "Water Leakage";
      aiPriority = "HIGH";
      aiSummary = "Potable water supply line rupture causing sidewalk flooding and resource loss.";
      aiAction = "Isolate sector distribution valve and replace damaged pipe coupling.";
    } else if (text.includes("garbage") || text.includes("waste") || text.includes("trash")) {
      aiCategory = "Garbage";
      aiPriority = "MEDIUM";
      aiSummary = "Accumulation of uncollected solid waste obstructing public pedestrian walkway.";
      aiAction = "Dispatch municipal waste compactor truck and sanitize collection bay.";
    }

    return {
      ai_summary: aiSummary,
      ai_category: aiCategory,
      ai_priority: aiPriority,
      ai_suggested_action: aiAction
    };
  }
};

// Make globally available
window.api = api;
