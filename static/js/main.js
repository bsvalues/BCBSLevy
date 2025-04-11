/**
 * Main JavaScript functionality for the Levy Calculation System
 * 
 * This file contains core JavaScript functionality for the application,
 * including UI enhancements, form validation, and user interaction.
 */

document.addEventListener('DOMContentLoaded', function() {
  console.log('Main JS initialized');
  
  // Initialize tooltips and popovers if Bootstrap is available
  if (typeof bootstrap !== 'undefined') {
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
      const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
    
    // Initialize popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    if (popoverTriggerList.length > 0) {
      const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    }
  }
  
  // Set up guided tours
  if (typeof introJs !== 'undefined') {
    // Get all tour trigger elements
    const tourTriggers = document.querySelectorAll('[data-tour]');
    
    tourTriggers.forEach(trigger => {
      trigger.addEventListener('click', function() {
        const tourName = this.getAttribute('data-tour');
        startTour(tourName);
      });
    });
  }
  
  // Help menu button creation is now managed in help_menu.js
  // createHelpMenu();
});

/**
 * Start a guided tour of the application.
 * This function is now just a wrapper around tourInitializer.startTour
 * to maintain backward compatibility.
 * 
 * @param {string} tourName - The name of the tour to start
 */
function startTour(tourName) {
  try {
    // Check if tourInitializer is available
    if (window.tourInitializer && typeof window.tourInitializer.startTour === 'function') {
      // Use the centralized tour initializer
      window.tourInitializer.startTour(tourName);
    } else {
      console.error('Tour initializer not found. Make sure tour_initializer.js is loaded before guided_tour.js');
    }
  } catch (error) {
    console.error('Error starting tour:', error);
  }
}

/**
 * Create and manage the help menu
 */
function createHelpMenu() {
  // Create help button
  const helpButton = document.createElement('div');
  helpButton.className = 'help-menu-button';
  helpButton.innerHTML = '?';
  
  // Create help menu
  const helpMenu = document.createElement('div');
  helpMenu.className = 'help-menu';
  
  // Add menu items
  helpMenu.innerHTML = `
    <div class="help-menu-item" data-tour="dashboard">Dashboard Tour</div>
    <div class="help-menu-item" data-tour="levy-calculator">Levy Calculator Tour</div>
    <div class="help-menu-item" data-tour="import">Import Data Tour</div>
    <div class="help-menu-item" data-action="glossary">Tax Glossary</div>
    <div class="help-menu-item" data-action="faq">FAQ</div>
    <div class="help-menu-item" data-action="support">Support</div>
  `;
  
  // Add elements to the DOM
  document.body.appendChild(helpButton);
  document.body.appendChild(helpMenu);
  
  // Toggle menu on button click
  helpButton.addEventListener('click', function() {
    helpMenu.classList.toggle('active');
  });
  
  // Add click events to help menu items
  const helpMenuItems = document.querySelectorAll('.help-menu-item');
  helpMenuItems.forEach(item => {
    item.addEventListener('click', function() {
      const tour = this.getAttribute('data-tour');
      const action = this.getAttribute('data-action');
      
      if (tour) {
        startTour(tour);
        helpMenu.classList.remove('active');
      }
      
      // Handle actions
      if (action === 'glossary') {
        window.location.href = '/glossary';
      }
      if (action === 'faq') {
        window.location.href = '/faq';
      }
      if (action === 'support') {
        window.location.href = '/support';
      }
      
      helpMenu.classList.remove('active');
    });
  });
  
  // Close menu when clicking outside
  document.addEventListener('click', function(event) {
    if (!helpButton.contains(event.target) && !helpMenu.contains(event.target)) {
      helpMenu.classList.remove('active');
    }
  });
}

// Form validation
(function() {
  'use strict'
  
  // Fetch all the forms we want to apply custom Bootstrap validation styles to
  const forms = document.querySelectorAll('.needs-validation');
  
  // Loop over them and prevent submission
  Array.from(forms).forEach(form => {
    form.addEventListener('submit', event => {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      
      form.classList.add('was-validated');
    }, false);
  });
})();

// Initialize Bootstrap tooltips if available
if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  Array.from(tooltipTriggerList).map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

// Initialize DataTables if available
document.addEventListener('DOMContentLoaded', function() {
  if (typeof $.fn.DataTable !== 'undefined') {
    $('.datatable').DataTable({
      responsive: true,
      pageLength: 25,
      language: {
        search: "_INPUT_",
        searchPlaceholder: "Search..."
      },
      dom: 
        "<'row'<'col-sm-12 col-md-6'l><'col-sm-12 col-md-6'f>>" +
        "<'row'<'col-sm-12'tr>>" +
        "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>"
    });
  }
});

// Auto-hide flash messages after delay
document.addEventListener('DOMContentLoaded', function() {
  const flashMessages = document.querySelectorAll('.alert-dismissible');
  
  flashMessages.forEach(message => {
    // Auto-hide after 5 seconds
    setTimeout(() => {
      message.classList.add('fade-out');
      
      // Remove from DOM after animation
      setTimeout(() => {
        message.remove();
      }, 500);
    }, 5000);
  });
});
