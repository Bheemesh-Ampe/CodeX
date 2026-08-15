/**
 * ==============================================================================
 * CIVICFIX — Main Controller & Design System Navigation (js/main.js)
 * ==============================================================================
 * Handles responsive mobile navigation toggle and active page indicator.
 */

document.addEventListener('DOMContentLoaded', () => {
  initMobileNavigation();
  highlightActiveNavigation();
});

/**
 * Mobile Navigation Toggle (Hamburger Menu)
 */
function initMobileNavigation() {
  const toggleBtn = document.querySelector('.nav-toggle');
  const navMenu = document.querySelector('.nav-menu');

  if (toggleBtn && navMenu) {
    toggleBtn.addEventListener('click', () => {
      const isExpanded = navMenu.classList.toggle('open');
      toggleBtn.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
    });

    // Close menu when clicking outside on mobile
    document.addEventListener('click', (event) => {
      if (!navMenu.contains(event.target) && !toggleBtn.contains(event.target)) {
        navMenu.classList.remove('open');
        toggleBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }
}

/**
 * Automatically marks current route active in navigation menu
 */
function highlightActiveNavigation() {
  const currentPath = window.location.pathname.split('/').pop() || 'index.html';
  const navLinks = document.querySelectorAll('.nav-link');

  navLinks.forEach((link) => {
    const href = link.getAttribute('href');
    if (href && (href === currentPath || href.endsWith(currentPath))) {
      link.classList.add('active');
    }
  });
}
