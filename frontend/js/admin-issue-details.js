/**
 * ==============================================================================
 * CIVICFIX Admin — Issue Details & Action Controller (js/admin-issue-details.js)
 * ==============================================================================
 * Renders full issue details, photo, Leaflet map, AI analysis, and handles
 * administrative status transitions and audit log additions.
 */

let adminMapInstance = null;
let currentIssueId = 1;

document.addEventListener('DOMContentLoaded', async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const rawId = urlParams.get('id') || '1';
  const parsedId = rawId.startsWith('CF-') ? parseInt(rawId.replace('CF-', '')) - 1000 : parseInt(rawId);
  currentIssueId = isNaN(parsedId) ? 1 : parsedId;

  await loadAdminIssueDetails(currentIssueId);
  initAdminActionForm();
});

async function loadAdminIssueDetails(issueId) {
  try {
    const issue = await window.api.getIssueById(issueId);
    renderAdminIssue(issue);
  } catch (error) {
    console.error('Failed to load admin issue details:', error);
    const titleEl = document.getElementById('admin-issue-title');
    if (titleEl) titleEl.textContent = `Issue #${issueId} Not Found`;
  }
}

function renderAdminIssue(issue) {
  const formattedId = `CF-${1000 + Number(issue.id)}`;
  const formattedCreated = new Date(issue.created_at).toLocaleString();
  const formattedUpdated = new Date(issue.updated_at || issue.created_at).toLocaleString();

  // 1. Header Information
  const titleEl = document.getElementById('admin-issue-title');
  const subtitleEl = document.getElementById('admin-issue-subtitle');
  if (titleEl) titleEl.textContent = `⚙️ Action Panel: ${issue.title}`;
  if (subtitleEl) {
    subtitleEl.textContent = `Registry ${formattedId} • Logged on ${formattedCreated}`;
  }

  // 2. Header Badges
  const statusBadge = document.getElementById('admin-status-badge');
  const priorityBadge = document.getElementById('admin-priority-badge');
  const categoryBadge = document.getElementById('admin-category-badge');

  if (statusBadge) {
    statusBadge.textContent = formatStatus(issue.status);
    statusBadge.className = `status-badge ${getStatusBadgeClass(issue.status)}`;
  }

  if (priorityBadge) {
    priorityBadge.textContent = `${issue.priority} Priority`;
    priorityBadge.className = `priority-badge ${getPriorityBadgeClass(issue.priority)}`;
  }

  if (categoryBadge) {
    categoryBadge.textContent = `Category: ${issue.category}`;
  }

  // 3. Admin Action Form Pre-fill
  const statusSelect = document.getElementById('admin-action-status');
  if (statusSelect) {
    statusSelect.value = issue.status || 'REPORTED';
  }

  // 4. Issue Description & Meta
  const descEl = document.getElementById('admin-issue-desc');
  if (descEl) descEl.textContent = issue.description;

  const metaId = document.getElementById('meta-admin-id');
  const metaCat = document.getElementById('meta-admin-cat');
  const metaCreator = document.getElementById('meta-admin-creator');
  const metaAssigned = document.getElementById('meta-admin-assigned');
  const metaCreated = document.getElementById('meta-admin-created');
  const metaUpdated = document.getElementById('meta-admin-updated');

  if (metaId) metaId.textContent = formattedId;
  if (metaCat) metaCat.textContent = issue.category;
  if (metaCreator) metaCreator.textContent = `Resident #${issue.created_by || 1}`;
  if (metaAssigned) metaAssigned.textContent = issue.assigned_to ? `Admin Officer #${issue.assigned_to}` : 'Unassigned';
  if (metaCreated) metaCreated.textContent = formattedCreated;
  if (metaUpdated) metaUpdated.textContent = formattedUpdated;

  // 5. AI Generated Analysis
  const aiSummary = document.getElementById('admin-ai-summary');
  const aiCat = document.getElementById('admin-ai-category');
  const aiPrio = document.getElementById('admin-ai-priority');
  const aiAction = document.getElementById('admin-ai-action');

  if (aiSummary) aiSummary.textContent = issue.ai_summary ? `"${issue.ai_summary}"` : 'AI analysis pending.';
  if (aiCat) aiCat.textContent = issue.ai_category || issue.category || '--';
  if (aiPrio) aiPrio.textContent = issue.ai_priority ? `${issue.ai_priority} Priority` : (issue.priority || '--');
  if (aiAction) aiAction.textContent = issue.ai_suggested_action || 'Pending officer review.';

  // 6. Photo Evidence
  const photoImg = document.getElementById('admin-photo-img');
  const photoPlaceholder = document.getElementById('admin-photo-placeholder');
  const photoBadge = document.getElementById('admin-photo-badge');

  if (issue.image_path) {
    if (photoImg) {
      photoImg.src = issue.image_path;
      photoImg.style.display = 'block';
    }
    if (photoPlaceholder) photoPlaceholder.style.display = 'none';
    if (photoBadge) photoBadge.textContent = 'Evidence Attached';
  } else {
    if (photoImg) photoImg.style.display = 'none';
    if (photoPlaceholder) photoPlaceholder.style.display = 'block';
    if (photoBadge) photoBadge.textContent = 'No Photo';
  }

  // 7. Location & Map
  const addressText = document.getElementById('admin-address-text');
  const coordsBadge = document.getElementById('admin-coords-badge');

  if (addressText) {
    addressText.textContent = issue.address || `GPS Coordinates (${issue.latitude}, ${issue.longitude})`;
  }

  if (coordsBadge) {
    coordsBadge.textContent = `Lat: ${parseFloat(issue.latitude).toFixed(4)}, Lng: ${parseFloat(issue.longitude).toFixed(4)}`;
  }

  initAdminMap(issue.latitude, issue.longitude, issue.title);

  // 8. Resolution Timeline Updates
  renderAdminTimeline(issue.updates || []);
}

function initAdminActionForm() {
  const form = document.getElementById('admin-action-form');
  const alertBox = document.getElementById('admin-action-alert');
  const alertMsg = document.getElementById('admin-action-msg');
  const submitBtn = document.getElementById('btn-update-issue');

  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const statusVal = document.getElementById('admin-action-status')?.value;
    const commentVal = document.getElementById('admin-action-comment')?.value.trim();

    if (!statusVal) return;

    if (submitBtn) {
      submitBtn.textContent = '⏳ Saving Update...';
      submitBtn.disabled = true;
    }

    try {
      // Step 14: Call updateIssueStatus(id, status, comment, updated_by)
      const updatedIssue = await window.api.updateIssueStatus(
        currentIssueId,
        statusVal,
        commentVal || `Status updated to ${statusVal} by Municipal Administration.`,
        3 // Mock Admin ID: Admin Officer Rajesh
      );

      // Show success alert
      if (alertBox) {
        if (alertMsg) alertMsg.textContent = 'Issue updated successfully.';
        alertBox.style.display = 'flex';
        alertBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }

      // Clear comment box
      const commentInput = document.getElementById('admin-action-comment');
      if (commentInput) commentInput.value = '';

      // Re-render updated state
      renderAdminIssue(updatedIssue);
    } catch (error) {
      console.error('Error updating issue status:', error);
      alert(`Update failed: ${error.message}`);
    } finally {
      if (submitBtn) {
        submitBtn.textContent = 'UPDATE ISSUE';
        submitBtn.disabled = false;
      }
    }
  });
}

function renderAdminTimeline(updates) {
  const container = document.getElementById('admin-timeline-container');
  const countBadge = document.getElementById('admin-timeline-count');
  if (!container) return;

  if (countBadge) {
    countBadge.textContent = `${updates.length} Update${updates.length === 1 ? '' : 's'}`;
  }

  if (updates.length === 0) {
    container.innerHTML = `<p style="font-size: var(--font-size-xs); color: var(--color-text-muted);">No audit entries recorded.</p>`;
    return;
  }

  // Reverse chronological
  const sorted = [...updates].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

  container.innerHTML = sorted.map((u, idx) => {
    const isLatest = idx === 0;
    const formattedDate = new Date(u.created_at).toLocaleString();
    const updaterName = u.updated_by === 3 ? 'Admin Officer Rajesh' : `Citizen User #${u.updated_by}`;

    return `
      <div style="margin-bottom: var(--space-4); position: relative; padding-bottom: var(--space-2); border-bottom: 1px dashed var(--color-border-subtle);">
        <div style="display: flex; align-items: center; justify-content: space-between; gap: var(--space-2); margin-bottom: var(--space-1);">
          <span class="status-badge ${getStatusBadgeClass(u.status)}" style="font-size: 0.7rem; padding: 1px 6px;">
            ${formatStatus(u.status)}
          </span>
          <span style="font-size: 0.7rem; color: var(--color-text-muted);">
            ${formattedDate}
          </span>
        </div>
        <p style="font-size: var(--font-size-sm); color: var(--color-text-main); margin: var(--space-1) 0; font-weight: ${isLatest ? '600' : '400'};">
          ${escapeHtml(u.comment)}
        </p>
        <span style="font-size: var(--font-size-xs); color: var(--color-text-muted);">
          👤 ${escapeHtml(updaterName)}
        </span>
      </div>
    `;
  }).join('');
}

function initAdminMap(lat, lng, title) {
  const mapContainer = document.getElementById('admin-details-map');
  if (!mapContainer || typeof L === 'undefined') return;

  if (adminMapInstance) {
    adminMapInstance.remove();
    adminMapInstance = null;
  }

  try {
    adminMapInstance = L.map('admin-details-map', {
      center: [lat, lng],
      zoom: 15,
      scrollWheelZoom: false
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(adminMapInstance);

    const marker = L.marker([lat, lng]).addTo(adminMapInstance);
    marker.bindPopup(`<b>${escapeHtml(title)}</b><br>Lat: ${lat}, Lng: ${lng}`).openPopup();
  } catch (err) {
    console.error('Error rendering admin details map:', err);
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
