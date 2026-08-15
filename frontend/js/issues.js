/**
 * ==============================================================================
 * CIVICFIX — Resident My Issues Controller (js/issues.js)
 * ==============================================================================
 * Dynamically loads and renders resident reported civic issues from the API layer.
 * Manages loading, empty, and error fallback states.
 */

document.addEventListener('DOMContentLoaded', () => {
  loadResidentIssues();

  const btnRetry = document.getElementById('btn-retry-issues');
  if (btnRetry) {
    btnRetry.addEventListener('click', () => {
      loadResidentIssues();
    });
  }
});

async function loadResidentIssues() {
  const loadingEl = document.getElementById('issues-loading');
  const errorEl = document.getElementById('issues-error');
  const emptyEl = document.getElementById('issues-empty');
  const gridEl = document.getElementById('issues-grid');
  const errorMessageEl = document.getElementById('error-message-text');

  // Set Loading State
  if (loadingEl) loadingEl.style.display = 'flex';
  if (errorEl) errorEl.style.display = 'none';
  if (emptyEl) emptyEl.style.display = 'none';
  if (gridEl) gridEl.style.display = 'none';

  try {
    const issues = await window.api.getIssues();

    if (loadingEl) loadingEl.style.display = 'none';

    if (!issues || issues.length === 0) {
      if (emptyEl) emptyEl.style.display = 'block';
      return;
    }

    // Render Cards in Grid
    if (gridEl) {
      gridEl.innerHTML = issues.map((issue) => renderIssueCard(issue)).join('');
      gridEl.style.display = 'grid';
    }
  } catch (error) {
    console.error('Error loading resident issues:', error);
    if (loadingEl) loadingEl.style.display = 'none';
    if (errorEl) errorEl.style.display = 'flex';
    if (errorMessageEl) {
      errorMessageEl.textContent = `Unable to load issues: ${error.message || 'Network error'}`;
    }
  }
}

function renderIssueCard(issue) {
  const formattedId = `CF-${1000 + Number(issue.id)}`;
  const statusBadgeClass = getStatusBadgeClass(issue.status);
  const priorityBadgeClass = getPriorityBadgeClass(issue.priority);
  const formattedDate = new Date(issue.created_at).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });

  const locationText = issue.address 
    ? escapeHtml(issue.address)
    : `Lat: ${parseFloat(issue.latitude).toFixed(4)}, Lng: ${parseFloat(issue.longitude).toFixed(4)}`;

  const aiSnippet = issue.ai_summary
    ? `
      <div class="ai-triage-card" style="margin-top: var(--space-3); padding: var(--space-2) var(--space-3);">
        <div class="ai-triage-header" style="font-size: var(--font-size-xs);">
          <span>🤖</span> AI Triage
        </div>
        <p style="font-size: 0.75rem; color: #166534; margin: 0; line-height: 1.4;">
          ${escapeHtml(issue.ai_summary)}
        </p>
      </div>
    `
    : '';

  return `
    <div class="card" style="display: flex; flex-direction: column; justify-content: space-between;">
      <div>
        <div class="card-header flex-between" style="padding-bottom: var(--space-2); border-bottom: 1px solid var(--color-border-subtle);">
          <div style="display: flex; align-items: center; gap: var(--space-2);">
            <span style="font-size: var(--font-size-xs); font-weight: 800; color: var(--color-primary); background: var(--color-primary-subtle); padding: 2px 6px; border-radius: var(--radius-sm);">
              ${formattedId}
            </span>
            <span style="font-size: var(--font-size-xs); color: var(--color-text-muted);">
              ${escapeHtml(issue.category)}
            </span>
          </div>
          <div style="display: flex; gap: var(--space-2);">
            <span class="status-badge ${statusBadgeClass}">
              ${formatStatus(issue.status)}
            </span>
            <span class="priority-badge ${priorityBadgeClass}">
              ${issue.priority}
            </span>
          </div>
        </div>

        <div class="card-body" style="padding-top: var(--space-3);">
          <h2 class="card-title" style="font-size: var(--font-size-base); margin-bottom: var(--space-2);">
            ${escapeHtml(issue.title)}
          </h2>

          <p style="font-size: var(--font-size-xs); color: var(--color-text-muted); display: flex; align-items: center; gap: var(--space-1); margin-bottom: var(--space-2);">
            <span>📍</span> <strong>Location:</strong> <span style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${locationText}</span>
          </p>

          ${aiSnippet}
        </div>
      </div>

      <div class="card-footer flex-between" style="border-top: 1px solid var(--color-border-subtle); padding: var(--space-3) var(--space-4); background-color: #fafafa;">
        <span style="font-size: var(--font-size-xs); color: var(--color-text-muted);">
          📅 Reported ${formattedDate}
        </span>
        <a href="issue-details.html?id=${issue.id}" class="button secondary-button button-sm">
          🔍 View Details
        </a>
      </div>
    </div>
  `;
}

function formatStatus(status) {
  return (status || '').replace('_', ' ');
}

function getStatusBadgeClass(status) {
  switch ((status || '').toUpperCase()) {
    case 'REPORTED': return 'status-reported';
    case 'IN_REVIEW': return 'status-in-review';
    case 'IN_PROGRESS': return 'status-in-progress';
    case 'RESOLVED': return 'status-resolved';
    case 'REJECTED': return 'status-rejected';
    default: return 'status-reported';
  }
}

function getPriorityBadgeClass(priority) {
  switch ((priority || '').toUpperCase()) {
    case 'CRITICAL':
    case 'HIGH': return 'priority-high';
    case 'MEDIUM': return 'priority-medium';
    case 'LOW': return 'priority-low';
    default: return 'priority-medium';
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
