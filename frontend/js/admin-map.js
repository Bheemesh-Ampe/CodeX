/**
 * ==============================================================================
 * CIVICFIX Admin — City-Wide Distribution Map Controller (js/admin-map.js)
 * ==============================================================================
 * Renders all municipal issues as interactive pins on OpenStreetMap via Leaflet.
 */

let adminMap = null;

document.addEventListener('DOMContentLoaded', async () => {
  await initCityMap();
});

async function initCityMap() {
  const mapContainer = document.getElementById('admin-city-map');
  const countBadge = document.getElementById('map-pins-count');

  if (!mapContainer) return;

  if (typeof L === 'undefined') {
    console.warn('Leaflet library unavailable.');
    mapContainer.innerHTML = `
      <div style="padding: var(--space-8); text-align: center; color: var(--color-text-muted);">
        ⚠️ Interactive map tiles unavailable. Please check your internet connection.
      </div>
    `;
    if (countBadge) countBadge.textContent = 'Map Offline';
    return;
  }

  try {
    // 1. Initialize Map instance
    adminMap = L.map('admin-city-map', {
      center: [12.9716, 77.5946],
      zoom: 13,
      scrollWheelZoom: true
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(adminMap);

    // 2. Fetch issues from API
    const issues = await window.api.getIssues();

    if (!issues || issues.length === 0) {
      if (countBadge) countBadge.textContent = '0 Issues Active';
      return;
    }

    const markersGroup = [];

    // 3. Add pins for each geocoded issue
    issues.forEach((issue) => {
      if (issue.latitude && issue.longitude) {
        const lat = parseFloat(issue.latitude);
        const lng = parseFloat(issue.longitude);

        if (!isNaN(lat) && !isNaN(lng)) {
          const marker = L.marker([lat, lng]).addTo(adminMap);
          markersGroup.push([lat, lng]);

          const formattedId = `CF-${1000 + Number(issue.id)}`;
          const locationText = issue.address || `Lat ${lat.toFixed(3)}, Lng ${lng.toFixed(3)}`;

          const popupContent = `
            <div style="font-family: 'Plus Jakarta Sans', sans-serif; min-width: 220px; padding: 2px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <strong style="color: #2563eb; font-size: 11px;">${formattedId}</strong>
                <span style="font-size: 10px; font-weight: 700; background: #e0f2fe; color: #0369a1; padding: 2px 6px; border-radius: 9999px;">
                  ${formatStatus(issue.status)}
                </span>
              </div>
              <h4 style="font-size: 13px; font-weight: 800; margin: 0 0 4px 0; color: #0f172a;">
                ${escapeHtml(issue.title)}
              </h4>
              <p style="font-size: 11px; color: #64748b; margin: 0 0 6px 0;">
                📍 ${escapeHtml(locationText)}
              </p>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 11px; color: #475569;">
                  <strong>Cat:</strong> ${escapeHtml(issue.category)}
                </span>
                <span style="font-size: 10px; font-weight: 700; color: ${issue.priority === 'HIGH' || issue.priority === 'CRITICAL' ? '#dc2626' : '#d97706'};">
                  ${issue.priority} Priority
                </span>
              </div>
              <a href="issue-details.html?id=${issue.id}" style="display: block; text-align: center; background: #2563eb; color: #ffffff; text-decoration: none; font-size: 12px; font-weight: 700; padding: 6px 10px; border-radius: 6px;">
                🔍 View Issue
              </a>
            </div>
          `;

          marker.bindPopup(popupContent);
        }
      }
    });

    if (countBadge) {
      countBadge.textContent = `${markersGroup.length} Issues Plotted`;
    }

    // 4. Adjust bounds to fit all markers
    if (markersGroup.length > 0) {
      adminMap.fitBounds(markersGroup, { padding: [40, 40] });
    }
  } catch (error) {
    console.error('Error plotting admin map markers:', error);
    if (countBadge) countBadge.textContent = 'Error Ploting Pins';
  }
}

function formatStatus(status) {
  return (status || '').replace('_', ' ');
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
