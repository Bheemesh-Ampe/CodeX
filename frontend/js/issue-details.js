/**
 * ==============================================================================
 * CIVICFIX — Resident Issue Details Controller (js/issue-details.js)
 * ==============================================================================
 * Loads issue details by ID from the API layer, displays photos, Leaflet map,
 * AI triage card, lifecycle stepper, and full resolution audit trail.
 */

let detailsMapInstance = null;

document.addEventListener('DOMContentLoaded', async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const rawId = urlParams.get('id') || '1';

  // Support both "1" and "CF-1001" formats
  const parsedId = rawId.startsWith('CF-') ? parseInt(rawId.replace('CF-', '')) - 1000 : parseInt(rawId);
  const targetId = isNaN(parsedId) ? 1 : parsedId;

  await loadIssueDetails(targetId);
});

async function loadIssueDetails(issueId) {
  const errorBox = document.getElementById('details-error');
  const errorMsg = document.getElementById('details-error-msg');
  const contentBox = document.getElementById('details-content');

  try {
    const issue = await window.api.getIssueById(issueId);

    if (errorBox) errorBox.style.display = 'none';
    if (contentBox) contentBox.style.display = 'block';

    renderIssue(issue);
  } catch (error) {
    console.error('Failed to load issue details:', error);
    if (contentBox) contentBox.style.display = 'none';
    if (errorBox) {
      errorBox.style.display = 'flex';
      if (errorMsg) errorMsg.textContent = `Issue #${issueId} could not be found or loaded.`;
    }
    const titleEl = document.getElementById('issue-title');
    if (titleEl) titleEl.textContent = `Issue #${issueId} Not Found`;
  }
}

function renderIssue(issue) {
  const formattedId = `CF-${1000 + Number(issue.id)}`;
  const formattedCreated = new Date(issue.created_at).toLocaleString();
  const formattedUpdated = new Date(issue.updated_at || issue.created_at).toLocaleString();

  // 1. Title & Header Subtitle
  const titleEl = document.getElementById('issue-title');
  const subtitleEl = document.getElementById('issue-meta-subtitle');
  if (titleEl) titleEl.textContent = issue.title;
  if (subtitleEl) {
    subtitleEl.textContent = `Report ${formattedId} • Logged on ${formattedCreated}`;
  }

  // 2. Header Badges
  const statusBadge = document.getElementById('issue-status-badge');
  const priorityBadge = document.getElementById('issue-priority-badge');
  const categoryBadge = document.getElementById('issue-category-badge');

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

  // 3. Issue Information & Description
  const descEl = document.getElementById('issue-description');
  if (descEl) descEl.textContent = issue.description;

  const metaId = document.getElementById('meta-issue-id');
  const metaCategory = document.getElementById('meta-category');
  const metaCreated = document.getElementById('meta-created-at');
  const metaUpdated = document.getElementById('meta-updated-at');

  if (metaId) metaId.textContent = formattedId;
  if (metaCategory) metaCategory.textContent = issue.category;
  if (metaCreated) metaCreated.textContent = formattedCreated;
  if (metaUpdated) metaUpdated.textContent = formattedUpdated;

  // 4. Lifecycle Stepper Highlighting
  highlightLifecycleStepper(issue.status);

  // 5. AI Generated Analysis
  const aiSummary = document.getElementById('ai-summary-val');
  const aiCategory = document.getElementById('ai-category-val');
  const aiPriority = document.getElementById('ai-priority-val');
  const aiAction = document.getElementById('ai-action-val');

  if (aiSummary) aiSummary.textContent = issue.ai_summary ? `"${issue.ai_summary}"` : 'AI analysis pending or not triggered.';
  if (aiCategory) aiCategory.textContent = issue.ai_category || issue.category || '--';
  if (aiPriority) aiPriority.textContent = issue.ai_priority ? `${issue.ai_priority} Priority` : (issue.priority || '--');
  if (aiAction) aiAction.textContent = issue.ai_suggested_action || 'Pending municipal assignment and technician review.';

  // 6. Photo Evidence Handling
  const photoImg = document.getElementById('issue-photo-img');
  const photoPlaceholder = document.getElementById('photo-placeholder');
  const photoBadge = document.getElementById('photo-badge');

  if (issue.image_path) {
    if (photoImg) {
      photoImg.src = issue.image_path;
      photoImg.style.display = 'block';
    }
    if (photoPlaceholder) photoPlaceholder.style.display = 'none';
    if (photoBadge) photoBadge.textContent = 'Evidence Attached';
  } else {
    if (photoImg) photoImg.style.display = 'none';
    if (photoPlaceholder) {
      photoPlaceholder.textContent = '📷 No image available.';
      photoPlaceholder.style.display = 'block';
    }
    if (photoBadge) photoBadge.textContent = 'No Photo';
  }

  // 7. Location & Leaflet Map
  const addressText = document.getElementById('details-address-text');
  const coordsBadge = document.getElementById('issue-coords-badge');

  if (addressText) {
    addressText.textContent = issue.address || 'GPS Coordinates provided (no street address entered)';
  }

  if (coordsBadge) {
    coordsBadge.textContent = `Lat: ${parseFloat(issue.latitude).toFixed(4)}, Lng: ${parseFloat(issue.longitude).toFixed(4)}`;
  }

  initDetailsMap(issue.latitude, issue.longitude, issue.title, issue.address);

  // 8. Status Resolution Timeline (IssueUpdate list)
  renderTimeline(issue.updates || [], issue.status);
}

function highlightLifecycleStepper(currentStatus) {
  const statuses = ['REPORTED', 'IN_REVIEW', 'ASSIGNED', 'IN_PROGRESS', 'RESOLVED'];
  const normalized = (currentStatus || 'REPORTED').toUpperCase();
  const currentIndex = statuses.indexOf(normalized);

  statuses.forEach((st, idx) => {
    const el = document.getElementById(`step-${st}`);
    if (!el) return;

    if (idx <= currentIndex && currentIndex !== -1) {
      el.classList.add('active');
      if (idx === currentIndex) {
        el.classList.add('current');
      } else {
        el.classList.remove('current');
      }
    } else {
      el.classList.remove('active');
      el.classList.remove('current');
    }
  });
}

function renderTimeline(updates, currentStatus) {
  const container = document.getElementById('timeline-container');
  const countBadge = document.getElementById('timeline-count-badge');
  if (!container) return;

  if (countBadge) {
    countBadge.textContent = `${updates.length} Update${updates.length === 1 ? '' : 's'}`;
  }

  if (updates.length === 0) {
    container.innerHTML = `<p style="font-size: var(--font-size-xs); color: var(--color-text-muted);">No timeline updates recorded yet.</p>`;
    return;
  }

  // Show updates in reverse chronological order
  const sorted = [...updates].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

  container.innerHTML = sorted.map((u, idx) => {
    const isCurrent = idx === 0;
    const formattedDate = new Date(u.created_at).toLocaleString();
    const updaterName = u.updated_by === 3 ? 'Admin Officer Rajesh' : `User #${u.updated_by}`;

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
        <p style="font-size: var(--font-size-sm); color: var(--color-text-main); margin: var(--space-1) 0; font-weight: ${isCurrent ? '600' : '400'};">
          ${escapeHtml(u.comment)}
        </p>
        <span style="font-size: var(--font-size-xs); color: var(--color-text-muted);">
          👤 Updated by ${escapeHtml(updaterName)}
        </span>
      </div>
    `;
  }).join('');
}

function initDetailsMap(lat, lng, title, address) {
  const mapContainer = document.getElementById('details-map');
  if (!mapContainer || typeof L === 'undefined') return;

  if (detailsMapInstance) {
    detailsMapInstance.remove();
    detailsMapInstance = null;
  }

  try {
    detailsMapInstance = L.map('details-map', {
      center: [lat, lng],
      zoom: 15,
      scrollWheelZoom: false
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(detailsMapInstance);

    const marker = L.marker([lat, lng]).addTo(detailsMapInstance);
    marker.bindPopup(`<b>${escapeHtml(title)}</b><br>${escapeHtml(address || 'Report Location')}`).openPopup();
  } catch (err) {
    console.error('Error rendering details map:', err);
    mapContainer.innerHTML = `
      <div style="padding: var(--space-6); text-align: center; color: var(--color-text-muted); font-size: var(--font-size-xs);">
        📍 Map display unavailable. Coordinates: Lat ${lat}, Lng ${lng}
      </div>
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
