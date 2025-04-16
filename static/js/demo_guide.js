/**
 * LevyMaster Demo Guide
 * Interactive demo mode for the LevyMaster MCP system
 */

// Wait for window to load before initializing
window.addEventListener('load', function() {
    console.log('Demo Guide initialized');
    
    // Add the demo mode toggle button to the page
    addDemoModeToggle();
    
    // Set up page-specific demo content
    setupPageSpecificDemo();
    
    // Force log to ensure code is running
    console.log('Demo mode toggle button should now be visible');
});

/**
 * Adds the demo mode toggle button to the page
 */
function addDemoModeToggle() {
    // Create toggle button
    const toggleButton = document.createElement('button');
    toggleButton.className = 'demo-mode-toggle';
    toggleButton.id = 'demoModeToggle';
    toggleButton.innerHTML = '<i class="bi bi-play-fill"></i>';
    toggleButton.setAttribute('title', 'Start Demo Mode');
    
    // Create demo mode indicator
    const indicator = document.createElement('div');
    indicator.className = 'demo-mode-indicator';
    indicator.id = 'demoModeIndicator';
    indicator.innerHTML = '<i class="bi bi-lightning-fill"></i> Demo Mode Active';
    
    // Add elements to page
    document.body.appendChild(toggleButton);
    document.body.appendChild(indicator);
    
    // Set up toggle event
    toggleButton.addEventListener('click', toggleDemoMode);
}

/**
 * Toggles the demo mode on/off
 */
function toggleDemoMode() {
    const toggle = document.getElementById('demoModeToggle');
    const indicator = document.getElementById('demoModeIndicator');
    
    // Check if demo mode is active
    const isDemoActive = toggle.classList.contains('active');
    
    if (isDemoActive) {
        // Deactivate demo mode
        toggle.classList.remove('active');
        indicator.classList.remove('active');
        toggle.innerHTML = '<i class="bi bi-play-fill"></i>';
        toggle.setAttribute('title', 'Start Demo Mode');
        
        // Clean up demo elements
        cleanupDemoElements();
    } else {
        // Activate demo mode
        toggle.classList.add('active');
        indicator.classList.add('active');
        toggle.innerHTML = '<i class="bi bi-stop-fill"></i>';
        toggle.setAttribute('title', 'End Demo Mode');
        
        // Show intro card and start demo for current page
        showDemoIntroCard();
    }
}

/**
 * Creates and shows the initial demo introduction card
 */
function showDemoIntroCard() {
    // Identify current page
    const currentPath = window.location.pathname;
    let demoTitle, demoDescription, startDemoFunction;
    
    // Set content based on current page
    if (currentPath.includes('workflow-designer')) {
        demoTitle = 'Workflow Designer Demo';
        demoDescription = 'This guided tour will introduce you to the key features of the Workflow Designer, including the advanced complexity metrics and optimization tools.';
        startDemoFunction = startWorkflowDesignerDemo;
    } else if (currentPath.includes('agent-registry')) {
        demoTitle = 'Agent Registry Demo';
        demoDescription = 'Explore the Agent Registry interface to learn how to monitor and manage AI agents in the LevyMaster system.';
        startDemoFunction = startAgentRegistryDemo;
    } else if (currentPath.includes('agent-playground')) {
        demoTitle = 'Agent Playground Demo';
        demoDescription = 'Discover how to interact directly with AI agents and create custom workflows in this interactive playground.';
        startDemoFunction = startAgentPlaygroundDemo;
    } else {
        demoTitle = 'LevyMaster Demo';
        demoDescription = 'This guided tour will introduce you to the key features of the LevyMaster platform. Please navigate to Workflow Designer, Agent Registry, or Agent Playground for a specialized demo.';
        startDemoFunction = null;
    }
    
    // Create and populate demo card
    const demoCard = document.createElement('div');
    demoCard.className = 'demo-card';
    demoCard.id = 'demoIntroCard';
    demoCard.style.top = '100px';
    demoCard.style.left = '50%';
    demoCard.style.transform = 'translateX(-50%)';
    
    demoCard.innerHTML = `
        <div class="demo-card-header">
            <h5 class="demo-card-title">${demoTitle}</h5>
            <button type="button" class="btn-close" aria-label="Close"></button>
        </div>
        <div class="demo-card-body">
            <p>${demoDescription}</p>
        </div>
        <div class="demo-card-footer">
            <span class="demo-card-step">Step 1 of 5</span>
            <button class="btn btn-primary btn-sm" id="startDemoBtn">Start Tour</button>
        </div>
    `;
    
    // Add to document
    document.body.appendChild(demoCard);
    
    // Set up event listeners
    document.querySelector('#demoIntroCard .btn-close').addEventListener('click', function() {
        demoCard.remove();
        toggleDemoMode(); // Turn off demo mode
    });
    
    if (startDemoFunction) {
        document.getElementById('startDemoBtn').addEventListener('click', function() {
            demoCard.remove();
            startDemoFunction();
        });
    } else {
        document.getElementById('startDemoBtn').addEventListener('click', function() {
            demoCard.remove();
            showDemoNavigationPrompt();
        });
    }
}

/**
 * Shows a prompt to navigate to a demo-enabled page
 */
function showDemoNavigationPrompt() {
    const demoPrompt = document.createElement('div');
    demoPrompt.className = 'demo-card';
    demoPrompt.id = 'demoNavPrompt';
    demoPrompt.style.top = '100px';
    demoPrompt.style.left = '50%';
    demoPrompt.style.transform = 'translateX(-50%)';
    
    demoPrompt.innerHTML = `
        <div class="demo-card-header">
            <h5 class="demo-card-title">Choose a Demo</h5>
            <button type="button" class="btn-close" aria-label="Close"></button>
        </div>
        <div class="demo-card-body">
            <p>Please select one of the available demos:</p>
            <div class="list-group mt-3">
                <a href="/workflow-designer" class="list-group-item list-group-item-action">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">Workflow Designer</h6>
                        <small><i class="bi bi-arrow-right"></i></small>
                    </div>
                    <small class="text-muted">Design and optimize AI workflows</small>
                </a>
                <a href="/agent-registry" class="list-group-item list-group-item-action">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">Agent Registry</h6>
                        <small><i class="bi bi-arrow-right"></i></small>
                    </div>
                    <small class="text-muted">Monitor and manage AI agents</small>
                </a>
                <a href="/agent-playground" class="list-group-item list-group-item-action">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">Agent Playground</h6>
                        <small><i class="bi bi-arrow-right"></i></small>
                    </div>
                    <small class="text-muted">Interact with agents directly</small>
                </a>
            </div>
        </div>
    `;
    
    // Add to document
    document.body.appendChild(demoPrompt);
    
    // Set up event listeners
    document.querySelector('#demoNavPrompt .btn-close').addEventListener('click', function() {
        demoPrompt.remove();
        toggleDemoMode(); // Turn off demo mode
    });
}

/**
 * Sets up page-specific demo initialization based on current URL
 */
function setupPageSpecificDemo() {
    const currentPath = window.location.pathname;
    
    if (currentPath.includes('workflow-designer')) {
        initWorkflowDesignerDemo();
    } else if (currentPath.includes('agent-registry')) {
        initAgentRegistryDemo();
    } else if (currentPath.includes('agent-playground')) {
        initAgentPlaygroundDemo();
    }
}

/**
 * Initializes the Workflow Designer demo elements
 */
function initWorkflowDesignerDemo() {
    // Add any required elements or listeners for workflow designer demos
    console.log('Workflow Designer demo initialized');
}

/**
 * Initializes the Agent Registry demo elements
 */
function initAgentRegistryDemo() {
    // Add any required elements or listeners for agent registry demos
    console.log('Agent Registry demo initialized');
    
    // Add detail button functionality to show agent details modal
    const detailButtons = document.querySelectorAll('.btn-outline-primary');
    detailButtons.forEach(button => {
        button.addEventListener('click', function() {
            // This is now handled in the page's own JavaScript
        });
    });
}

/**
 * Initializes the Agent Playground demo elements
 */
function initAgentPlaygroundDemo() {
    // Add any required elements or listeners for agent playground demos
    console.log('Agent Playground demo initialized');
}

/**
 * Starts the Workflow Designer demo sequence
 */
function startWorkflowDesignerDemo() {
    console.log('Starting Workflow Designer demo');
    
    // Create overlay
    const overlay = document.createElement('div');
    overlay.className = 'demo-overlay active';
    overlay.id = 'demoOverlay';
    document.body.appendChild(overlay);
    
    // Begin the tour
    workflowDesignerTourStep1();
}

/**
 * Starts the Agent Registry demo sequence
 */
function startAgentRegistryDemo() {
    console.log('Starting Agent Registry demo');
    
    // Create overlay
    const overlay = document.createElement('div');
    overlay.className = 'demo-overlay active';
    overlay.id = 'demoOverlay';
    document.body.appendChild(overlay);
    
    // Begin the tour
    agentRegistryTourStep1();
}

/**
 * Starts the Agent Playground demo sequence
 */
function startAgentPlaygroundDemo() {
    console.log('Starting Agent Playground demo');
    
    // Create overlay
    const overlay = document.createElement('div');
    overlay.className = 'demo-overlay active';
    overlay.id = 'demoOverlay';
    document.body.appendChild(overlay);
    
    // Begin the tour
    agentPlaygroundTourStep1();
}

/**
 * Removes all demo elements from the page
 */
function cleanupDemoElements() {
    // Remove overlay
    const overlay = document.getElementById('demoOverlay');
    if (overlay) overlay.remove();
    
    // Remove all tooltips
    const tooltips = document.querySelectorAll('.demo-tooltip');
    tooltips.forEach(tooltip => tooltip.remove());
    
    // Remove all cards
    const cards = document.querySelectorAll('.demo-card');
    cards.forEach(card => card.remove());
    
    // Remove highlights
    const highlights = document.querySelectorAll('.demo-highlight');
    highlights.forEach(element => element.classList.remove('demo-highlight'));
    
    // Remove completion message
    const completion = document.getElementById('demoCompletion');
    if (completion) completion.remove();
}

/**
 * Creates a tooltip pointing to a specific element
 * @param {string} targetElementId - ID of the element to point at
 * @param {string} text - Text for the tooltip
 * @param {string} position - Position (top, right, bottom, left)
 */
function createElementTooltip(targetElementId, text, position = 'bottom') {
    const targetElement = document.getElementById(targetElementId);
    if (!targetElement) return null;
    
    // Get element position
    const rect = targetElement.getBoundingClientRect();
    
    // Create tooltip
    const tooltip = document.createElement('div');
    tooltip.className = `demo-tooltip ${position}`;
    tooltip.innerHTML = text;
    document.body.appendChild(tooltip);
    
    // Add highlight to target
    targetElement.classList.add('demo-highlight');
    
    // Position tooltip
    let tooltipLeft, tooltipTop;
    
    switch(position) {
        case 'top':
            tooltipLeft = rect.left + rect.width / 2 - tooltip.offsetWidth / 2;
            tooltipTop = rect.top - tooltip.offsetHeight - 12;
            break;
        case 'right':
            tooltipLeft = rect.right + 12;
            tooltipTop = rect.top + rect.height / 2 - tooltip.offsetHeight / 2;
            break;
        case 'bottom':
            tooltipLeft = rect.left + rect.width / 2 - tooltip.offsetWidth / 2;
            tooltipTop = rect.bottom + 12;
            break;
        case 'left':
            tooltipLeft = rect.left - tooltip.offsetWidth - 12;
            tooltipTop = rect.top + rect.height / 2 - tooltip.offsetHeight / 2;
            break;
    }
    
    tooltip.style.left = `${tooltipLeft}px`;
    tooltip.style.top = `${tooltipTop}px`;
    
    return tooltip;
}

/**
 * Workflow Designer tour - Step 1
 * Introduces the complexity meter
 */
function workflowDesignerTourStep1() {
    // Find complexity meter element
    const complexityMeterId = 'workflowComplexityMeter';
    
    // Create tooltip for complexity meter
    const tooltip = createElementTooltip(
        complexityMeterId,
        'The Workflow Complexity Meter analyzes your workflow and provides a real-time assessment of its complexity across 5 key dimensions.',
        'bottom'
    );
    
    // Create step card
    const stepCard = document.createElement('div');
    stepCard.className = 'demo-card';
    stepCard.id = 'demoStepCard1';
    stepCard.style.top = '100px';
    stepCard.style.right = '20px';
    
    stepCard.innerHTML = `
        <div class="demo-card-header">
            <h5 class="demo-card-title">Workflow Complexity</h5>
            <button type="button" class="btn-close" aria-label="Close"></button>
        </div>
        <div class="demo-card-body">
            <p>The complexity meter helps you understand how your workflow will perform in production.</p>
            <p>High complexity workflows may require more computational resources and can impact performance.</p>
        </div>
        <div class="demo-card-footer">
            <span class="demo-card-step">Step 1 of 3</span>
            <button class="btn btn-primary btn-sm" id="nextStepBtn">Next Step</button>
        </div>
    `;
    
    // Add to document
    document.body.appendChild(stepCard);
    
    // Set up event listeners
    document.querySelector('#demoStepCard1 .btn-close').addEventListener('click', function() {
        cleanupDemoElements();
        toggleDemoMode(); // Turn off demo mode
    });
    
    document.getElementById('nextStepBtn').addEventListener('click', function() {
        tooltip.remove();
        document.getElementById(complexityMeterId).classList.remove('demo-highlight');
        stepCard.remove();
        workflowDesignerTourStep2();
    });
}

/**
 * Workflow Designer tour - Step 2
 * Demonstrates the Analyze feature
 */
function workflowDesignerTourStep2() {
    // Find analyze button
    const analyzeButtonId = 'analyzeWorkflowBtn';
    
    // Create tooltip for analyze button
    const tooltip = createElementTooltip(
        analyzeButtonId,
        'The Analyze feature provides detailed insights into your workflow performance and identifies potential bottlenecks.',
        'top'
    );
    
    // Create step card
    const stepCard = document.createElement('div');
    stepCard.className = 'demo-card';
    stepCard.id = 'demoStepCard2';
    stepCard.style.top = '150px';
    stepCard.style.left = '20px';
    
    stepCard.innerHTML = `
        <div class="demo-card-header">
            <h5 class="demo-card-title">Workflow Analysis</h5>
            <button type="button" class="btn-close" aria-label="Close"></button>
        </div>
        <div class="demo-card-body">
            <p>Click "Analyze" to get comprehensive metrics on:</p>
            <ul>
                <li>Total agent steps & computational cost</li>
                <li>Agent communication overhead</li>
                <li>Expected execution time</li>
                <li>Error recovery pathways</li>
                <li>Data transfer volume</li>
            </ul>
        </div>
        <div class="demo-card-footer">
            <span class="demo-card-step">Step 2 of 3</span>
            <button class="btn btn-primary btn-sm" id="nextStepBtn">Next Step</button>
        </div>
    `;
    
    // Add to document
    document.body.appendChild(stepCard);
    
    // Set up event listeners
    document.querySelector('#demoStepCard2 .btn-close').addEventListener('click', function() {
        cleanupDemoElements();
        toggleDemoMode(); // Turn off demo mode
    });
    
    document.getElementById('nextStepBtn').addEventListener('click', function() {
        tooltip.remove();
        document.getElementById(analyzeButtonId).classList.remove('demo-highlight');
        stepCard.remove();
        workflowDesignerTourStep3();
    });
}

/**
 * Workflow Designer tour - Step 3
 * Shows the optimization feature
 */
function workflowDesignerTourStep3() {
    // Find optimize button
    const optimizeButtonId = 'optimizeWorkflowBtn';
    
    // Create tooltip for optimize button
    const tooltip = createElementTooltip(
        optimizeButtonId,
        'The Optimize feature automatically analyzes your workflow and suggests improvements to enhance performance.',
        'right'
    );
    
    // Create step card
    const stepCard = document.createElement('div');
    stepCard.className = 'demo-card';
    stepCard.id = 'demoStepCard3';
    stepCard.style.top = '200px';
    stepCard.style.right = '20px';
    
    stepCard.innerHTML = `
        <div class="demo-card-header">
            <h5 class="demo-card-title">Workflow Optimization</h5>
            <button type="button" class="btn-close" aria-label="Close"></button>
        </div>
        <div class="demo-card-body">
            <p>The optimization engine can:</p>
            <ul>
                <li>Merge redundant agent steps</li>
                <li>Simplify complex branches</li>
                <li>Identify parallel execution opportunities</li>
                <li>Reduce total computational cost</li>
                <li>Preview before/after performance</li>
            </ul>
            <p>This helps make your workflows faster and more efficient.</p>
        </div>
        <div class="demo-card-footer">
            <span class="demo-card-step">Step 3 of 3</span>
            <button class="btn btn-primary btn-sm" id="finishDemoBtn">Finish Tour</button>
        </div>
    `;
    
    // Add to document
    document.body.appendChild(stepCard);
    
    // Set up event listeners
    document.querySelector('#demoStepCard3 .btn-close').addEventListener('click', function() {
        cleanupDemoElements();
        toggleDemoMode(); // Turn off demo mode
    });
    
    document.getElementById('finishDemoBtn').addEventListener('click', function() {
        tooltip.remove();
        document.getElementById(optimizeButtonId).classList.remove('demo-highlight');
        stepCard.remove();
        showDemoCompletionMessage();
    });
}

/**
 * Agent Registry tour - Step 1
 */
function agentRegistryTourStep1() {
    // Find agent table
    const agentTableId = 'agentRegistryTable';
    
    // Create step card
    const stepCard = document.createElement('div');
    stepCard.className = 'demo-card';
    stepCard.id = 'demoStepCard1';
    stepCard.style.top = '100px';
    stepCard.style.left = '20px';
    
    stepCard.innerHTML = `
        <div class="demo-card-header">
            <h5 class="demo-card-title">Agent Registry</h5>
            <button type="button" class="btn-close" aria-label="Close"></button>
        </div>
        <div class="demo-card-body">
            <p>The Agent Registry provides a central place to monitor and manage all AI agents in your system.</p>
            <p>For each agent, you can:</p>
            <ul>
                <li>View agent status and health metrics</li>
                <li>Access detailed performance analytics</li>
                <li>Configure agent parameters</li>
                <li>View logs and activity history</li>
            </ul>
            <p>Try clicking the "Details" button on any agent to see more information.</p>
        </div>
        <div class="demo-card-footer">
            <span class="demo-card-step">Step 1 of 1</span>
            <button class="btn btn-primary btn-sm" id="finishDemoBtn">Finish Tour</button>
        </div>
    `;
    
    // Add to document
    document.body.appendChild(stepCard);
    
    // Set up event listeners
    document.querySelector('#demoStepCard1 .btn-close').addEventListener('click', function() {
        cleanupDemoElements();
        toggleDemoMode(); // Turn off demo mode
    });
    
    document.getElementById('finishDemoBtn').addEventListener('click', function() {
        stepCard.remove();
        showDemoCompletionMessage();
    });
    
    // Highlight the first detail button
    const firstDetailBtn = document.querySelector('.btn-outline-primary');
    if (firstDetailBtn) {
        firstDetailBtn.classList.add('demo-highlight');
    }
}

/**
 * Agent Playground tour - Step 1
 */
function agentPlaygroundTourStep1() {
    // Create step card
    const stepCard = document.createElement('div');
    stepCard.className = 'demo-card';
    stepCard.id = 'demoStepCard1';
    stepCard.style.top = '100px';
    stepCard.style.right = '20px';
    
    stepCard.innerHTML = `
        <div class="demo-card-header">
            <h5 class="demo-card-title">Agent Playground</h5>
            <button type="button" class="btn-close" aria-label="Close"></button>
        </div>
        <div class="demo-card-body">
            <p>The Agent Playground allows you to interact directly with AI agents and test custom workflows.</p>
            <p>You can:</p>
            <ul>
                <li>Send messages to specific agents</li>
                <li>Test agent capabilities in real-time</li>
                <li>Create and save custom workflows</li>
                <li>Experiment with agent collaboration</li>
            </ul>
            <p>The playground is perfect for testing before deploying workflows to production.</p>
        </div>
        <div class="demo-card-footer">
            <span class="demo-card-step">Step 1 of 1</span>
            <button class="btn btn-primary btn-sm" id="finishDemoBtn">Finish Tour</button>
        </div>
    `;
    
    // Add to document
    document.body.appendChild(stepCard);
    
    // Set up event listeners
    document.querySelector('#demoStepCard1 .btn-close').addEventListener('click', function() {
        cleanupDemoElements();
        toggleDemoMode(); // Turn off demo mode
    });
    
    document.getElementById('finishDemoBtn').addEventListener('click', function() {
        stepCard.remove();
        showDemoCompletionMessage();
    });
}

/**
 * Shows demo completion message
 */
function showDemoCompletionMessage() {
    // Remove overlay
    const overlay = document.getElementById('demoOverlay');
    if (overlay) overlay.remove();
    
    // Create completion message
    const completion = document.createElement('div');
    completion.className = 'demo-completion active';
    completion.id = 'demoCompletion';
    
    completion.innerHTML = `
        <div class="demo-completion-icon">
            <i class="bi bi-check-circle"></i>
        </div>
        <h4 class="demo-completion-title">Demo Complete!</h4>
        <p class="demo-completion-message">You've completed the guided tour of this feature. Feel free to explore and experiment with the interface.</p>
        <button class="btn btn-primary" id="closeDemoBtn">Close Demo</button>
    `;
    
    // Add to document
    document.body.appendChild(completion);
    
    // Set up event listener
    document.getElementById('closeDemoBtn').addEventListener('click', function() {
        cleanupDemoElements();
        toggleDemoMode(); // Turn off demo mode
    });
}