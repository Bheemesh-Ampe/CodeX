/**
 * ==============================================================================
 * CIVICFIX — Main Application Controller (js/app.js)
 * ==============================================================================
 * Handles tab navigation, UI initialization, and backend connectivity checks.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize UI components
  initTabNavigation();
  checkBackendConnectivity();
});

/**
 * Tab Navigation: Switch between Resident Portal and Admin Dashboard
 */
function initTabNavigation() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  const residentSection = document.getElementById('resident-section');
  const adminSection = document.getElementById('admin-section');

  tabButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      // 1. Remove 'active' class from all tab buttons
      tabButtons.forEach((b) => b.classList.remove('active'));

      // 2. Add 'active' class to the clicked button
      btn.classList.add('active');

      // 3. Toggle section visibility
      const targetId = btn.getAttribute('data-target');
      if (targetId === 'resident-section') {
        residentSection.style.display = 'block';
        adminSection.style.display = 'none';
      } else if (targetId === 'admin-section') {
        residentSection.style.display = 'none';
        adminSection.style.display = 'block';
      }
    });
  });
}

/**
 * Backend Connectivity Check: Uses api.checkHealth() to verify connection to FastAPI
 */
async function checkBackendConnectivity() {
  const statusDot = document.getElementById('api-status-dot');
  const statusText = document.getElementById('api-status-text');

  if (!statusDot || !statusText) return;

  try {
    const health = await window.api.checkHealth();
    if (health && health.status === 'healthy') {
      statusDot.className = 'status-dot dot-online';
      statusText.textContent = 'Backend Online';
      statusDot.title = `Connected: ${health.service} v${health.version || '0.1.0'}`;
    } else {
      statusDot.className = 'status-dot dot-offline';
      statusText.textContent = 'Backend Issue';
    }
  } catch (error) {
    statusDot.className = 'status-dot dot-offline';
    statusText.textContent = 'Backend Offline';
    statusDot.title = 'Unable to connect to http://localhost:8000. Start backend server.';
  }
}
