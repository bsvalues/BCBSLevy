/**
 * Public Portal JavaScript
 * Provides interactive functionality for the public-facing portal
 */

document.addEventListener("DOMContentLoaded", function () {
  // Enable tooltips with improved touch device support
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]'),
  );
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl, {
      html: true,
      trigger: isTouchDevice() ? "click" : "hover focus", // Use click on touch devices
      boundary: document.body, // Prevent positioning issues
    });
  });

  // Enable popovers with improved touch device support
  const popoverTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="popover"]'),
  );
  popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl, {
      html: true,
      trigger: isTouchDevice() ? "click" : "hover focus",
      boundary: document.body,
    });
  });

  // Initialize back to top button
  initBackToTop();

  // Property Lookup Form Validation
  const propertyLookupForm = document.querySelector(
    'form[action*="property_lookup"]',
  );
  if (propertyLookupForm) {
    propertyLookupForm.addEventListener("submit", function (event) {
      const propertyId = document.getElementById("property_id");
      if (propertyId && propertyId.value.trim() === "") {
        event.preventDefault();
        showAlert("Please enter a Property ID", "danger");
        propertyId.focus();
      }
    });
  }

  // Print Property Information Button
  const printPropertyBtn = document.getElementById("printPropertyInfo");
  if (printPropertyBtn) {
    printPropertyBtn.addEventListener("click", function () {
      window.print();
    });
  }

  // Add event listeners to the tax rate comparison chart tabs if they exist
  const taxRateTabs = document.querySelectorAll(
    '[data-bs-toggle="tab"][href*="tax-rate"]',
  );
  taxRateTabs.forEach(function (tab) {
    tab.addEventListener("shown.bs.tab", function (event) {
      // Reinitialize chart when tab is shown
      if (window.taxRateChart) {
        window.taxRateChart.resize();
      }
    });
  });

  // Initialize tooltips that appear on hover over tax terms
  initializeTermTooltips();
});

/**
 * Shows an alert message
 * @param {string} message - The message to display
 * @param {string} type - The alert type (success, danger, warning, info)
 */
function showAlert(message, type = "info") {
  const alertContainer = document.createElement("div");
  alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
  alertContainer.setAttribute("role", "alert");

  alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

  // Find the container to insert the alert
  const container = document.querySelector(".container");
  const firstChild = container.firstChild;
  container.insertBefore(alertContainer, firstChild);

  // Auto-dismiss after 5 seconds
  setTimeout(function () {
    const bsAlert = new bootstrap.Alert(alertContainer);
    bsAlert.close();
  }, 5000);
}

/**
 * Initialize tooltips for tax terminology
 */
function initializeTermTooltips() {
  const taxTerms = document.querySelectorAll(".tax-term");
  taxTerms.forEach(function (term) {
    const tooltipText = term.getAttribute("data-tooltip");
    if (tooltipText) {
      term.setAttribute("data-bs-toggle", "tooltip");
      term.setAttribute("data-bs-placement", "top");
      term.setAttribute("title", tooltipText);
      new bootstrap.Tooltip(term, {
        html: true,
      });
    }
  });
}

/**
 * Formats a number as currency
 * @param {number} value - The number to format
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted currency string
 */
function formatCurrency(value, decimals = 2) {
  return (
    "$" +
    parseFloat(value)
      .toFixed(decimals)
      .replace(/\d(?=(\d{3})+\.)/g, "$&,")
  );
}

/**
 * Formats a number as a percentage
 * @param {number} value - The number to format
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted percentage string
 */
function formatPercentage(value, decimals = 2) {
  return parseFloat(value).toFixed(decimals) + "%";
}

/**
 * Calculate property tax based on assessed value and levy rate
 * @param {number} assessedValue - Property's assessed value
 * @param {number} levyRate - Levy rate per $1000
 * @returns {number} Calculated tax amount
 */
function calculatePropertyTax(assessedValue, levyRate) {
  return (assessedValue / 1000) * levyRate;
}

/**
 * Calculate percentage change between two values
 * @param {number} oldValue - Original value
 * @param {number} newValue - New value
 * @returns {number} Percentage change
 */
function calculatePercentageChange(oldValue, newValue) {
  if (oldValue === 0) return 100; // Handle division by zero
  return ((newValue - oldValue) / oldValue) * 100;
}

/**
 * Adds a CSS class based on value change (positive, negative, or neutral)
 * @param {number} value - The change value to evaluate
 * @returns {string} CSS class name
 */
function getChangeClass(value) {
  if (value > 0) return "tax-rate-change-positive";
  if (value < 0) return "tax-rate-change-negative";
  return "tax-rate-change-neutral";
}

/**
 * Detects if the current device is a touch device
 * @returns {boolean} True if touch device, false otherwise
 */
function isTouchDevice() {
  return (
    "ontouchstart" in window ||
    navigator.maxTouchPoints > 0 ||
    navigator.msMaxTouchPoints > 0
  );
}

/**
 * Initializes the back to top button functionality
 */
function initBackToTop() {
  const backToTopBtn = document.getElementById("back-to-top-btn");

  if (!backToTopBtn) return;

  // Show button when user scrolls down 300px
  window.addEventListener("scroll", function () {
    if (window.pageYOffset > 300) {
      backToTopBtn.classList.add("show");
    } else {
      backToTopBtn.classList.remove("show");
    }
  });

  // Scroll to top when button is clicked
  backToTopBtn.addEventListener("click", function (e) {
    e.preventDefault();
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  });

  // Initially check scroll position
  if (window.pageYOffset > 300) {
    backToTopBtn.classList.add("show");
  }
}
