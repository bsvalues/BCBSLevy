/**
 * guided_tour.js
 * 
 * This module provides functionality for the guided tour feature using Bootstrap Tooltips and Popovers.
 * It works with help_menu.js to provide contextual guided tours for different
 * sections of the application.
 */

// Global tour state
let tourActive = false;
let currentTourStep = 0;
let tourSteps = [];
let currentTourName = '';

// Initialize when the DOM is fully loaded with all resources
window.addEventListener('load', function() {
    console.log("Guided tour - window.load event fired");
    
    // Ensure demo button exists by injecting it if needed
    injectDemoButtonIfNeeded();
    
    setupTourButtons();
    console.log("Guided tour initialized from window.load");
});

// Also initialize when the DOM structure is loaded (earlier than window.load)
document.addEventListener('DOMContentLoaded', function() {
    console.log("Guided tour - DOMContentLoaded event fired");
    
    // Attempt early injection of demo button
    injectDemoButtonIfNeeded();
    
    // Attempt to setup early but don't rely on it fully
    setupTourButtons();
    console.log("Guided tour initialized from DOMContentLoaded");
});

/**
 * Injects the demo button into the DOM if it doesn't already exist
 */
function injectDemoButtonIfNeeded() {
    // Check if demo button already exists
    if (!document.getElementById('demoModeButton')) {
        console.log('Demo button not found, injecting it now');
        
        // Create the button element
        const demoButton = document.createElement('button');
        demoButton.id = 'demoModeButton';
        demoButton.className = 'demo-button-pulse';
        demoButton.title = 'Start guided tour';
        demoButton.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 9999; background-color: #3DA5BD; ' +
                            'color: white; border: none; border-radius: 50%; width: 60px; height: 60px; ' +
                            'display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(0,0,0,0.15); ' +
                            'cursor: pointer;';
        
        // Create the icon
        const icon = document.createElement('i');
        icon.className = 'bi bi-play-fill';
        icon.style.fontSize = '1.5rem';
        
        // Append icon to button
        demoButton.appendChild(icon);
        
        // Append button to body
        document.body.appendChild(demoButton);
        
        console.log('Demo button injected successfully');
    } else {
        console.log('Demo button already exists in the DOM');
    }
}

/**
 * Set up event listeners for tour-related buttons
 */
function setupTourButtons() {
    // Set up contact support functionality
    setupContactButtons();
    
    // Set up tour buttons in the navigation and help menu
    const tourButtons = document.querySelectorAll('[data-tour]');
    tourButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tourName = this.getAttribute('data-tour');
            startTour(tourName);
        });
    });
    
    // Try to set up demo button here as a fallback
    setupDemoButton();
}

/**
 * Set up the demo button click handler - this is now primarily handled in base.html
 * but we keep this as a fallback mechanism
 */
function setupDemoButton() {
    // Get the demo button from base.html
    const demoButton = document.getElementById('demoModeButton');
    
    // Set up the demo button if it exists and doesn't already have a click handler
    if (demoButton && !demoButton._hasGuidedTourHandler) {
        console.log('Setting up demo button handler from guided_tour.js');
        
        // Mark this button as having our handler
        demoButton._hasGuidedTourHandler = true;
        
        // Use addEventListener instead of direct onclick override to avoid conflicts
        demoButton.addEventListener('click', function(event) {
            // Prevent default behavior
            event.preventDefault();
            
            // Determine which tour to start based on the current page
            const currentPath = window.location.pathname;
            let tourName = 'general';
            
            if (currentPath.includes('/mcp/agent-registry')) {
                tourName = 'agent-registry';
            } else if (currentPath.includes('/mcp/workflow-designer')) {
                tourName = 'workflow-designer';
            } else if (currentPath.includes('/mcp/agent-playground')) {
                tourName = 'agent-playground';
            }
            
            console.log('Starting tour from guided_tour.js handler:', tourName);
            startTour(tourName);
            return false;
        });
    } else if (!demoButton) {
        console.error('Demo button not found in the DOM during setupDemoButton()');
    }
}

/**
 * Start a guided tour
 * @param {string} tourName - The name of the tour to start
 */
function startTour(tourName) {
    // Don't start a new tour if one is already active
    if (tourActive) {
        endTour();
    }
    
    // Update tour state
    tourActive = true;
    currentTourStep = 0;
    currentTourName = tourName;
    
    // Get tour steps based on the tour name
    tourSteps = getTourSteps(tourName);
    
    // Show welcome message
    showWelcomeMessage(tourName);
}

/**
 * Show welcome message for the tour
 * @param {string} tourName - The name of the tour
 */
function showWelcomeMessage(tourName) {
    // Create modal for welcome message
    const modalHTML = `
    <div class="modal fade" id="tourWelcomeModal" tabindex="-1" aria-labelledby="tourWelcomeModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header bg-primary text-white">
                    <h5 class="modal-title" id="tourWelcomeModalLabel">Welcome to the ${getTourTitle(tourName)}</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <p>${getTourDescription(tourName)}</p>
                    <p>This tour will guide you through the key features and functionalities of this section.</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" onclick="endTour()">Skip Tour</button>
                    <button type="button" class="btn btn-primary" data-bs-dismiss="modal" onclick="showNextTourStep()">Start Tour</button>
                </div>
            </div>
        </div>
    </div>
    `;
    
    // Add modal to the document
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalHTML;
    document.body.appendChild(modalContainer);
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('tourWelcomeModal'));
    modal.show();
    
    // Clean up when the modal is hidden
    document.getElementById('tourWelcomeModal').addEventListener('hidden.bs.modal', function() {
        if (document.getElementById('tourWelcomeModal')) {
            document.getElementById('tourWelcomeModal').remove();
        }
    });
}

/**
 * Show the next step in the tour
 */
function showNextTourStep() {
    // If we've reached the end of the tour, show completion message
    if (currentTourStep >= tourSteps.length) {
        showTourCompletionMessage();
        return;
    }
    
    // Get the current step
    const step = tourSteps[currentTourStep];
    
    // Find the target element
    const targetElement = document.querySelector(step.element);
    
    if (!targetElement) {
        console.error(`Target element not found: ${step.element}`);
        currentTourStep++;
        showNextTourStep();
        return;
    }
    
    // Create the popover
    const popover = new bootstrap.Popover(targetElement, {
        title: step.title,
        content: step.content,
        placement: step.placement || 'auto',
        trigger: 'manual',
        html: true,
        template: `
            <div class="popover tour-popover" role="tooltip">
                <div class="popover-arrow"></div>
                <h3 class="popover-header"></h3>
                <div class="popover-body"></div>
                <div class="popover-footer p-2 d-flex justify-content-between">
                    <button class="btn btn-sm btn-outline-secondary" onclick="showPreviousTourStep()">Previous</button>
                    <div class="tour-step-indicator small text-muted">Step ${currentTourStep + 1} of ${tourSteps.length}</div>
                    <button class="btn btn-sm btn-primary" onclick="showNextTourStep()">Next</button>
                </div>
            </div>
        `
    });
    
    // Store popover in data attribute for clean up
    targetElement.setAttribute('data-tour-active', 'true');
    
    // Show the popover
    popover.show();
    
    // Apply highlight effect
    targetElement.classList.add('tour-highlight');
    
    // Scroll to the element
    targetElement.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
    });
    
    // Increment the step counter
    currentTourStep++;
}

/**
 * Show the previous step in the tour
 */
function showPreviousTourStep() {
    // Remove current highlight and popover
    clearCurrentTourStep();
    
    // Decrement step counter (minimum 0)
    currentTourStep = Math.max(0, currentTourStep - 2);
    
    // Show the previous step
    showNextTourStep();
}

/**
 * Clear current tour step highlights and popovers
 */
function clearCurrentTourStep() {
    // Remove all active tour highlights and popovers
    document.querySelectorAll('[data-tour-active="true"]').forEach(element => {
        // Remove highlight
        element.classList.remove('tour-highlight');
        
        // Remove popover
        const popover = bootstrap.Popover.getInstance(element);
        if (popover) {
            popover.dispose();
        }
        
        // Remove active flag
        element.removeAttribute('data-tour-active');
    });
}

/**
 * Show tour completion message
 */
function showTourCompletionMessage() {
    // Create modal for completion message
    const modalHTML = `
    <div class="modal fade" id="tourCompletionModal" tabindex="-1" aria-labelledby="tourCompletionModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header bg-success text-white">
                    <h5 class="modal-title" id="tourCompletionModalLabel">Tour Completed!</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <p>Congratulations! You've completed the ${getTourTitle(currentTourName)}.</p>
                    <p>You now have a better understanding of the key features and functionalities of this section.</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-primary" data-bs-dismiss="modal" onclick="restartTour()">Restart Tour</button>
                </div>
            </div>
        </div>
    </div>
    `;
    
    // Add modal to the document
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalHTML;
    document.body.appendChild(modalContainer);
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('tourCompletionModal'));
    modal.show();
    
    // Clean up when the modal is hidden
    document.getElementById('tourCompletionModal').addEventListener('hidden.bs.modal', function() {
        if (document.getElementById('tourCompletionModal')) {
            document.getElementById('tourCompletionModal').remove();
        }
        endTour();
    });
}

/**
 * End the current tour
 */
function endTour() {
    // Clear any active tour steps
    clearCurrentTourStep();
    
    // Reset tour state
    tourActive = false;
    currentTourStep = 0;
    tourSteps = [];
    currentTourName = '';
}

/**
 * Restart the current tour
 */
function restartTour() {
    endTour();
    startTour(currentTourName);
}

/**
 * Get tour steps based on the tour name
 * @param {string} tourName - The name of the tour
 * @returns {Array} - Array of tour steps
 */
function getTourSteps(tourName) {
    switch (tourName) {
        case 'agent-registry':
            return [
                {
                    element: '.card-header',
                    title: 'Registered Agents',
                    content: 'This table shows all agents currently registered in the system, their types, and statuses.',
                    placement: 'top'
                },
                {
                    element: '.table-responsive',
                    title: 'Agent Information',
                    content: 'Each row represents an agent with its ID, name, type, status, and available actions.',
                    placement: 'top'
                },
                {
                    element: '.card:nth-child(2) .card-header',
                    title: 'Performance Metrics',
                    content: 'This panel shows real-time performance metrics for each active agent in the system.',
                    placement: 'top'
                },
                {
                    element: '.card:nth-child(3) .card-header',
                    title: 'Recent Activities',
                    content: 'Here you can see the most recent activities performed by the agents in the system.',
                    placement: 'left'
                },
                {
                    element: '.btn-outline-primary:first',
                    title: 'Agent Details',
                    content: 'Click this button to view detailed information about the agent, including its capabilities and status.',
                    placement: 'top'
                }
            ];
            
        case 'workflow-designer':
            return [
                {
                    element: '.col-md-3 .card-header',
                    title: 'Components Panel',
                    content: 'This panel contains all the components you can use to build your workflow, including agents, connectors, and data sources.',
                    placement: 'right'
                },
                {
                    element: '.complexity-meter-container',
                    title: 'Complexity Meter',
                    content: 'This meter shows the current complexity of your workflow, which affects performance and resource requirements.',
                    placement: 'bottom'
                },
                {
                    element: '#workflow-canvas',
                    title: 'Workflow Canvas',
                    content: 'Drag and drop components from the left panel to this canvas to build your workflow. Connect components to create the process flow.',
                    placement: 'top'
                },
                {
                    element: '.col-md-6:first .card-header',
                    title: 'Properties Panel',
                    content: 'When you select a component on the canvas, this panel displays its properties that you can modify.',
                    placement: 'top'
                },
                {
                    element: '.col-md-6:last .card-header',
                    title: 'Complexity Analysis',
                    content: 'This panel provides detailed analysis of your workflow\'s complexity metrics to help you optimize it.',
                    placement: 'left'
                }
            ];
            
        case 'agent-playground':
            return [
                {
                    element: '.col-md-4 .card-header:first',
                    title: 'Agent Selection',
                    content: 'Use this panel to select the agent you want to work with and configure its operating mode.',
                    placement: 'right'
                },
                {
                    element: '#agent-parameters',
                    title: 'Agent Parameters',
                    content: 'Customize the agent\'s behavior by modifying these parameters in JSON format.',
                    placement: 'right'
                },
                {
                    element: '#execute-btn',
                    title: 'Execute Agent',
                    content: 'Click this button to run the agent with the configured parameters.',
                    placement: 'right'
                },
                {
                    element: '#agent-output',
                    title: 'Agent Output',
                    content: 'This panel displays the real-time output from the agent execution, including system messages and results.',
                    placement: 'left'
                },
                {
                    element: '.col-md-6:first .card-header',
                    title: 'Visualizations',
                    content: 'The agent may generate visualizations of its analysis, which will appear in this panel.',
                    placement: 'top'
                },
                {
                    element: '.list-group-item',
                    title: 'Compare Results',
                    content: 'Use this action to compare the current forecast with previously saved forecasts.',
                    placement: 'left'
                }
            ];
            
        case 'general':
        default:
            return [
                {
                    element: '.navbar-brand',
                    title: 'Welcome to LevyMaster',
                    content: 'LevyMaster is an AI-powered financial calculation platform specialized in multi-component process (MCP) management.',
                    placement: 'bottom'
                },
                {
                    element: '.navbar-nav',
                    title: 'Navigation Menu',
                    content: 'Use this menu to navigate between different sections of the application, including the MCP framework.',
                    placement: 'bottom'
                },
                {
                    element: '.container:first',
                    title: 'Main Content Area',
                    content: 'This area displays the content of the selected section. Try navigating to the MCP UI section to explore the advanced features.',
                    placement: 'top'
                }
            ];
    }
}

/**
 * Get the title for a tour
 * @param {string} tourName - The name of the tour
 * @returns {string} - The tour title
 */
function getTourTitle(tourName) {
    switch (tourName) {
        case 'agent-registry':
            return 'Agent Registry Tour';
        case 'workflow-designer':
            return 'Workflow Designer Tour';
        case 'agent-playground':
            return 'Agent Playground Tour';
        case 'general':
        default:
            return 'LevyMaster Demo Tour';
    }
}

/**
 * Get the description for a tour
 * @param {string} tourName - The name of the tour
 * @returns {string} - The tour description
 */
function getTourDescription(tourName) {
    switch (tourName) {
        case 'agent-registry':
            return 'Discover how the Agent Registry allows you to monitor and manage all AI agents in the LevyMaster system.';
        case 'workflow-designer':
            return 'Learn how to create custom workflows by connecting different agents and data sources to automate complex levy processes.';
        case 'agent-playground':
            return 'Explore the Agent Playground where you can interact directly with individual agents and test their capabilities.';
        case 'general':
        default:
            return 'Get familiar with the LevyMaster platform and its key features for levy management and calculation.';
    }
}

/**
 * Set up event listeners for contact support buttons
 */
function setupContactButtons() {
    // Contact support button in help menu
    const contactSupportBtn = document.getElementById('contactSupportBtn');
    if (contactSupportBtn) {
        contactSupportBtn.addEventListener('click', function() {
            // Close help menu first
            const helpMenu = document.getElementById('helpMenu');
            if (helpMenu && helpMenu.classList.contains('active')) {
                toggleHelpMenu(false);
            }
            
            // Redirect to contact page or show contact form
            window.location.href = '/contact';
        });
    }
}