/**
 * ==============================================================================
 * CIVICFIX Admin — Dashboard Controller (js/admin-dashboard.js)
 * ==============================================================================
 * Loads aggregated municipal metrics and renders recent civic reports.
 */

document.addEventListener('DOMContentLoaded', async () => {
  await Promise.all([
    loadAdminStats(),
    loadRecentIssues()
  ]);
});

async function loadAdminStats() {
  const totalEl = document.getElementById('stat-total');
  const openEl = document.getElementById('stat-open');
  const highEl = document.getElementById('stat-high');
  const resolvedEl = document.getElementById('stat-resolved');

  try {
    const stats = await window.api.getDashboardStats();

    const total = stats.total_issues || 0;
    const open = (stats.by_status.REPORTED || 0) +
                 (stats.by_status.IN_REVIEW || 0) +
                 (stats.by_status.ASSIGNED || 0) +
                 (stats.by_status.IN_PROGRESS || 0);
    const high = (stats.by_priority.HIGH || 0) + (stats.by_priority.CRITICAL || 0);
    const resolved = stats.by_status.RESOLVED || 0;

    if (totalEl) totalEl.textContent = total;
    if (openEl) openEl.textContent = open;
    if (highEl) highEl.textContent = high;
    if (resolvedEl) resolvedEl.textContent = resolved;
  } catch (error) {
    console.error('Error fetching admin dashboard stats:', error);
    if (totalEl) totalEl.textContent = '0';
    if (openEl) openEl.textContent = '0';
    if (highEl) highEl.textContent = '0';
    if (resolvedEl) resolvedEl.textContent = '0';
  }
}

async function loadRecentIssues() {
  const tbody = document.getElementById('recent-issues-tbody');
  if (!tbody) return;

  try {
    const issues = await window.api.getIssues();

    if (!issues || issues.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8" style="text-align: center; padding: var(--space-6); color: var(--color-text-muted);">
            No issues found in the registry.
          </td>
        </tr>
      `;
      return;
    }

    const recent = issues.slice(0, 5);

    tbody.innerHTML = recent.map((issue) => {
      const formattedId = `CF-${1000 + Number(issue.id)}`;
      const formattedDate = new Date(issue.created_at).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric'
      });
      const locationText = issue.address || `Lat ${parseFloat(issue.latitude).toFixed(2)}, Lng ${parseFloat(issue.longitude).toFixed(2)}`;

      return `
        <tr>
          <td>
            <strong style="color: var(--color-primary);">${formattedId}</strong>
          </td>
          <td>
            <div style="font-weight: 700; color: var(--color-text-main);">${escapeHtml(issue.title)}</div>
          </td>
          <td>${escapeHtml(issue.category)}</td>
          <td>
            <span class="priority-badge ${getPriorityBadgeClass(issue.priority)}">
              ${issue.priority}
            </span>
          </td>
          <td>
            <span class="status-badge ${getStatusBadgeClass(issue.status)}">
              ${formatStatus(issue.status)}
            </span>
          </td>
          <td style="max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
            ${escapeHtml(locationText)}
          </td>
          <td>${formattedDate}</td>
          <td>
            <a href="issue-details.html?id=${issue.id}" class="button secondary-button button-sm">
              🔍 Inspect
            </a>
          </td>
        </tr>
      `;
    }).join('');
  } catch (error) {
    console.error('Error loading recent issues table:', error);
    tbody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align: center; padding: var(--space-6); color: var(--color-danger);">
          ⚠️ Failed to load recent issues: ${error.message}
        </td>
      </tr>
    `;
  }
}

function formatStatus(status) {
  return (status || '').replace('_', ' ');
}

function getStatusBadgeClass(status) {
  switch ((status || '').toUpperCase()) {
    case 'REPORTED': return 'status-reported';
    case 'IN_REVIEW': return 'status-in-review';
    case 'ASSIGNED': return 'status-in-review';
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
