/**
 * TerraFusion Workflow Management System
 * 
 * This module provides standardized workflow handling for all TerraFusion applications.
 * It manages multi-step processes, data flow visualization, and contextual help.
 */

class TerraFusionWorkflow {
  /**
   * Initialize a new workflow.
   * @param {Object} options - Configuration options
   * @param {string} options.containerId - ID of the container element
   * @param {Array} options.steps - Array of step definitions
   * @param {Function} options.onStepChange - Callback when step changes
   * @param {Function} options.onComplete - Callback when workflow completes
   * @param {boolean} options.persistState - Whether to persist state in sessionStorage
   */
  constructor(options) {
    this.containerId = options.containerId;
    this.steps = options.steps || [];
    this.currentStepIndex = 0;
    this.onStepChange = options.onStepChange || function() {};
    this.onComplete = options.onComplete || function() {};
    this.persistState = options.persistState || false;
    this.stateKey = `tf-workflow-${this.containerId}`;
    this.data = {};
    
    // Initialize the workflow
    this.init();
  }
  
  /**
   * Initialize the workflow UI and state.
   */
  init() {
    // Get the container element
    this.container = document.getElementById(this.containerId);
    if (!this.container) {
      console.error(`Workflow container #${this.containerId} not found`);
      return;
    }
    
    // Restore state if enabled
    if (this.persistState) {
      this.restoreState();
    }
    
    // Generate the workflow UI
    this.renderWorkflow();
    
    // Set up event listeners
    this.setupEventListeners();
    
    // Show the current step
    this.showStep(this.currentStepIndex);
    
    console.log(`TerraFusion Workflow initialized with ${this.steps.length} steps`);
  }
  
  /**
   * Render the workflow UI
   */
  renderWorkflow() {
    // Create workflow header with steps
    const stepsWrapper = document.createElement('div');
    stepsWrapper.className = 'tf-workflow-stepper';
    
    // Create each step indicator
    this.steps.forEach((step, index) => {
      const stepElement = document.createElement('div');
      stepElement.className = 'tf-workflow-step';
      stepElement.dataset.step = index;
      
      if (index < this.currentStepIndex) {
        stepElement.classList.add('completed');
      } else if (index === this.currentStepIndex) {
        stepElement.classList.add('active');
      }
      
      // Create step indicator (circle with number)
      const indicator = document.createElement('div');
      indicator.className = 'tf-step-indicator';
      indicator.textContent = index + 1;
      
      // Create step label
      const label = document.createElement('div');
      label.className = 'tf-step-label';
      label.textContent = step.title;
      
      // Assemble the step
      stepElement.appendChild(indicator);
      stepElement.appendChild(label);
      stepsWrapper.appendChild(stepElement);
    });
    
    // Create container for step content
    const contentWrapper = document.createElement('div');
    contentWrapper.className = 'tf-workflow-content';
    
    // Create each step's content container
    this.steps.forEach((step, index) => {
      const stepContent = document.createElement('div');
      stepContent.className = 'tf-step-content';
      stepContent.id = `step-${index}-content`;
      stepContent.innerHTML = step.content || '';
      
      // Create navigation buttons
      const navigation = document.createElement('div');
      navigation.className = 'tf-workflow-navigation mt-4 d-flex justify-content-between';
      
      // Back button (hidden for first step)
      const backButton = document.createElement('button');
      backButton.type = 'button';
      backButton.className = 'tf-btn tf-btn-outline tf-workflow-back';
      backButton.innerHTML = '<i class="bi bi-arrow-left me-2"></i>Back';
      if (index === 0) {
        backButton.style.visibility = 'hidden';
      }
      
      // Next/Complete button
      const nextButton = document.createElement('button');
      nextButton.type = 'button';
      nextButton.className = 'tf-btn tf-btn-primary tf-workflow-next';
      
      if (index === this.steps.length - 1) {
        nextButton.innerHTML = '<i class="bi bi-check2 me-2"></i>Complete';
        nextButton.classList.add('tf-workflow-complete');
      } else {
        nextButton.innerHTML = 'Next<i class="bi bi-arrow-right ms-2"></i>';
      }
      
      // Add the buttons to the navigation
      navigation.appendChild(backButton);
      navigation.appendChild(nextButton);
      
      // Add navigation to the step content
      stepContent.appendChild(navigation);
      
      // Add the step content to the wrapper
      contentWrapper.appendChild(stepContent);
    });
    
    // Add progress tracking
    const progressTracking = document.createElement('div');
    progressTracking.className = 'tf-workflow-progress mt-3';
    progressTracking.innerHTML = `
      <div class="progress" style="height: 6px;">
        <div class="progress-bar tf-bg-primary" role="progressbar" style="width: ${(this.currentStepIndex / (this.steps.length - 1)) * 100}%"></div>
      </div>
      <div class="d-flex justify-content-between mt-2">
        <small class="text-muted">Step ${this.currentStepIndex + 1} of ${this.steps.length}</small>
        <small class="text-muted tf-workflow-time"></small>
      </div>
    `;
    
    // Clear the container and add our elements
    this.container.innerHTML = '';
    this.container.appendChild(stepsWrapper);
    this.container.appendChild(contentWrapper);
    this.container.appendChild(progressTracking);
    
    // Update time estimate
    this.updateTimeEstimate();
  }
  
  /**
   * Set up event listeners for workflow navigation
   */
  setupEventListeners() {
    // Next button click
    const nextButtons = this.container.querySelectorAll('.tf-workflow-next');
    nextButtons.forEach(button => {
      button.addEventListener('click', () => {
        if (this.validateCurrentStep()) {
          if (button.classList.contains('tf-workflow-complete')) {
            this.completeWorkflow();
          } else {
            this.nextStep();
          }
        }
      });
    });
    
    // Back button click
    const backButtons = this.container.querySelectorAll('.tf-workflow-back');
    backButtons.forEach(button => {
      button.addEventListener('click', () => {
        this.previousStep();
      });
    });
    
    // Step indicator click (for direct navigation if allowed)
    const stepIndicators = this.container.querySelectorAll('.tf-workflow-step');
    stepIndicators.forEach(step => {
      step.addEventListener('click', (e) => {
        const clickedStep = parseInt(step.dataset.step, 10);
        // Only allow clicking on completed steps or the next step
        if (clickedStep < this.currentStepIndex || clickedStep === this.currentStepIndex + 1) {
          if (this.validateCurrentStep() || clickedStep < this.currentStepIndex) {
            this.goToStep(clickedStep);
          }
        }
      });
    });
  }
  
  /**
   * Validate the current step before proceeding
   * @return {boolean} True if validation passes, false otherwise
   */
  validateCurrentStep() {
    const currentStep = this.steps[this.currentStepIndex];
    
    // If the step has a validate function, call it
    if (currentStep.validate && typeof currentStep.validate === 'function') {
      const stepData = this.collectStepData();
      return currentStep.validate(stepData);
    }
    
    // Default to valid if no validation function is provided
    return true;
  }
  
  /**
   * Collect data from the current step
   * @return {Object} Data collected from the current step
   */
  collectStepData() {
    const currentStep = this.steps[this.currentStepIndex];
    const stepContent = document.getElementById(`step-${this.currentStepIndex}-content`);
    
    // If the step has a collectData function, call it
    if (currentStep.collectData && typeof currentStep.collectData === 'function') {
      const stepData = currentStep.collectData(stepContent);
      
      // Merge the step data into the main data object
      this.data = { ...this.data, ...stepData };
      
      // Save state if enabled
      if (this.persistState) {
        this.saveState();
      }
      
      return stepData;
    }
    
    // Default collect form data if no specific collection function
    const formData = {};
    const formElements = stepContent.querySelectorAll('input, select, textarea');
    
    formElements.forEach(element => {
      if (element.id) {
        if (element.type === 'checkbox') {
          formData[element.id] = element.checked;
        } else if (element.type === 'radio') {
          if (element.checked) {
            formData[element.name] = element.value;
          }
        } else {
          formData[element.id] = element.value;
        }
      }
    });
    
    // Merge the form data into the main data object
    this.data = { ...this.data, ...formData };
    
    // Save state if enabled
    if (this.persistState) {
      this.saveState();
    }
    
    return formData;
  }
  
  /**
   * Move to the next step in the workflow
   */
  nextStep() {
    if (this.currentStepIndex < this.steps.length - 1) {
      this.goToStep(this.currentStepIndex + 1);
    }
  }
  
  /**
   * Move to the previous step in the workflow
   */
  previousStep() {
    if (this.currentStepIndex > 0) {
      this.goToStep(this.currentStepIndex - 1);
    }
  }
  
  /**
   * Go to a specific step in the workflow
   * @param {number} stepIndex - Index of the step to go to
   */
  goToStep(stepIndex) {
    if (stepIndex >= 0 && stepIndex < this.steps.length) {
      // Hide current step
      this.hideStep(this.currentStepIndex);
      
      // Update current step index
      this.currentStepIndex = stepIndex;
      
      // Show new step
      this.showStep(this.currentStepIndex);
      
      // Update progress
      this.updateProgress();
      
      // Call step change callback
      this.onStepChange(this.currentStepIndex, this.data);
      
      // Save state if enabled
      if (this.persistState) {
        this.saveState();
      }
    }
  }
  
  /**
   * Show a specific step
   * @param {number} stepIndex - Index of the step to show
   */
  showStep(stepIndex) {
    // Update step indicators
    const stepIndicators = this.container.querySelectorAll('.tf-workflow-step');
    stepIndicators.forEach((step, index) => {
      step.classList.remove('active');
      
      if (index < stepIndex) {
        step.classList.add('completed');
        step.classList.remove('active');
      } else if (index === stepIndex) {
        step.classList.add('active');
        step.classList.remove('completed');
      } else {
        step.classList.remove('completed');
      }
    });
    
    // Show step content
    const stepContent = document.getElementById(`step-${stepIndex}-content`);
    if (stepContent) {
      stepContent.classList.add('active');
    }
    
    // Initialize step if it has an init function
    const step = this.steps[stepIndex];
    if (step.init && typeof step.init === 'function') {
      step.init(stepContent, this.data);
    }
  }
  
  /**
   * Hide a specific step
   * @param {number} stepIndex - Index of the step to hide
   */
  hideStep(stepIndex) {
    const stepContent = document.getElementById(`step-${stepIndex}-content`);
    if (stepContent) {
      stepContent.classList.remove('active');
    }
  }
  
  /**
   * Update the progress indicator
   */
  updateProgress() {
    const progressBar = this.container.querySelector('.progress-bar');
    const stepCounter = this.container.querySelector('.tf-workflow-progress small:first-child');
    
    if (progressBar) {
      progressBar.style.width = `${(this.currentStepIndex / (this.steps.length - 1)) * 100}%`;
    }
    
    if (stepCounter) {
      stepCounter.textContent = `Step ${this.currentStepIndex + 1} of ${this.steps.length}`;
    }
    
    this.updateTimeEstimate();
  }
  
  /**
   * Update the time estimate for completion
   */
  updateTimeEstimate() {
    const timeElement = this.container.querySelector('.tf-workflow-time');
    if (!timeElement) return;
    
    const remainingSteps = this.steps.length - this.currentStepIndex - 1;
    
    if (remainingSteps <= 0) {
      timeElement.textContent = 'Almost done!';
      return;
    }
    
    // Calculate estimated time based on remaining steps
    // Assume average of 2 minutes per step (adjust as needed)
    const minutesRemaining = remainingSteps * 2;
    
    if (minutesRemaining < 1) {
      timeElement.textContent = 'Less than a minute remaining';
    } else if (minutesRemaining === 1) {
      timeElement.textContent = 'About 1 minute remaining';
    } else if (minutesRemaining < 60) {
      timeElement.textContent = `About ${minutesRemaining} minutes remaining`;
    } else {
      const hours = Math.floor(minutesRemaining / 60);
      const minutes = minutesRemaining % 60;
      timeElement.textContent = `About ${hours} hour${hours > 1 ? 's' : ''} ${minutes > 0 ? `and ${minutes} minute${minutes > 1 ? 's' : ''}` : ''} remaining`;
    }
  }
  
  /**
   * Complete the workflow
   */
  completeWorkflow() {
    // Collect data from the final step
    this.collectStepData();
    
    // Call the completion callback with the collected data
    this.onComplete(this.data);
    
    // Clear state if enabled
    if (this.persistState) {
      this.clearState();
    }
  }
  
  /**
   * Save the current workflow state to sessionStorage
   */
  saveState() {
    if (!window.sessionStorage) return;
    
    const state = {
      currentStepIndex: this.currentStepIndex,
      data: this.data
    };
    
    sessionStorage.setItem(this.stateKey, JSON.stringify(state));
  }
  
  /**
   * Restore the workflow state from sessionStorage
   */
  restoreState() {
    if (!window.sessionStorage) return;
    
    const savedState = sessionStorage.getItem(this.stateKey);
    if (savedState) {
      try {
        const state = JSON.parse(savedState);
        this.currentStepIndex = state.currentStepIndex || 0;
        this.data = state.data || {};
      } catch (e) {
        console.error('Error restoring workflow state:', e);
      }
    }
  }
  
  /**
   * Clear the saved workflow state
   */
  clearState() {
    if (!window.sessionStorage) return;
    sessionStorage.removeItem(this.stateKey);
  }
  
  /**
   * Reset the workflow to the first step
   */
  reset() {
    this.currentStepIndex = 0;
    this.data = {};
    this.clearState();
    this.renderWorkflow();
    this.setupEventListeners();
    this.showStep(0);
  }
  
  /**
   * Get the current workflow data
   * @return {Object} Current workflow data
   */
  getData() {
    return { ...this.data };
  }
  
  /**
   * Set workflow data (for pre-filling)
   * @param {Object} data - Data to set
   */
  setData(data) {
    this.data = { ...data };
    
    // If we're on a step, refresh it with the new data
    const currentStep = this.steps[this.currentStepIndex];
    const stepContent = document.getElementById(`step-${this.currentStepIndex}-content`);
    
    if (currentStep && currentStep.init && stepContent) {
      currentStep.init(stepContent, this.data);
    }
    
    if (this.persistState) {
      this.saveState();
    }
  }
}

/**
 * Data Flow Visualization Component
 * Visualizes the flow of data through a multi-step process
 */
class TerraFusionDataFlow {
  /**
   * Initialize a new data flow visualization
   * @param {Object} options - Configuration options
   * @param {string} options.containerId - ID of the container element
   * @param {Array} options.steps - Array of step definitions
   * @param {number} options.activeStep - Index of currently active step
   */
  constructor(options) {
    this.containerId = options.containerId;
    this.steps = options.steps || [];
    this.activeStep = options.activeStep || 0;
    
    this.init();
  }
  
  /**
   * Initialize the data flow visualization
   */
  init() {
    this.container = document.getElementById(this.containerId);
    if (!this.container) {
      console.error(`Data flow container #${this.containerId} not found`);
      return;
    }
    
    this.render();
  }
  
  /**
   * Render the data flow visualization
   */
  render() {
    this.container.innerHTML = '';
    this.container.className = 'tf-data-flow';
    
    this.steps.forEach((step, index) => {
      const stepElement = document.createElement('div');
      stepElement.className = 'tf-data-flow-step';
      
      if (index < this.activeStep) {
        stepElement.classList.add('completed');
      } else if (index === this.activeStep) {
        stepElement.classList.add('active');
      }
      
      // Icon
      const icon = document.createElement('div');
      icon.className = 'tf-data-flow-icon';
      icon.innerHTML = step.icon || '<i class="bi bi-arrow-right"></i>';
      
      // Content
      const content = document.createElement('div');
      content.className = 'tf-data-flow-content';
      
      const title = document.createElement('h5');
      title.className = 'tf-data-flow-title';
      title.textContent = step.title;
      
      const description = document.createElement('p');
      description.className = 'tf-data-flow-description';
      description.textContent = step.description;
      
      content.appendChild(title);
      content.appendChild(description);
      
      // Status indicator
      const status = document.createElement('div');
      status.className = 'tf-data-flow-status';
      
      let statusClass = 'tf-process-status';
      let statusIcon = '';
      let statusText = '';
      
      if (index < this.activeStep) {
        statusClass += ' tf-process-status-completed';
        statusIcon = '<i class="bi bi-check-circle tf-process-status-icon"></i>';
        statusText = 'Completed';
      } else if (index === this.activeStep) {
        statusClass += ' tf-process-status-processing';
        statusIcon = '<i class="bi bi-arrow-repeat tf-process-status-icon"></i>';
        statusText = 'Processing';
      } else {
        statusClass += ' tf-process-status-pending';
        statusIcon = '<i class="bi bi-clock tf-process-status-icon"></i>';
        statusText = 'Pending';
      }
      
      status.className = statusClass;
      status.innerHTML = `${statusIcon}${statusText}`;
      
      // Assemble the step
      stepElement.appendChild(icon);
      stepElement.appendChild(content);
      stepElement.appendChild(status);
      this.container.appendChild(stepElement);
    });
  }
  
  /**
   * Update the active step
   * @param {number} stepIndex - Index of the step to set as active
   */
  setActiveStep(stepIndex) {
    if (stepIndex >= 0 && stepIndex < this.steps.length) {
      this.activeStep = stepIndex;
      this.render();
    }
  }
  
  /**
   * Move to the next step
   */
  nextStep() {
    if (this.activeStep < this.steps.length - 1) {
      this.activeStep++;
      this.render();
    }
  }
  
  /**
   * Set a step's status directly
   * @param {number} stepIndex - Index of the step to update
   * @param {string} status - Status to set ('pending', 'processing', 'completed', 'error')
   */
  setStepStatus(stepIndex, status) {
    if (stepIndex >= 0 && stepIndex < this.steps.length) {
      const stepElement = this.container.children[stepIndex];
      if (!stepElement) return;
      
      const statusElement = stepElement.querySelector('.tf-data-flow-status');
      if (!statusElement) return;
      
      // Remove all status classes
      statusElement.classList.remove(
        'tf-process-status-pending',
        'tf-process-status-processing',
        'tf-process-status-completed',
        'tf-process-status-error'
      );
      
      // Add the appropriate class
      statusElement.classList.add(`tf-process-status-${status}`);
      
      // Update icon and text
      let statusIcon = '';
      let statusText = '';
      
      switch (status) {
        case 'pending':
          statusIcon = '<i class="bi bi-clock tf-process-status-icon"></i>';
          statusText = 'Pending';
          break;
        case 'processing':
          statusIcon = '<i class="bi bi-arrow-repeat tf-process-status-icon"></i>';
          statusText = 'Processing';
          break;
        case 'completed':
          statusIcon = '<i class="bi bi-check-circle tf-process-status-icon"></i>';
          statusText = 'Completed';
          break;
        case 'error':
          statusIcon = '<i class="bi bi-exclamation-circle tf-process-status-icon"></i>';
          statusText = 'Error';
          break;
      }
      
      statusElement.innerHTML = `${statusIcon}${statusText}`;
    }
  }
}

/**
 * Contextual Help System
 * Provides contextual help throughout the application
 */
class TerraFusionHelp {
  /**
   * Initialize the contextual help system
   */
  constructor() {
    this.tooltips = {};
    this.activeTooltip = null;
    
    this.init();
  }
  
  /**
   * Initialize the help system
   */
  init() {
    this.initTooltipTriggers();
    
    // Close tooltips when clicking outside
    document.addEventListener('click', (e) => {
      if (this.activeTooltip && !e.target.classList.contains('tf-help-trigger')) {
        this.hideTooltip(this.activeTooltip);
      }
    });
  }
  
  /**
   * Initialize tooltip triggers
   */
  initTooltipTriggers() {
    const triggers = document.querySelectorAll('.tf-help-trigger');
    
    triggers.forEach(trigger => {
      // Get the tooltip content from data attribute
      const content = trigger.dataset.help;
      const position = trigger.dataset.position || 'top';
      
      if (!content) return;
      
      // Create tooltip if it doesn't exist
      if (!this.tooltips[trigger.id]) {
        this.createTooltip(trigger.id, content, position);
      }
      
      // Add click event
      trigger.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        // If this tooltip is active, hide it
        if (this.activeTooltip === trigger.id) {
          this.hideTooltip(trigger.id);
        } else {
          // Hide any active tooltip
          if (this.activeTooltip) {
            this.hideTooltip(this.activeTooltip);
          }
          
          // Show this tooltip
          this.showTooltip(trigger.id);
        }
      });
    });
  }
  
  /**
   * Create a tooltip
   * @param {string} id - ID of the tooltip trigger
   * @param {string} content - Content for the tooltip
   * @param {string} position - Position of the tooltip (top, bottom, left, right)
   */
  createTooltip(id, content, position) {
    const trigger = document.getElementById(id);
    if (!trigger) return;
    
    // Create tooltip element
    const tooltip = document.createElement('div');
    tooltip.className = `tf-tooltip ${position}`;
    tooltip.innerHTML = content;
    
    // Add to page
    document.body.appendChild(tooltip);
    
    // Store reference
    this.tooltips[id] = {
      element: tooltip,
      trigger: trigger,
      position: position
    };
  }
  
  /**
   * Show a tooltip
   * @param {string} id - ID of the tooltip trigger
   */
  showTooltip(id) {
    const tooltip = this.tooltips[id];
    if (!tooltip) return;
    
    // Position the tooltip
    this.positionTooltip(id);
    
    // Show the tooltip
    tooltip.element.classList.add('show');
    
    // Set as active
    this.activeTooltip = id;
  }
  
  /**
   * Hide a tooltip
   * @param {string} id - ID of the tooltip trigger
   */
  hideTooltip(id) {
    const tooltip = this.tooltips[id];
    if (!tooltip) return;
    
    // Hide the tooltip
    tooltip.element.classList.remove('show');
    
    // Clear active
    if (this.activeTooltip === id) {
      this.activeTooltip = null;
    }
  }
  
  /**
   * Position a tooltip relative to its trigger
   * @param {string} id - ID of the tooltip trigger
   */
  positionTooltip(id) {
    const tooltip = this.tooltips[id];
    if (!tooltip) return;
    
    const triggerRect = tooltip.trigger.getBoundingClientRect();
    const tooltipRect = tooltip.element.getBoundingClientRect();
    
    let top = 0;
    let left = 0;
    
    // Position based on specified position
    switch (tooltip.position) {
      case 'top':
        top = triggerRect.top - tooltipRect.height - 10;
        left = triggerRect.left + (triggerRect.width / 2) - (tooltipRect.width / 2);
        break;
      case 'bottom':
        top = triggerRect.bottom + 10;
        left = triggerRect.left + (triggerRect.width / 2) - (tooltipRect.width / 2);
        break;
      case 'left':
        top = triggerRect.top + (triggerRect.height / 2) - (tooltipRect.height / 2);
        left = triggerRect.left - tooltipRect.width - 10;
        break;
      case 'right':
        top = triggerRect.top + (triggerRect.height / 2) - (tooltipRect.height / 2);
        left = triggerRect.right + 10;
        break;
    }
    
    // Keep tooltip in viewport
    if (left < 0) left = 0;
    if (top < 0) top = 0;
    if (left + tooltipRect.width > window.innerWidth) {
      left = window.innerWidth - tooltipRect.width;
    }
    if (top + tooltipRect.height > window.innerHeight) {
      top = window.innerHeight - tooltipRect.height;
    }
    
    // Set position
    tooltip.element.style.top = `${top}px`;
    tooltip.element.style.left = `${left}px`;
  }
  
  /**
   * Register global help topics
   * @param {Object} topics - Object mapping topic keys to content
   */
  registerTopics(topics) {
    this.topics = topics || {};
  }
  
  /**
   * Show a help topic in a modal
   * @param {string} topicKey - Key of the help topic to show
   */
  showTopic(topicKey) {
    if (!this.topics || !this.topics[topicKey]) return;
    
    const topic = this.topics[topicKey];
    
    // Check if Bootstrap modal is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
      // Create modal if it doesn't exist
      let helpModal = document.getElementById('tf-help-modal');
      
      if (!helpModal) {
        const modalHtml = `
          <div class="modal fade" id="tf-help-modal" tabindex="-1" aria-labelledby="tf-help-modal-title" aria-hidden="true">
            <div class="modal-dialog modal-lg">
              <div class="modal-content">
                <div class="modal-header">
                  <h5 class="modal-title" id="tf-help-modal-title"></h5>
                  <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                </div>
                <div class="modal-footer">
                  <button type="button" class="tf-btn tf-btn-outline" data-bs-dismiss="modal">Close</button>
                </div>
              </div>
            </div>
          </div>
        `;
        
        const modalContainer = document.createElement('div');
        modalContainer.innerHTML = modalHtml;
        document.body.appendChild(modalContainer.firstChild);
        
        helpModal = document.getElementById('tf-help-modal');
      }
      
      // Set content
      const modalTitle = helpModal.querySelector('.modal-title');
      const modalBody = helpModal.querySelector('.modal-body');
      
      modalTitle.textContent = topic.title || 'Help';
      modalBody.innerHTML = topic.content || '';
      
      // Show modal
      const modal = new bootstrap.Modal(helpModal);
      modal.show();
    } else {
      // Fallback to alert for simple cases
      alert(`${topic.title || 'Help'}\n\n${topic.content.replace(/<[^>]*>/g, '')}`);
    }
  }
}

/**
 * Task Suggestion System
 * Provides contextual task suggestions based on current workflow
 */
class TerraFusionTaskSuggestions {
  /**
   * Initialize the task suggestion system
   * @param {Object} options - Configuration options
   * @param {string} options.containerId - ID of the container element
   * @param {Array} options.tasks - Array of task definitions
   * @param {Function} options.onSelect - Callback when a task is selected
   */
  constructor(options) {
    this.containerId = options.containerId;
    this.tasks = options.tasks || [];
    this.onSelect = options.onSelect || function() {};
    
    this.init();
  }
  
  /**
   * Initialize the task suggestion system
   */
  init() {
    this.container = document.getElementById(this.containerId);
    if (!this.container) {
      console.error(`Task suggestion container #${this.containerId} not found`);
      return;
    }
    
    this.render();
  }
  
  /**
   * Render the task suggestions
   */
  render() {
    this.container.innerHTML = '';
    this.container.className = 'tf-task-suggestions';
    
    this.tasks.forEach(task => {
      const taskElement = document.createElement('a');
      taskElement.href = task.url || '#';
      taskElement.className = 'tf-task-card';
      taskElement.dataset.taskId = task.id;
      
      // Prevent navigation if no URL
      if (!task.url) {
        taskElement.addEventListener('click', (e) => {
          e.preventDefault();
          this.onSelect(task);
        });
      }
      
      // Icon
      const icon = document.createElement('div');
      icon.className = 'tf-task-icon';
      icon.innerHTML = task.icon || '<i class="bi bi-lightning"></i>';
      
      // Title
      const title = document.createElement('h5');
      title.className = 'tf-task-title';
      title.textContent = task.title;
      
      // Description
      const description = document.createElement('p');
      description.className = 'tf-task-description';
      description.textContent = task.description;
      
      // Assemble the task card
      taskElement.appendChild(icon);
      taskElement.appendChild(title);
      taskElement.appendChild(description);
      
      this.container.appendChild(taskElement);
    });
  }
  
  /**
   * Update the tasks based on context
   * @param {Object} context - Current application context
   */
  updateTasks(context) {
    // Filter tasks based on context
    const filteredTasks = this.tasks.filter(task => {
      if (!task.contexts || task.contexts.length === 0) {
        return true; // No context restrictions
      }
      
      // Check if any context matches
      return task.contexts.some(taskContext => {
        // Match context keys
        return Object.keys(taskContext).every(key => {
          if (!(key in context)) {
            return false;
          }
          
          // Check value
          if (Array.isArray(taskContext[key])) {
            return taskContext[key].includes(context[key]);
          } else {
            return taskContext[key] === context[key];
          }
        });
      });
    });
    
    // Sort tasks by priority
    filteredTasks.sort((a, b) => (b.priority || 0) - (a.priority || 0));
    
    // Update displayed tasks
    this.tasks = filteredTasks;
    this.render();
  }
  
  /**
   * Get the current task suggestions
   * @return {Array} Current task suggestions
   */
  getTasks() {
    return [...this.tasks];
  }
}

// Make classes available globally
window.TerraFusionWorkflow = TerraFusionWorkflow;
window.TerraFusionDataFlow = TerraFusionDataFlow;
window.TerraFusionHelp = TerraFusionHelp;
window.TerraFusionTaskSuggestions = TerraFusionTaskSuggestions;

// Initialize help system
document.addEventListener('DOMContentLoaded', () => {
  window.terraFusionHelp = new TerraFusionHelp();
  console.log('TerraFusion Workflow Management System initialized');
});