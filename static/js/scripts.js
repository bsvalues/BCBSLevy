/**
 * Main JavaScript for the LevyMaster
 */

document.addEventListener('DOMContentLoaded', function() {
  console.log('LevyMaster JS initialized successfully');
  
  // Initialize Bootstrap components
  initializeBootstrapComponents();
  
  // Setup form validations
  setupFormValidations();
  
  // Handle flash messages auto-dismiss
  setupFlashMessages();
  
  // Initialize theme toggler
  initializeThemeToggler();
  
  // Help menu initialization is disabled to prevent automatic popup
  // if (document.getElementById('help-button')) {
  //   initializeHelpMenu();
  // }
  
  // Guided tour initialization is disabled to prevent automatic popup
  // initializeGuidedTour();
});

/**
 * Initialize Bootstrap components
 */
function initializeBootstrapComponents() {
  // Initialize tooltips
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  if (tooltipTriggerList.length > 0) {
    [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
  }
  
  // Initialize popovers
  const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
  if (popoverTriggerList.length > 0) {
    [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
  }
}

/**
 * Setup form validations
 */
function setupFormValidations() {
  // Get all forms with validation
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
  
  // Add password strength meter if available
  const passwordInputs = document.querySelectorAll('input[type="password"]');
  passwordInputs.forEach(input => {
    if (input.id === 'new_password' || input.id === 'password') {
      input.addEventListener('input', updatePasswordStrength);
    }
  });
  
  // Add password match validation
  const confirmPasswordInputs = document.querySelectorAll('#confirm_password');
  confirmPasswordInputs.forEach(input => {
    input.addEventListener('input', validatePasswordMatch);
  });
}

/**
 * Update password strength meter
 */
function updatePasswordStrength() {
  const password = this.value;
  const meterEl = document.querySelector('.password-strength-meter');
  
  if (!meterEl) return;
  
  let strength = 0;
  let feedback = '';
  
  // Check password length
  if (password.length >= 8) {
    strength += 25;
  }
  
  // Check for uppercase letters
  if (/[A-Z]/.test(password)) {
    strength += 25;
  }
  
  // Check for numbers
  if (/[0-9]/.test(password)) {
    strength += 25;
  }
  
  // Check for special characters
  if (/[^A-Za-z0-9]/.test(password)) {
    strength += 25;
  }
  
  // Update meter width
  const progressBar = meterEl.querySelector('.progress-bar');
  progressBar.style.width = `${strength}%`;
  
  // Update feedback text and meter color
  if (strength < 25) {
    progressBar.className = 'progress-bar bg-danger';
    feedback = 'Very weak';
  } else if (strength < 50) {
    progressBar.className = 'progress-bar bg-warning';
    feedback = 'Weak';
  } else if (strength < 75) {
    progressBar.className = 'progress-bar bg-info';
    feedback = 'Good';
  } else {
    progressBar.className = 'progress-bar bg-success';
    feedback = 'Strong';
  }
  
  // Update feedback text
  const feedbackEl = meterEl.nextElementSibling;
  if (feedbackEl) {
    feedbackEl.textContent = feedback;
  }
}

/**
 * Validate password match
 */
function validatePasswordMatch() {
  const confirmPassword = this.value;
  const password = document.querySelector('#new_password, #password').value;
  
  if (confirmPassword === password) {
    this.setCustomValidity('');
  } else {
    this.setCustomValidity('Passwords do not match');
  }
}

/**
 * Setup flash messages auto-dismiss
 */
function setupFlashMessages() {
  const flashMessages = document.querySelectorAll('.alert-dismissible');
  
  flashMessages.forEach(message => {
    // Auto-dismiss flash messages after 5 seconds
    setTimeout(() => {
      if (message && message.parentNode) {
        message.classList.add('fade');
        setTimeout(() => {
          if (message.parentNode) {
            message.remove();
          }
        }, 500);
      }
    }, 5000);
  });
}

/**
 * Initialize theme toggler
 */
function initializeThemeToggler() {
  const themeToggleBtn = document.getElementById('darkModeToggle');
  
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', function() {
      const htmlEl = document.documentElement;
      
      if (htmlEl.getAttribute('data-bs-theme') === 'dark') {
        htmlEl.setAttribute('data-bs-theme', 'light');
        themeToggleBtn.innerHTML = '<i class="bi bi-sun-fill"></i>';
        localStorage.setItem('theme', 'light');
      } else {
        htmlEl.setAttribute('data-bs-theme', 'dark');
        themeToggleBtn.innerHTML = '<i class="bi bi-moon-fill"></i>';
        localStorage.setItem('theme', 'dark');
      }
    });
    
    // Check for saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
      document.documentElement.setAttribute('data-bs-theme', 'light');
      themeToggleBtn.innerHTML = '<i class="bi bi-sun-fill"></i>';
    }
  }
}

/**
 * Initialize help menu functionality
 */
function initializeHelpMenu() {
  console.log('Initializing help menu...');
  
  const helpButton = document.getElementById('help-button');
  
  if (helpButton) {
    // Create help menu container if it doesn't exist
    let helpMenu = document.querySelector('.help-menu');
    
    if (!helpMenu) {
      helpMenu = document.createElement('div');
      helpMenu.className = 'help-menu';
      
      // Add help menu items
      helpMenu.innerHTML = `
        <div class="help-menu-header">
          <h5>Help & Resources</h5>
        </div>
        <div class="help-menu-body">
          <ul class="help-menu-items">
            <li class="help-menu-item" data-tour="dashboard">
              <i class="bi bi-info-circle me-2"></i>Dashboard Tour
            </li>
            <li class="help-menu-item" data-action="glossary">
              <i class="bi bi-book me-2"></i>Levy Glossary
            </li>
            <li class="help-menu-item" data-action="faq">
              <i class="bi bi-question-circle me-2"></i>FAQ
            </li>
            <li class="help-menu-item" data-action="documentation">
              <i class="bi bi-file-text me-2"></i>User Guide
            </li>
            <li class="help-menu-item" data-action="support">
              <i class="bi bi-headset me-2"></i>Contact Support
            </li>
          </ul>
        </div>
      `;
      
      document.body.appendChild(helpMenu);
      
      // Add click events to help menu items
      const helpMenuItems = helpMenu.querySelectorAll('.help-menu-item');
      helpMenuItems.forEach(item => {
        item.addEventListener('click', function() {
          const tour = this.getAttribute('data-tour');
          const action = this.getAttribute('data-action');
          
          if (tour) {
            window.location.href = "/guided-tour/" + tour;
            helpMenu.classList.remove('active');
          }
          
          if (action) {
            handleHelpAction(action);
            helpMenu.classList.remove('active');
          }
        });
      });
    }
    
    // Add click event to help button
    helpButton.addEventListener('click', function(e) {
      e.preventDefault();
      helpMenu.classList.toggle('active');
    });
    
    // Close help menu when clicking outside
    document.addEventListener('click', function(event) {
      if (helpMenu.classList.contains('active') && 
          !helpMenu.contains(event.target) && 
          !helpButton.contains(event.target)) {
        helpMenu.classList.remove('active');
      }
    });
  }
  
  console.log('Help menu initialized successfully');
}

/**
 * Handle help menu actions
 * @param {string} action - The action to perform
 */
function handleHelpAction(action) {
  switch(action) {
    case 'glossary':
      window.location.href = '/glossary';
      break;
    case 'faq':
      window.location.href = '/faq';
      break;
    case 'documentation':
      window.location.href = '/help';
      break;
    case 'support':
      window.location.href = '/support';
      break;
    default:
      console.log('Unknown help action:', action);
  }
}

/**
 * Initialize the guided tour functionality
 */
function initializeGuidedTour() {
  console.log('Guided Tour System initialized');
  
  // Check if IntroJS is available
  if (typeof introJs === 'function') {
    // Get all tour trigger elements
    const tourTriggers = document.querySelectorAll('[data-tour]');
    
    tourTriggers.forEach(trigger => {
      trigger.addEventListener('click', function() {
        const tourName = this.getAttribute('data-tour');
        window.location.href = "/guided-tour/" + tourName;
      });
    });
  } else {
    console.log('IntroJS not available');
  }
}

/**
 * This function is now moved to guided_tour.js to avoid duplication
 * We're just handling the redirection here
 */
