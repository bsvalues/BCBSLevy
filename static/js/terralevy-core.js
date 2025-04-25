/**
 * TerraLevy Core JavaScript
 * Core functionality for the TerraLevy application
 */

// Initialize the TerraLevy application namespace
const TerraLevy = {
  /**
   * Application configuration
   */
  config: {
    apiBaseUrl: '/api',
    dateFormat: 'MM/DD/YYYY',
    theme: {
      charts: {
        colors: [
          '#00e5ff', // Primary
          '#00b8d4', // Secondary
          '#004d7a', // Light blue
          '#002a4a', // Medium blue
          '#001529', // Dark blue
          '#4fc3f7',
          '#29b6f6',
          '#03a9f4',
          '#039be5',
          '#0288d1'
        ],
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
      }
    }
  },

  /**
   * Initialize TerraLevy application
   */
  init() {
    console.log('TerraLevy Core initialized');
    this.setupEventListeners();
    this.initializeChartDefaults();
    this.initializeDataTables();
    this.setupAccessibility();
  },

  /**
   * Set up global event listeners
   */
  setupEventListeners() {
    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.navbar-toggler');
    if (mobileMenuToggle) {
      mobileMenuToggle.addEventListener('click', () => {
        document.body.classList.toggle('nav-open');
      });
    }

    // Search functionality
    const searchForm = document.querySelector('.tl-search-form');
    if (searchForm) {
      searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const query = searchForm.querySelector('input').value.trim();
        if (query) {
          window.location.href = `/search?q=${encodeURIComponent(query)}`;
        }
      });
    }

    // Handle data-refresh elements
    document.addEventListener('click', (e) => {
      if (e.target.closest('[data-refresh]')) {
        const refreshEl = e.target.closest('[data-refresh]');
        const targetId = refreshEl.dataset.refresh;
        const targetEl = document.getElementById(targetId);
        
        if (targetEl) {
          this.refreshContent(targetEl, refreshEl.dataset.url);
        }
      }
    });

    // Handle data-toggle-collapse elements
    document.addEventListener('click', (e) => {
      if (e.target.closest('[data-toggle-collapse]')) {
        const toggleEl = e.target.closest('[data-toggle-collapse]');
        const targetId = toggleEl.dataset.toggleCollapse;
        const targetEl = document.getElementById(targetId);
        
        if (targetEl) {
          const isCollapsed = targetEl.classList.contains('show');
          if (isCollapsed) {
            targetEl.classList.remove('show');
            toggleEl.setAttribute('aria-expanded', 'false');
          } else {
            targetEl.classList.add('show');
            toggleEl.setAttribute('aria-expanded', 'true');
          }
        }
      }
    });
  },

  /**
   * Initialize default Chart.js settings
   */
  initializeChartDefaults() {
    if (typeof Chart !== 'undefined') {
      Chart.defaults.font.family = this.config.theme.charts.fontFamily;
      Chart.defaults.color = '#4a5568';
      Chart.defaults.borderColor = '#e2e8f0';
      Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0, 21, 41, 0.8)';
      Chart.defaults.animation.duration = 1000;
      
      // Add responsive configuration for all charts
      Chart.defaults.responsive = true;
      Chart.defaults.maintainAspectRatio = false;
    }
  },

  /**
   * Initialize DataTables if available
   */
  initializeDataTables() {
    if (typeof $.fn.DataTable !== 'undefined') {
      $.extend(true, $.fn.DataTable.defaults, {
        language: {
          search: "_INPUT_",
          searchPlaceholder: "Search records...",
          lengthMenu: "Show _MENU_ entries",
          info: "Showing _START_ to _END_ of _TOTAL_ entries",
          infoEmpty: "Showing 0 to 0 of 0 entries",
          infoFiltered: "(filtered from _MAX_ total entries)",
          paginate: {
            first: '<i class="bi bi-chevron-double-left"></i>',
            previous: '<i class="bi bi-chevron-left"></i>',
            next: '<i class="bi bi-chevron-right"></i>',
            last: '<i class="bi bi-chevron-double-right"></i>'
          }
        },
        dom: "<'row'<'col-sm-12 col-md-6'l><'col-sm-12 col-md-6'f>>" +
             "<'row'<'col-sm-12'tr>>" +
             "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
        pageLength: 10,
        lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        autoWidth: false,
        responsive: true
      });
    }
  },

  /**
   * Set up accessibility features
   */
  setupAccessibility() {
    // Add focus visible class
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        document.body.classList.add('keyboard-navigation');
      }
    });

    document.addEventListener('mousedown', () => {
      document.body.classList.remove('keyboard-navigation');
    });

    // Skip to content functionality
    const skipLink = document.querySelector('.skip-to-content');
    if (skipLink) {
      skipLink.addEventListener('click', (e) => {
        e.preventDefault();
        const target = document.querySelector(skipLink.getAttribute('href'));
        if (target) {
          target.setAttribute('tabindex', '-1');
          target.focus();
        }
      });
    }
  },

  /**
   * Refresh content in a container with AJAX
   * @param {HTMLElement} container - Container element to refresh
   * @param {string} url - URL to fetch content from
   */
  refreshContent(container, url) {
    // Add loading state
    container.innerHTML = `
      <div class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2 text-muted">Loading data...</p>
      </div>
    `;

    // Fetch new content
    fetch(url)
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.text();
      })
      .then(html => {
        container.innerHTML = html;
        // Dispatch event for other components to react
        container.dispatchEvent(new CustomEvent('content-refreshed'));
      })
      .catch(error => {
        container.innerHTML = `
          <div class="alert tl-alert-error" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            Error loading content: ${error.message}
          </div>
        `;
        console.error('Error refreshing content:', error);
      });
  },

  /**
   * Show a notification message
   * @param {string} message - The message to display
   * @param {string} type - Type of notification (success, error, warning, info)
   * @param {number} duration - Duration in milliseconds to show the notification
   */
  showNotification(message, type = 'info', duration = 5000) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `tl-notification tl-notification-${type}`;
    
    // Add icon based on type
    let icon = 'info-circle';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'exclamation-circle';
    if (type === 'warning') icon = 'exclamation-triangle';
    
    notification.innerHTML = `
      <div class="tl-notification-icon">
        <i class="bi bi-${icon}"></i>
      </div>
      <div class="tl-notification-content">
        ${message}
      </div>
      <button type="button" class="tl-notification-close" aria-label="Close">
        <i class="bi bi-x"></i>
      </button>
    `;
    
    // Add to notifications container or create one
    let container = document.querySelector('.tl-notifications-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'tl-notifications-container';
      document.body.appendChild(container);
    }
    
    container.appendChild(notification);
    
    // Add closing functionality
    const closeBtn = notification.querySelector('.tl-notification-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        notification.classList.add('tl-notification-hiding');
        setTimeout(() => {
          notification.remove();
        }, 300);
      });
    }
    
    // Auto remove after duration
    if (duration > 0) {
      setTimeout(() => {
        if (notification.parentNode) {
          notification.classList.add('tl-notification-hiding');
          setTimeout(() => {
            notification.remove();
          }, 300);
        }
      }, duration);
    }
    
    // Add show class after a small delay (for animation)
    setTimeout(() => {
      notification.classList.add('tl-notification-visible');
    }, 10);
  },

  /**
   * Format date based on the application's date format
   * @param {Date|string} date - Date to format
   * @returns {string} Formatted date string
   */
  formatDate(date) {
    const d = new Date(date);
    if (isNaN(d.getTime())) {
      return 'Invalid date';
    }
    
    // Format based on config
    const format = this.config.dateFormat;
    let result = format;
    
    // Year
    result = result.replace('YYYY', d.getFullYear());
    result = result.replace('YY', d.getFullYear().toString().slice(-2));
    
    // Month
    const month = d.getMonth() + 1;
    result = result.replace('MM', month.toString().padStart(2, '0'));
    result = result.replace('M', month);
    
    // Day
    const day = d.getDate();
    result = result.replace('DD', day.toString().padStart(2, '0'));
    result = result.replace('D', day);
    
    return result;
  }
};

// Initialize TerraLevy when DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
  TerraLevy.init();
});