/**
 * Tax-Themed Loading Animations
 * 
 * JavaScript functionality for managing tax-themed loading animations
 * throughout the Levy Calculation System.
 */

// Initialize the loading animations when the document is loaded
document.addEventListener('DOMContentLoaded', function() {
  initializeLoadingAnimations();
});

/**
 * Initialize all loading animation functionality
 */
function initializeLoadingAnimations() {
  // Add the loading animations CSS to the page
  appendAnimationStyles();
  
  // Set up loading behavior for form submissions
  setupFormSubmitLoading();
  
  // Set up loading behavior for AJAX requests
  setupAjaxLoadingHandlers();
  
  // Initialize any elements with the data-loading-auto attribute
  initAutoLoadingElements();
  
  console.log('Loading animations initialized');
}

/**
 * Append animation styles to the document head
 */
function appendAnimationStyles() {
  if (!document.getElementById('loading-animations-css')) {
    const link = document.createElement('link');
    link.id = 'loading-animations-css';
    link.rel = 'stylesheet';
    link.href = '/static/css/animations/loading-animations.css';
    document.head.appendChild(link);
  }
}

/**
 * Set up loading behavior for form submissions
 */
function setupFormSubmitLoading() {
  // Find all forms with the loading-indicator attribute
  const forms = document.querySelectorAll('form[data-loading="true"]');
  
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      // Only show loading if the form is valid
      if (form.checkValidity()) {
        const loadingType = form.getAttribute('data-loading-type') || 'default';
        const loadingText = form.getAttribute('data-loading-text') || 'Processing your request';
        const targetEl = form.getAttribute('data-loading-target');
        
        // If there's a specific target element, use that, otherwise overlay the form
        if (targetEl) {
          showLoadingInElement(document.querySelector(targetEl), loadingType, loadingText);
        } else {
          // Create overlay within the form
          showLoadingInElement(form, loadingType, loadingText);
          
          // Disable all inputs and buttons
          const inputs = form.querySelectorAll('input, button, select, textarea');
          inputs.forEach(input => {
            input.disabled = true;
          });
        }
      }
    });
  });
}

/**
 * Set up loading behavior for AJAX requests
 */
function setupAjaxLoadingHandlers() {
  // Set up AJAX loading for elements with the data-ajax-loading attribute
  const ajaxElements = document.querySelectorAll('[data-ajax-loading="true"]');
  
  ajaxElements.forEach(element => {
    // Find the closest button or the element itself if it's a button
    const button = element.tagName === 'BUTTON' ? 
      element : 
      element.querySelector('button');
    
    if (button) {
      button.addEventListener('click', function(e) {
        const loadingType = element.getAttribute('data-loading-type') || 'default';
        const loadingText = element.getAttribute('data-loading-text') || 'Loading data';
        const targetEl = element.getAttribute('data-loading-target');
        
        // Show loading animation in the specified target or create a fullscreen overlay
        if (targetEl) {
          showLoadingInElement(document.querySelector(targetEl), loadingType, loadingText);
        } else {
          showLoadingOverlay(loadingType, loadingText);
        }
      });
    }
  });
}

/**
 * Initialize elements that should automatically show loading animations
 */
function initAutoLoadingElements() {
  const autoLoadElements = document.querySelectorAll('[data-loading-auto="true"]');
  
  autoLoadElements.forEach(element => {
    const loadingType = element.getAttribute('data-loading-type') || 'default';
    const loadingText = element.getAttribute('data-loading-text') || 'Loading';
    
    showLoadingInElement(element, loadingType, loadingText);
  });
}

/**
 * Show a loading animation inside a specified element
 * 
 * @param {HTMLElement} element - The element to show the loading animation in
 * @param {string} type - The type of loading animation to show
 * @param {string} text - The loading text to display
 */
function showLoadingInElement(element, type, text) {
  // Clear the element's contents
  const originalContent = element.innerHTML;
  element.setAttribute('data-original-content', originalContent);
  
  // Create the loading HTML based on the type
  const loadingHTML = createLoadingHTML(type, text);
  
  // Set the element's content to the loading HTML
  element.innerHTML = loadingHTML;
  
  // Add a loading class to the element
  element.classList.add('levy-is-loading');
  
  return {
    // Return a function to hide the loading and restore original content
    hide: function() {
      element.innerHTML = element.getAttribute('data-original-content');
      element.removeAttribute('data-original-content');
      element.classList.remove('levy-is-loading');
    }
  };
}

/**
 * Show a full-screen loading overlay
 * 
 * @param {string} type - The type of loading animation to show
 * @param {string} text - The loading text to display
 */
function showLoadingOverlay(type, text) {
  // Create overlay element
  const overlay = document.createElement('div');
  overlay.className = 'levy-loading-overlay';
  
  // Create the loading HTML based on the type
  const loadingHTML = createLoadingHTML(type, text);
  
  // Set the overlay's content
  overlay.innerHTML = loadingHTML;
  
  // Add the overlay to the document body
  document.body.appendChild(overlay);
  
  // Prevent scrolling on the body
  document.body.style.overflow = 'hidden';
  
  return {
    // Return a function to hide the overlay
    hide: function() {
      document.body.style.overflow = '';
      overlay.style.opacity = '0';
      
      // Remove after transition completes
      setTimeout(() => {
        if (document.body.contains(overlay)) {
          document.body.removeChild(overlay);
        }
      }, 300);
    }
  };
}

/**
 * Create HTML for the loading animation based on the specified type
 * 
 * @param {string} type - The type of loading animation to create
 * @param {string} text - The loading text to display
 * @returns {string} The HTML for the loading animation
 */
function createLoadingHTML(type, text) {
  let animationHTML = '';
  
  // Choose the animation based on the type
  switch (type) {
    case 'dollar-bill':
      animationHTML = '<div class="loading-dollar-bill"><img src="/static/images/animations/dollar-bill.svg" alt="Loading"></div>';
      break;
    case 'tax-calculator':
      animationHTML = '<div class="loading-tax-calculator"><img src="/static/images/animations/tax-calculator.svg" alt="Loading"></div>';
      break;
    case 'property-tax':
      animationHTML = '<div class="loading-property-tax"><img src="/static/images/animations/property-tax.svg" alt="Loading"></div>';
      break;
    case 'coins':
      animationHTML = '<div class="loading-coins"><img src="/static/images/animations/loading-coins.svg" alt="Loading"></div>';
      break;
    case 'tax-form':
      animationHTML = '<div class="loading-tax-form"><img src="/static/images/animations/tax-form.svg" alt="Loading"></div>';
      break;
    default:
      // Randomly choose an animation for the default case
      const animations = ['dollar-bill', 'tax-calculator', 'property-tax', 'coins', 'tax-form'];
      const randomType = animations[Math.floor(Math.random() * animations.length)];
      return createLoadingHTML(randomType, text);
  }
  
  // Construct the full loading HTML
  return `
    <div class="levy-loading-container">
      <div class="levy-loading-animation">
        ${animationHTML}
      </div>
      <div class="levy-loading-text">${text}<span class="loading-dots"></span></div>
      <div class="levy-progress-bar"></div>
    </div>
  `;
}

/**
 * Global loading animation functions exposed to the window object
 */

// Show loading in an element
window.showLevyLoading = function(selector, type, text) {
  const element = (typeof selector === 'string') ? 
    document.querySelector(selector) : selector;
  
  if (element) {
    return showLoadingInElement(element, type || 'default', text || 'Loading');
  }
  
  console.error('Element not found for loading:', selector);
  return { hide: function() {} };
};

// Show full-screen loading overlay
window.showLevyLoadingOverlay = function(type, text) {
  return showLoadingOverlay(type || 'default', text || 'Loading');
};

// Hide all loading animations
window.hideLevyLoadingAll = function() {
  // Remove any full-screen overlays
  const overlays = document.querySelectorAll('.levy-loading-overlay');
  overlays.forEach(overlay => {
    document.body.style.overflow = '';
    overlay.style.opacity = '0';
    setTimeout(() => {
      if (document.body.contains(overlay)) {
        document.body.removeChild(overlay);
      }
    }, 300);
  });
  
  // Restore original content to any elements with loading
  const loadingElements = document.querySelectorAll('.levy-is-loading');
  loadingElements.forEach(element => {
    const originalContent = element.getAttribute('data-original-content');
    if (originalContent) {
      element.innerHTML = originalContent;
      element.removeAttribute('data-original-content');
    }
    element.classList.remove('levy-is-loading');
  });
  
  // Re-enable any disabled form elements
  const forms = document.querySelectorAll('form[data-loading="true"]');
  forms.forEach(form => {
    const inputs = form.querySelectorAll('input, button, select, textarea');
    inputs.forEach(input => {
      input.disabled = false;
    });
  });
};
