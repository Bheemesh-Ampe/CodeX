/**
 * ==============================================================================
 * CIVICFIX Admin — Issues Management Controller (js/admin-issues.js)
 * ==============================================================================
 * Manages the municipal issue table, search indexing, and multi-field filters.
 */

let allAdminIssues = [];

document.addEventListener('DOMContentLoaded', async () => {
  await fetchAndRenderAdminIssues();
  initFilterListeners();
});

async function fetchAndRenderAdminIssues() {
  const tbody = document.getElementById('admin-issues-tbody');
  const countBadge = document.getElementById('filtered-count-badge');

  try {
    allAdminIssues = await window.api.getIssues();
    applyFiltersAndRender();
  } catch (error) {
    console.error('Error fetching admin issues:', error);
    if (tbody) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8" style="text-align: center; padding: var(--space-8); color: var(--color-danger);">
            ⚠️ Unable to load municipal issue registry: ${error.message}
          </td>
        </tr>
      `;
    }
    if (countBadge) countBadge.textContent = 'Error';
  }
}

function initFilterListeners() {
  const searchInput = document.getElementById('filter-search');
  const statusSelect = document.getElementById('filter-status');
  const prioritySelect = document.getElementById('filter-priority');
  const categorySelect = document.getElementById('filter-category');
  const btnReset = document.getElementById('btn-reset-filters');

  if (searchInput) searchInput.addEventListener('input', applyFiltersAndRender);
  if (statusSelect) statusSelect.addEventListener('change', applyFiltersAndRender);
  if (prioritySelect) prioritySelect.addEventListener('change', applyFiltersAndRender);
  if (categorySelect) categorySelect.addEventListener('change', applyFiltersAndRender);

  if (btnReset) {
    btnReset.addEventListener('click', () => {
      if (searchInput) searchInput.value = '';
      if (statusSelect) statusSelect.value = '';
      if (prioritySelect) prioritySelect.value = '';
      if (categorySelect) categorySelect.value = '';
      applyFiltersAndRender();
    });
  }
}

function applyFiltersAndRender() {
  const tbody = document.getElementById('admin-issues-tbody');
  const countBadge = document.getElementById('filtered-count-badge');
  if (!tbody) return;

  const searchQuery = (document.getElementById('filter-search')?.value || '').trim().toLowerCase();
  const statusFilter = document.getElementById('filter-status')?.value || '';
  const priorityFilter = document.getElementById('filter-priority')?.value || '';
  const categoryFilter = document.getElementById('filter-category')?.value || '';

  let filtered = [...allAdminIssues];

  // Search filter
  if (searchQuery) {
    filtered = filtered.filter((i) =>
      (i.title && i.title.toLowerCase().includes(searchQuery)) ||
      (i.description && i.description.toLowerCase().includes(searchQuery)) ||
      (i.address && i.address.toLowerCase().includes(searchQuery)) ||
      (`CF-${1000 + Number(i.id)}`.toLowerCase().includes(searchQuery)) ||
      (`issue #${i.id}`.toLowerCase().includes(searchQuery))
    );
  }

  // Status filter
  if (statusFilter) {
    filtered = filtered.filter((i) => i.status === statusFilter);
  }

  // Priority filter
  if (priorityFilter) {
    filtered = filtered.filter((i) => i.priority === priorityFilter);
  }

  // Category filter
  if (categoryFilter) {
    filtered = filtered.filter((i) => i.category === categoryFilter);
  }

  if (countBadge) {
    countBadge.textContent = `${filtered.length} Issue${filtered.length === 1 ? '' : 's'}`;
  }

  if (filtered.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align: center; padding: var(--space-8); color: var(--color-text-muted);">
          No matching issues found matching the selected filters.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = filtered.map((issue) => {
    const formattedId = `CF-${1000 + Number(issue.id)}`;
    const formattedDate = new Date(issue.created_at).toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
    const locationText = issue.address || `Lat ${parseFloat(issue.latitude).toFixed(3)}, Lng ${parseFloat(issue.longitude).toFixed(3)}`;

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
        <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
          ${escapeHtml(locationText)}
        </td>
        <td>${formattedDate}</td>
        <td>
          <a href="issue-details.html?id=${issue.id}" class="button primary-button button-sm">
            View
          </a>
        </td>
      </tr>
    `;
  }).join('');
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
