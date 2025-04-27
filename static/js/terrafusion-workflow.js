/**
 * TerraFusion Workflow JavaScript
 * 
 * Handles consistent workflow logic, data processing, and UI interactions
 * for the TerraFusion platform.
 */

// Initialize Terra Fusion workflow system
document.addEventListener('DOMContentLoaded', function() {
  console.log('TerraFusion Workflow JS initialized');
  initializeWorkflowComponents();
});

/**
 * Initialize all workflow components on the page
 */
function initializeWorkflowComponents() {
  // Initialize workflow steppers
  initializeWorkflowSteppers();
  
  // Initialize data flow visualizations
  initializeDataFlowVisualization();
  
  // Initialize help context tooltips
  initializeHelpContext();
  
  // Initialize task suggestion cards
  initializeTaskSuggestions();
  
  // Initialize process status indicators
  initializeProcessStatus();
}

/**
 * Initialize workflow steppers on the page
 */
function initializeWorkflowSteppers() {
  const steppers = document.querySelectorAll('.tf-workflow-stepper');
  if (steppers.length === 0) return;
  
  steppers.forEach(stepper => {
    const steps = stepper.querySelectorAll('.tf-workflow-step');
    
    // Add click handlers to steps if they are completed
    steps.forEach((step, index) => {
      if (step.classList.contains('completed')) {
        step.style.cursor = 'pointer';
        
        step.addEventListener('click', function() {
          // Find active step
          const activeStep = stepper.querySelector('.tf-workflow-step.active');
          if (activeStep) {
            // Check if we need to navigate
            const currentIndex = Array.from(steps).indexOf(activeStep);
            if (index < currentIndex) {
              // Trigger navigation event
              const event = new CustomEvent('terraFusion:workflowStepChange', {
                detail: {
                  from: currentIndex,
                  to: index,
                  stepElement: step
                }
              });
              document.dispatchEvent(event);
            }
          }
        });
      }
    });
  });
}

/**
 * Initialize data flow visualizations on the page
 */
function initializeDataFlowVisualization() {
  const dataFlows = document.querySelectorAll('.tf-data-flow');
  if (dataFlows.length === 0) return;
  
  dataFlows.forEach(dataFlow => {
    const steps = dataFlow.querySelectorAll('.tf-data-flow-step');
    
    // Add click handlers to steps
    steps.forEach((step, index) => {
      // Only allow interaction with completed or active steps
      if (step.classList.contains('completed') || step.classList.contains('active')) {
        step.style.cursor = 'pointer';
        
        step.addEventListener('click', function() {
          // Find active step
          const activeStep = dataFlow.querySelector('.tf-data-flow-step.active');
          if (activeStep) {
            // Get current active index
            const currentIndex = Array.from(steps).indexOf(activeStep);
            
            // Only allow going backwards in the flow or clicking the current step
            if (index <= currentIndex) {
              // Remove active class from current step
              activeStep.classList.remove('active');
              
              // Add active class to clicked step
              step.classList.add('active');
              
              // Trigger data flow step change event
              const event = new CustomEvent('terraFusion:dataFlowStepChange', {
                detail: {
                  from: currentIndex,
                  to: index,
                  stepElement: step
                }
              });
              document.dispatchEvent(event);
            }
          }
        });
      }
    });
  });
}

/**
 * Initialize help context tooltips on the page
 */
function initializeHelpContext() {
  const helpContextElements = document.querySelectorAll('.tf-help-context');
  if (helpContextElements.length === 0) return;
  
  helpContextElements.forEach(element => {
    // Add click handler for context help mode
    element.addEventListener('click', function(e) {
      if (document.body.classList.contains('show-context-help')) {
        e.preventDefault();
        
        // Get id from element
        const helpId = element.getAttribute('id');
        
        // If we have a help system with registered topics, use it
        if (window.terraFusionHelp && window.terraFusionHelp.showHelpModal) {
          // Extract topic id from the element id
          const topicId = helpId.replace('help', '').toLowerCase();
          window.terraFusionHelp.showHelpModal(topicId);
        } else {
          // Fallback to tooltip
          const title = element.getAttribute('data-title') || '';
          const content = element.getAttribute('data-content') || '';
          
          if (title || content) {
            showNotification(title, content, 'info', 8000);
          }
        }
      }
    });
  });
  
  // Toggle context help mode button (if exists)
  const contextHelpBtn = document.getElementById('toggleContextHelp');
  if (contextHelpBtn) {
    contextHelpBtn.addEventListener('click', function() {
      document.body.classList.toggle('show-context-help');
      
      if (document.body.classList.contains('show-context-help')) {
        showNotification('Context Help Mode', 'Click on any help icon to see more information', 'info');
      } else {
        showNotification('Context Help Mode Disabled', 'Help mode has been turned off', 'info');
      }
    });
  }
}

/**
 * Initialize task suggestion cards on the page
 */
function initializeTaskSuggestions() {
  const taskCards = document.querySelectorAll('.tf-task-card');
  if (taskCards.length === 0) return;
  
  taskCards.forEach(card => {
    card.addEventListener('click', function(e) {
      // Check if the card has a specific action
      const action = card.getAttribute('data-action');
      
      if (action && e.target.tagName !== 'A') {
        e.preventDefault();
        
        // Trigger task action event
        const event = new CustomEvent('terraFusion:taskAction', {
          detail: {
            action: action,
            cardElement: card
          }
        });
        document.dispatchEvent(event);
      }
    });
  });
}

/**
 * Initialize process status indicators on the page
 */
function initializeProcessStatus() {
  // Add animation to processing status icons
  const processingIcons = document.querySelectorAll('.tf-process-status-processing .tf-process-status-icon');
  
  processingIcons.forEach(icon => {
    if (icon.classList.contains('bi-arrow-repeat')) {
      icon.style.animation = 'spin 1.5s linear infinite';
    }
  });
}

/**
 * Workflow Navigation Functions
 */

/**
 * Navigate to a specific step in a workflow
 * 
 * @param {string} workflowId - The ID of the workflow container
 * @param {number} stepIndex - The index of the step to navigate to (0-based)
 */
function navigateToStep(workflowId, stepIndex) {
  const workflowContainer = document.getElementById(workflowId);
  if (!workflowContainer) return;
  
  const stepper = workflowContainer.querySelector('.tf-workflow-stepper');
  if (!stepper) return;
  
  const steps = stepper.querySelectorAll('.tf-workflow-step');
  if (stepIndex < 0 || stepIndex >= steps.length) return;
  
  // Find current active step
  const activeStep = stepper.querySelector('.tf-workflow-step.active');
  if (activeStep) {
    // Get current index
    const currentIndex = Array.from(steps).indexOf(activeStep);
    
    // Only allow going to completed steps or the next step
    if (stepIndex < currentIndex || stepIndex === currentIndex + 1) {
      // Remove active class from current step
      activeStep.classList.remove('active');
      
      // Add active class to new step
      steps[stepIndex].classList.add('active');
      
      // Update step status classes
      steps.forEach((step, index) => {
        if (index < stepIndex) {
          step.classList.add('completed');
          step.classList.remove('active');
        } else if (index === stepIndex) {
          step.classList.add('active');
          step.classList.remove('completed');
        } else {
          step.classList.remove('active');
          step.classList.remove('completed');
        }
      });
      
      // Trigger step change event
      const event = new CustomEvent('terraFusion:workflowStepChange', {
        detail: {
          from: currentIndex,
          to: stepIndex,
          stepElement: steps[stepIndex]
        }
      });
      document.dispatchEvent(event);
      
      return true;
    }
  }
  
  return false;
}

/**
 * Move to the next step in a workflow
 * 
 * @param {string} workflowId - The ID of the workflow container
 * @returns {boolean} - Whether navigation was successful
 */
function navigateToNextStep(workflowId) {
  const workflowContainer = document.getElementById(workflowId);
  if (!workflowContainer) return false;
  
  const stepper = workflowContainer.querySelector('.tf-workflow-stepper');
  if (!stepper) return false;
  
  const steps = stepper.querySelectorAll('.tf-workflow-step');
  
  // Find current active step
  const activeStep = stepper.querySelector('.tf-workflow-step.active');
  if (activeStep) {
    // Get current index
    const currentIndex = Array.from(steps).indexOf(activeStep);
    
    // Check if we can go to next step
    if (currentIndex < steps.length - 1) {
      return navigateToStep(workflowId, currentIndex + 1);
    }
  }
  
  return false;
}

/**
 * Move to the previous step in a workflow
 * 
 * @param {string} workflowId - The ID of the workflow container
 * @returns {boolean} - Whether navigation was successful
 */
function navigateToPreviousStep(workflowId) {
  const workflowContainer = document.getElementById(workflowId);
  if (!workflowContainer) return false;
  
  const stepper = workflowContainer.querySelector('.tf-workflow-stepper');
  if (!stepper) return false;
  
  const steps = stepper.querySelectorAll('.tf-workflow-step');
  
  // Find current active step
  const activeStep = stepper.querySelector('.tf-workflow-step.active');
  if (activeStep) {
    // Get current index
    const currentIndex = Array.from(steps).indexOf(activeStep);
    
    // Check if we can go to previous step
    if (currentIndex > 0) {
      return navigateToStep(workflowId, currentIndex - 1);
    }
  }
  
  return false;
}

/**
 * Update the status of a process in a workflow
 * 
 * @param {string} processId - The ID of the process status element
 * @param {string} status - The new status (pending, processing, completed, error)
 * @param {string} details - Optional details text for the status
 */
function updateProcessStatus(processId, status, details = null) {
  const processElement = document.getElementById(processId);
  if (!processElement) return;
  
  // Remove all status classes
  processElement.classList.remove('tf-process-status-pending');
  processElement.classList.remove('tf-process-status-processing');
  processElement.classList.remove('tf-process-status-completed');
  processElement.classList.remove('tf-process-status-error');
  
  // Add the new status class
  processElement.classList.add(`tf-process-status-${status}`);
  
  // Update the icon
  const iconElement = processElement.querySelector('.tf-process-status-icon');
  if (iconElement) {
    iconElement.className = 'tf-process-status-icon bi';
    
    switch (status) {
      case 'pending':
        iconElement.classList.add('bi-clock');
        break;
      case 'processing':
        iconElement.classList.add('bi-arrow-repeat');
        iconElement.style.animation = 'spin 1.5s linear infinite';
        break;
      case 'completed':
        iconElement.classList.add('bi-check-circle');
        iconElement.style.animation = '';
        break;
      case 'error':
        iconElement.classList.add('bi-exclamation-triangle');
        iconElement.style.animation = '';
        break;
    }
  }
  
  // Update details if provided
  if (details !== null) {
    const detailsElement = processElement.querySelector('.tf-process-status-details');
    if (detailsElement) {
      detailsElement.textContent = details;
    } else {
      // Create details element if it doesn't exist
      const newDetailsElement = document.createElement('div');
      newDetailsElement.className = 'tf-process-status-details';
      newDetailsElement.textContent = details;
      processElement.appendChild(newDetailsElement);
    }
  }
}

/**
 * Event listeners and exports
 */
// Make functions available globally
window.terraFusionWorkflow = {
  navigateToStep,
  navigateToNextStep,
  navigateToPreviousStep,
  updateProcessStatus
};