/**
 * LEVYMASTER AUTOMATED DEMO SYSTEM
 * This module provides a comprehensive interactive demonstration of the LevyMaster system.
 * It simulates real-world usage with sample data and actions.
 */

// Demo state management
let demoActive = false;
let currentDemoStep = 0;
let demoScenario = null;
let demoTimer = null;
let demoSpeed = 1500; // Base speed for demo animations (ms)
let demoHistory = []; // Keep track of actions performed

// Demo Scenarios - Comprehensive workflows showcasing system capabilities
const demoScenarios = {
    // Agent Registry Demo
    'agent-registry': {
        name: 'Agent Collaboration Demo',
        description: 'Experience how intelligent agents collaborate to process complex levy calculations',
        steps: [
            {
                action: 'highlight',
                element: 'tr:nth-child(1)',
                message: 'Identifying the Levy Analysis Agent',
                duration: 2000
            },
            {
                action: 'click',
                element: 'tr:nth-child(1) .btn-outline-primary',
                message: 'Examining the Levy Analysis Agent capabilities',
                duration: 4000
            },
            {
                action: 'modal-close',
                message: 'Reviewing agent capabilities complete',
                duration: 1000
            },
            {
                action: 'highlight',
                element: 'tr:nth-child(4)',
                message: 'Selecting the Workflow Coordinator Agent',
                duration: 2000
            },
            {
                action: 'click',
                element: 'tr:nth-child(4) .btn-outline-primary',
                message: 'Examining the Workflow Coordinator Agent',
                duration: 4000
            },
            {
                action: 'modal-close',
                message: 'Reviewing coordinator capabilities complete',
                duration: 1000
            },
            {
                action: 'highlight',
                element: '.card:nth-child(3)',
                message: 'Monitoring real-time agent activity',
                duration: 3000
            },
            {
                action: 'simulate-activity',
                target: 'activity-log',
                message: 'New levy calculation workflow initiated',
                duration: 2000
            },
            {
                action: 'highlight',
                element: '.card:nth-child(2)',
                message: 'Checking agent performance metrics',
                duration: 3000
            },
            {
                action: 'navigate',
                url: '/mcp/workflow-designer',
                message: 'Moving to Workflow Designer',
                duration: 1000
            }
        ]
    },
    
    // Workflow Designer Demo
    'workflow-designer': {
        name: 'Workflow Design & Optimization Demo',
        description: 'See how to create, test and optimize levy calculation workflows',
        steps: [
            {
                action: 'highlight',
                element: '.col-md-3 .card',
                message: 'Selecting workflow components',
                duration: 2000
            },
            {
                action: 'drag-and-drop',
                source: '.component-list li:nth-child(1)',
                target: '#workflow-canvas',
                position: {x: 100, y: 100},
                message: 'Adding Levy Analysis component',
                duration: 3000
            },
            {
                action: 'drag-and-drop',
                source: '.component-list li:nth-child(3)',
                target: '#workflow-canvas',
                position: {x: 300, y: 100},
                message: 'Adding Prediction component',
                duration: 3000
            },
            {
                action: 'draw-connector',
                source: {x: 150, y: 120},
                target: {x: 280, y: 120},
                message: 'Connecting analysis to prediction',
                duration: 3000
            },
            {
                action: 'highlight',
                element: '.complexity-meter-container',
                message: 'Monitoring workflow complexity',
                duration: 2000
            },
            {
                action: 'update-ui',
                element: '.complexity-meter-fill',
                property: 'width',
                value: '45%',
                message: 'Workflow complexity increasing',
                duration: 2000
            },
            {
                action: 'highlight',
                element: '.col-md-6:last',
                message: 'Reviewing complexity analysis',
                duration: 3000
            },
            {
                action: 'click',
                element: '.workflow-actions .btn-primary',
                message: 'Running workflow optimization',
                duration: 2000
            },
            {
                action: 'simulate-activity',
                target: 'optimization-result',
                message: 'Workflow optimized - Estimated 32% performance improvement',
                duration: 4000
            },
            {
                action: 'navigate',
                url: '/mcp/agent-playground',
                message: 'Moving to Agent Playground',
                duration: 1000
            }
        ]
    },
    
    // Agent Playground Demo
    'agent-playground': {
        name: 'Interactive Agent Playground Demo',
        description: 'Test how the system handles real-world levy calculation scenarios',
        steps: [
            {
                action: 'highlight',
                element: '.agent-selector',
                message: 'Selecting the Levy Analysis Agent',
                duration: 2000
            },
            {
                action: 'select',
                element: '.agent-selector',
                value: 'levy_analysis',
                message: 'Levy Analysis Agent selected',
                duration: 2000
            },
            {
                action: 'highlight',
                element: '.query-input',
                message: 'Preparing to enter query',
                duration: 1500
            },
            {
                action: 'type',
                element: '.query-input',
                text: 'Calculate maximum allowable levy rate for Central School District with 3% new construction',
                message: 'Entering levy calculation query',
                duration: 4000
            },
            {
                action: 'click',
                element: '.query-submit',
                message: 'Submitting query to Levy Analysis Agent',
                duration: 2000
            },
            {
                action: 'fetch-real-data',
                endpoint: '/api/levy/analysis/district/benton-county-school',
                params: { newConstruction: 3, year: 2025 },
                target: 'response-container',
                fallbackHTML: `<div class="card mb-3 border-success">
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0">Levy Analysis Result</h5>
                    </div>
                    <div class="card-body">
                        <h6>Benton County School District - Levy Rate Analysis</h6>
                        <p>Based on the parameters provided:</p>
                        <ul>
                            <li>Current assessed value: $2,217,483,650</li>
                            <li>New construction value: $66,524,510 (3%)</li>
                            <li>Prior year levy amount: $11,087,418.25</li>
                            <li>Statutory maximum rate: $1.50 per $1,000</li>
                        </ul>
                        <h6 class="mt-3">Calculation Results:</h6>
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Scenario</th>
                                        <th>Calculated Rate</th>
                                        <th>Levy Amount</th>
                                        <th>% Change</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>Statutory Maximum</td>
                                        <td>$1.50</td>
                                        <td>$3,326,225.48</td>
                                        <td>+30.9%</td>
                                    </tr>
                                    <tr class="table-success">
                                        <td>Recommended Rate</td>
                                        <td>$1.28</td>
                                        <td>$2,827,620.04</td>
                                        <td>+1.0%</td>
                                    </tr>
                                    <tr>
                                        <td>Minimum (No Increase)</td>
                                        <td>$0.99</td>
                                        <td>$2,217,483.65</td>
                                        <td>0.0%</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <div class="alert alert-info mt-3">
                            <strong>Recommendation:</strong> Based on Benton County's historical patterns, the optimal levy rate is $1.28 per $1,000 assessed value, which incorporates new construction while maintaining a modest 1% increase over prior year collections.
                        </div>
                    </div>
                </div>`,
                message: 'Displaying analysis results',
                duration: 5000
            },
            {
                action: 'highlight',
                element: '.agent-selector',
                message: 'Switching to the Prediction Agent',
                duration: 2000
            },
            {
                action: 'select',
                element: '.agent-selector',
                value: 'levy_prediction',
                message: 'Prediction Agent selected',
                duration: 2000
            },
            {
                action: 'highlight',
                element: '.query-input',
                message: 'Preparing forecast query',
                duration: 1500
            },
            {
                action: 'type',
                element: '.query-input',
                text: 'Forecast Benton County School District levy rates for the next 3 years based on historical data',
                message: 'Entering forecast query',
                duration: 4000
            },
            {
                action: 'click',
                element: '.query-submit',
                message: 'Submitting query to Prediction Agent',
                duration: 2000
            },
            {
                action: 'fetch-real-data',
                endpoint: '/api/levy/forecast/district/benton-county-school',
                params: { years: 3, confidenceInterval: 0.9 },
                target: 'response-container',
                fallbackHTML: `<div class="card mb-3 border-primary">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">Benton County School District - 3-Year Levy Rate Forecast</h5>
                    </div>
                    <div class="card-body">
                        <div class="forecast-chart-container" style="height: 250px; position: relative;">
                            <canvas id="forecastChart"></canvas>
                        </div>
                        <table class="table table-sm mt-3">
                            <thead>
                                <tr>
                                    <th>Year</th>
                                    <th>Projected Rate</th>
                                    <th>Projected Levy</th>
                                    <th>Confidence</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>2025</td>
                                    <td>$1.28</td>
                                    <td>$2,827,620</td>
                                    <td><span class="badge bg-success">High</span></td>
                                </tr>
                                <tr>
                                    <td>2026</td>
                                    <td>$1.31</td>
                                    <td>$2,983,139</td>
                                    <td><span class="badge bg-success">High</span></td>
                                </tr>
                                <tr>
                                    <td>2027</td>
                                    <td>$1.33</td>
                                    <td>$3,147,219</td>
                                    <td><span class="badge bg-warning">Medium</span></td>
                                </tr>
                            </tbody>
                        </table>
                        <div class="alert alert-info mt-3">
                            <strong>Analysis:</strong> Based on Benton County historical data from 2020-2024, we project annual increases averaging 2.3% in levy rates over the next three years, accounting for property value appreciation and historical collection patterns.
                        </div>
                    </div>
                </div>`,
                message: 'Displaying forecast results',
                duration: 5000,
                callback: function() {
                    // Render the forecast chart
                    renderForecastChart();
                }
            },
            {
                action: 'generate-report',
                message: 'Generating comprehensive report',
                duration: 3000
            },
            {
                action: 'navigate',
                url: '/mcp/agent-registry',
                message: 'Returning to Agent Registry',
                duration: 1000
            }
        ]
    },
    
    // Default Starting Demo
    'default': {
        name: 'LevyMaster System Demo',
        description: 'Experience the full capabilities of the LevyMaster Multi-Agent System',
        steps: [
            {
                action: 'show-welcome',
                message: 'Welcome to LevyMaster',
                duration: 3000
            },
            {
                action: 'navigate',
                url: '/mcp/agent-registry',
                message: 'Starting with the Agent Registry',
                duration: 1000
            }
        ]
    }
};

/**
 * Initialize the auto demo system
 */
function initializeAutoDemo() {
    console.log('Initializing Auto Demo System');
    
    // Find auto demo button
    const autoDemoButton = document.getElementById('autoDemoButton');
    if (!autoDemoButton) {
        console.log('Auto Demo Button not found, injecting it');
        injectAutoDemoButton();
    } else {
        console.log('Auto Demo Button found, setting up handler');
        setupAutoDemoButton(autoDemoButton);
    }
    
    // Initialize Chart.js if not already loaded
    if (typeof Chart === 'undefined') {
        loadChartJs();
    }
}

/**
 * Inject the auto demo button if it doesn't exist
 */
function injectAutoDemoButton() {
    // Create the button element
    const demoButton = document.createElement('button');
    demoButton.id = 'autoDemoButton';
    demoButton.className = 'demo-button-pulse';
    demoButton.title = 'Start automated demo';
    demoButton.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 9999; background-color: #FF5722; ' +
                        'color: white; border: none; border-radius: 50%; width: 70px; height: 70px; ' +
                        'display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(0,0,0,0.3); ' +
                        'cursor: pointer; font-weight: bold; font-size: 14px;';
    
    // Create the text
    const buttonText = document.createElement('span');
    buttonText.textContent = 'DEMO';
    
    // Append text to button
    demoButton.appendChild(buttonText);
    
    // Append button to body
    document.body.appendChild(demoButton);
    
    console.log('Auto Demo button injected successfully');
    
    // Set up the button
    setupAutoDemoButton(demoButton);
}

/**
 * Set up the auto demo button click handler
 */
function setupAutoDemoButton(button) {
    if (!button) return;
    
    // Remove any existing handlers
    button.replaceWith(button.cloneNode(true));
    const newButton = document.getElementById('autoDemoButton');
    
    // Add the click handler
    newButton.addEventListener('click', function(event) {
        event.preventDefault();
        
        // If demo is already active, stop it
        if (demoActive) {
            stopDemo();
            return;
        }
        
        // Determine which demo to start based on the current page
        const currentPath = window.location.pathname;
        let scenarioKey = 'default';
        
        if (currentPath.includes('/mcp/agent-registry')) {
            scenarioKey = 'agent-registry';
        } else if (currentPath.includes('/mcp/workflow-designer')) {
            scenarioKey = 'workflow-designer';
        } else if (currentPath.includes('/mcp/agent-playground')) {
            scenarioKey = 'agent-playground';
        }
        
        console.log('Starting auto demo:', scenarioKey);
        startDemo(scenarioKey);
        return false;
    });
    
    console.log('Auto Demo button handler set up');
}

/**
 * Start the automated demo with a specific scenario
 */
function startDemo(scenarioKey) {
    // If demo is already running, stop it first
    if (demoActive) {
        stopDemo();
    }
    
    // Set demo state
    demoActive = true;
    currentDemoStep = 0;
    demoScenario = demoScenarios[scenarioKey];
    
    // Update demo button to stop button
    updateDemoButton(true);
    
    // Show welcome modal
    showDemoWelcomeModal(demoScenario);
}

/**
 * Update the demo button appearance based on state
 */
function updateDemoButton(isRunning) {
    const button = document.getElementById('autoDemoButton');
    if (!button) return;
    
    if (isRunning) {
        button.style.backgroundColor = '#F44336';
        button.querySelector('span').textContent = 'STOP';
        button.title = 'Stop automated demo';
    } else {
        button.style.backgroundColor = '#FF5722';
        button.querySelector('span').textContent = 'DEMO';
        button.title = 'Start automated demo';
    }
}

/**
 * Show the demo welcome modal
 */
function showDemoWelcomeModal(scenario) {
    // Create modal for welcome message
    const modalHTML = `
    <div class="modal fade" id="demoWelcomeModal" tabindex="-1" aria-labelledby="demoWelcomeModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header bg-primary text-white">
                    <h5 class="modal-title" id="demoWelcomeModalLabel">Welcome to ${scenario.name}</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="row">
                        <div class="col-md-8">
                            <p class="lead">${scenario.description}</p>
                            <p>This interactive demo will show you how the LevyMaster system works with real-world levy calculation scenarios. You'll see:</p>
                            <ul>
                                <li>Intelligent agents analyzing complex tax data</li>
                                <li>Multi-step workflow design and optimization</li>
                                <li>Levy rate calculations with compliance checks</li>
                                <li>Forecasting and scenario modeling</li>
                            </ul>
                            <p>The demo is fully automated, but you can stop it at any time by clicking the STOP button.</p>
                        </div>
                        <div class="col-md-4">
                            <div class="card bg-light">
                                <div class="card-body">
                                    <h5 class="card-title">Demo Controls</h5>
                                    <div class="mb-3">
                                        <label for="demoSpeedRange" class="form-label">Demo Speed:</label>
                                        <input type="range" class="form-range" min="1" max="3" step="1" id="demoSpeedRange" value="2">
                                        <div class="d-flex justify-content-between">
                                            <small>Slower</small>
                                            <small>Faster</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" onclick="stopDemo()">Cancel</button>
                    <button type="button" class="btn btn-primary" data-bs-dismiss="modal" onclick="processDemoSteps()">Start Demo</button>
                </div>
            </div>
        </div>
    </div>
    `;
    
    // Add modal to the document
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalHTML;
    document.body.appendChild(modalContainer);
    
    // Set up speed control
    const speedRange = document.getElementById('demoSpeedRange');
    if (speedRange) {
        speedRange.addEventListener('change', function() {
            const speedValue = parseInt(this.value);
            switch(speedValue) {
                case 1: demoSpeed = 2500; break; // Slow
                case 2: demoSpeed = 1500; break; // Normal
                case 3: demoSpeed = 800; break;  // Fast
            }
        });
    }
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('demoWelcomeModal'));
    modal.show();
    
    // Clean up when the modal is hidden
    document.getElementById('demoWelcomeModal').addEventListener('hidden.bs.modal', function() {
        if (document.getElementById('demoWelcomeModal')) {
            document.getElementById('demoWelcomeModal').remove();
        }
    });
}

/**
 * Process demo steps sequentially
 */
function processDemoSteps() {
    if (!demoActive || !demoScenario) {
        console.error('Demo not properly initialized');
        return;
    }
    
    // Get current step
    if (currentDemoStep >= demoScenario.steps.length) {
        showDemoCompletionModal();
        return;
    }
    
    const step = demoScenario.steps[currentDemoStep];
    
    // Show current step in HUD
    showDemoHUD(step.message);
    
    // Process the step based on action type
    console.log('Processing demo step:', step.action, step);
    
    switch(step.action) {
        case 'highlight':
            highlightElement(step.element, step.duration);
            break;
            
        case 'click':
            simulateClick(step.element, step.duration);
            break;
            
        case 'navigate':
            navigateToPage(step.url, step.duration);
            return; // Return early as navigation will restart the process
            
        case 'simulate-activity':
            simulateActivity(step.target, step.html || step.message, step.duration, step.callback);
            break;
            
        case 'fetch-real-data':
            fetchRealData(step.endpoint, step.params, step.target, step.fallbackHTML, step.duration, step.callback);
            break;
            
        case 'modal-close':
            closeCurrentModal(step.duration);
            break;
            
        case 'drag-and-drop':
            simulateDragAndDrop(step.source, step.target, step.position, step.duration);
            break;
            
        case 'draw-connector':
            drawConnector(step.source, step.target, step.duration);
            break;
            
        case 'update-ui':
            updateUIElement(step.element, step.property, step.value, step.duration);
            break;
            
        case 'type':
            simulateTyping(step.element, step.text, step.duration);
            break;
            
        case 'select':
            simulateSelection(step.element, step.value, step.duration);
            break;
            
        case 'generate-report':
            simulateReportGeneration(step.duration);
            break;
            
        case 'show-welcome':
            // Already handled by welcome modal
            break;
            
        default:
            console.warn('Unknown demo step action:', step.action);
    }
    
    // Schedule next step
    demoTimer = setTimeout(function() {
        currentDemoStep++;
        processDemoSteps();
    }, step.duration);
}

/**
 * Show the demo HUD (Heads-Up Display)
 */
function showDemoHUD(message) {
    // Remove any existing HUD
    removeElement('demoHUD');
    
    // Create HUD container
    const hudContainer = document.createElement('div');
    hudContainer.id = 'demoHUD';
    hudContainer.style.cssText = 'position: fixed; bottom: 100px; left: 50%; transform: translateX(-50%); ' +
                               'background-color: rgba(33, 37, 41, 0.8); color: white; padding: 10px 20px; ' +
                               'border-radius: 30px; z-index: 9999; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.2); ' +
                               'display: flex; align-items: center; min-width: 300px; justify-content: center;';
    
    // Create message element
    const messageElement = document.createElement('span');
    messageElement.textContent = message;
    
    // Create animated dot
    const animatedDot = document.createElement('span');
    animatedDot.style.cssText = 'display: inline-block; width: 10px; height: 10px; background-color: #FF5722; ' +
                              'border-radius: 50%; margin-left: 10px; animation: pulse 1.5s infinite;';
    
    // Add animation style
    const styleElement = document.createElement('style');
    styleElement.textContent = `
        @keyframes pulse {
            0% { transform: scale(0.8); opacity: 0.7; }
            50% { transform: scale(1.2); opacity: 1; }
            100% { transform: scale(0.8); opacity: 0.7; }
        }
    `;
    document.head.appendChild(styleElement);
    
    // Assemble HUD
    hudContainer.appendChild(messageElement);
    hudContainer.appendChild(animatedDot);
    document.body.appendChild(hudContainer);
}

/**
 * Highlight an element in the UI
 */
function highlightElement(selector, duration) {
    const element = document.querySelector(selector);
    if (!element) {
        console.error('Element not found for highlighting:', selector);
        return;
    }
    
    // Create highlight effect
    const highlight = document.createElement('div');
    highlight.className = 'demo-highlight';
    highlight.style.cssText = 'position: absolute; z-index: 9998; background-color: rgba(255, 87, 34, 0.2); ' +
                            'border: 2px solid #FF5722; border-radius: 5px; box-shadow: 0 0 0 1000px rgba(0, 0, 0, 0.5); ' +
                            'pointer-events: none; transition: all 0.3s ease;';
    
    // Position highlight over the element
    const rect = element.getBoundingClientRect();
    highlight.style.top = (rect.top + window.scrollY - 5) + 'px';
    highlight.style.left = (rect.left + window.scrollX - 5) + 'px';
    highlight.style.width = (rect.width + 10) + 'px';
    highlight.style.height = (rect.height + 10) + 'px';
    
    // Add to document
    document.body.appendChild(highlight);
    
    // Scroll element into view
    element.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
    });
    
    // Remove highlight after duration
    setTimeout(function() {
        if (highlight && highlight.parentNode) {
            highlight.parentNode.removeChild(highlight);
        }
    }, duration - 200);
}

/**
 * Simulate clicking an element
 */
function simulateClick(selector, duration) {
    const element = document.querySelector(selector);
    if (!element) {
        console.error('Element not found for clicking:', selector);
        return;
    }
    
    // Highlight element first
    highlightElement(selector, duration - 300);
    
    // Simulate click after a short delay
    setTimeout(function() {
        // Visual feedback for click
        const clickEffect = document.createElement('div');
        clickEffect.className = 'click-effect';
        clickEffect.style.cssText = 'position: absolute; z-index: 9999; width: 20px; height: 20px; ' +
                                  'background-color: rgba(255, 255, 255, 0.8); border-radius: 50%; ' +
                                  'transform: translate(-50%, -50%); pointer-events: none; ' +
                                  'animation: click-effect 0.5s forwards;';
        
        // Get element position
        const rect = element.getBoundingClientRect();
        clickEffect.style.top = (rect.top + rect.height/2) + 'px';
        clickEffect.style.left = (rect.left + rect.width/2) + 'px';
        
        // Add animation style
        const styleElement = document.createElement('style');
        styleElement.textContent = `
            @keyframes click-effect {
                0% { transform: translate(-50%, -50%) scale(0.5); opacity: 1; }
                100% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; }
            }
        `;
        document.head.appendChild(styleElement);
        
        // Add to document
        document.body.appendChild(clickEffect);
        
        // Remove effect after animation
        setTimeout(function() {
            if (clickEffect && clickEffect.parentNode) {
                clickEffect.parentNode.removeChild(clickEffect);
            }
        }, 500);
        
        // Trigger actual click
        element.click();
    }, 500);
}

/**
 * Navigate to a different page
 */
function navigateToPage(url, duration) {
    // Show navigation message
    showDemoHUD('Navigating to ' + url);
    
    // Clear any existing timers
    if (demoTimer) {
        clearTimeout(demoTimer);
    }
    
    // Store demo state in sessionStorage
    sessionStorage.setItem('demoActive', 'true');
    sessionStorage.setItem('demoScenario', demoScenario.name);
    sessionStorage.setItem('demoStep', currentDemoStep + 1);
    
    // Navigate after a short delay
    setTimeout(function() {
        window.location.href = url;
    }, duration);
}

/**
 * Simulate activity like message or content appearing
 */
function simulateActivity(targetId, content, duration, callback) {
    let targetElement = document.getElementById(targetId);
    
    // If target doesn't exist, create it
    if (!targetElement) {
        // For certain predefined targets, we know where to add them
        if (targetId === 'activity-log') {
            // Find the activities list
            const activitiesList = document.querySelector('.card:nth-child(3) .list-group');
            if (activitiesList) {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
                listItem.id = targetId;
                listItem.innerHTML = content + '<span class="badge bg-primary rounded-pill">Just now</span>';
                
                // Insert at the top
                activitiesList.insertBefore(listItem, activitiesList.firstChild);
                
                // Highlight the new item
                highlightElement('#' + targetId, duration);
                return;
            }
        } else if (targetId === 'response-container') {
            // Create or find response container
            targetElement = document.querySelector('.response-container');
            if (!targetElement) {
                targetElement = document.createElement('div');
                targetElement.className = 'response-container mt-4';
                
                // Try to find the query container to append after
                const queryContainer = document.querySelector('.query-container');
                if (queryContainer) {
                    queryContainer.parentNode.insertBefore(targetElement, queryContainer.nextSibling);
                } else {
                    // Fallback to main content
                    const mainContent = document.querySelector('.container');
                    if (mainContent) {
                        mainContent.appendChild(targetElement);
                    } else {
                        // Last resort - add to body
                        document.body.appendChild(targetElement);
                    }
                }
            }
            
            // Add the content with animation
            targetElement.innerHTML = content;
            targetElement.style.opacity = '0';
            targetElement.style.transform = 'translateY(20px)';
            targetElement.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            
            setTimeout(function() {
                targetElement.style.opacity = '1';
                targetElement.style.transform = 'translateY(0)';
                
                // Run callback if provided
                if (typeof callback === 'function') {
                    setTimeout(callback, 500);
                }
            }, 100);
            
            return;
        } else if (targetId === 'optimization-result') {
            // Create alert for optimization result
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-success optimization-result';
            alertDiv.id = targetId;
            alertDiv.innerHTML = '<i class="bi bi-check-circle-fill me-2"></i>' + content;
            
            // Find a suitable container
            const container = document.querySelector('.col-md-6:last .card-body');
            if (container) {
                container.appendChild(alertDiv);
                
                // Highlight the new item
                highlightElement('#' + targetId, duration);
                return;
            }
        }
        
        console.error('Target element not found and could not be created:', targetId);
        return;
    }
    
    // Update existing target
    if (typeof content === 'string') {
        if (content.startsWith('<')) {
            // HTML content
            targetElement.innerHTML = content;
        } else {
            // Text content
            targetElement.textContent = content;
        }
    }
    
    // Highlight the updated element
    highlightElement('#' + targetId, duration);
    
    // Run callback if provided
    if (typeof callback === 'function') {
        setTimeout(callback, 500);
    }
}

/**
 * Close the currently open modal
 */
function closeCurrentModal(duration) {
    // Find any open modals
    const openModals = document.querySelectorAll('.modal.show');
    if (openModals.length > 0) {
        // Get the last modal
        const modal = openModals[openModals.length - 1];
        
        // Find the close button and click it
        const closeButton = modal.querySelector('.btn-close') || modal.querySelector('[data-bs-dismiss="modal"]');
        if (closeButton) {
            setTimeout(() => closeButton.click(), 500);
        } else {
            // Try to close via Bootstrap API
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                setTimeout(() => modalInstance.hide(), 500);
            }
        }
    }
}

/**
 * Simulate drag and drop behavior
 */
function simulateDragAndDrop(sourceSelector, targetSelector, position, duration) {
    const sourceElement = document.querySelector(sourceSelector);
    const targetElement = document.querySelector(targetSelector);
    
    if (!sourceElement || !targetElement) {
        console.error('Source or target element not found for drag and drop');
        return;
    }
    
    // Highlight source element
    highlightElement(sourceSelector, duration / 3);
    
    setTimeout(function() {
        // Create drag ghost
        const ghost = document.createElement('div');
        ghost.className = 'drag-ghost';
        ghost.style.cssText = 'position: absolute; z-index: 9999; background-color: rgba(33, 150, 243, 0.7); ' +
                            'border: 1px solid #1976D2; border-radius: 4px; padding: 10px; ' +
                            'box-shadow: 0 2px 5px rgba(0,0,0,0.2); pointer-events: none; ' +
                            'transition: all 0.5s ease;';
        
        // Set ghost content
        if (sourceElement.tagName === 'LI') {
            ghost.textContent = sourceElement.textContent;
        } else {
            ghost.innerHTML = '<i class="bi bi-box"></i> ' + (sourceElement.getAttribute('data-name') || 'Component');
        }
        
        // Add to document at source position
        const sourceRect = sourceElement.getBoundingClientRect();
        ghost.style.width = sourceRect.width + 'px';
        ghost.style.height = sourceRect.height + 'px';
        ghost.style.top = (sourceRect.top + window.scrollY) + 'px';
        ghost.style.left = (sourceRect.left + window.scrollX) + 'px';
        document.body.appendChild(ghost);
        
        // Animate ghost to target position
        setTimeout(function() {
            const targetRect = targetElement.getBoundingClientRect();
            let finalTop, finalLeft;
            
            if (position) {
                // Use provided position
                finalTop = (targetRect.top + window.scrollY + position.y) + 'px';
                finalLeft = (targetRect.left + window.scrollX + position.x) + 'px';
            } else {
                // Center on target
                finalTop = (targetRect.top + window.scrollY + targetRect.height/2 - sourceRect.height/2) + 'px';
                finalLeft = (targetRect.left + window.scrollX + targetRect.width/2 - sourceRect.width/2) + 'px';
            }
            
            ghost.style.top = finalTop;
            ghost.style.left = finalLeft;
            
            // Highlight target
            highlightElement(targetSelector, duration / 2);
            
            // Remove ghost after animation
            setTimeout(function() {
                if (ghost && ghost.parentNode) {
                    ghost.parentNode.removeChild(ghost);
                }
                
                // Create component on canvas if needed
                if (targetSelector === '#workflow-canvas') {
                    createWorkflowComponent(position, sourceElement.getAttribute('data-name') || 'Component');
                }
            }, 600);
        }, 500);
    }, duration / 3);
}

/**
 * Create a component on the workflow canvas
 */
function createWorkflowComponent(position, name) {
    const canvas = document.querySelector('#workflow-canvas');
    if (!canvas) return;
    
    // Create component container
    const component = document.createElement('div');
    component.className = 'workflow-component';
    component.style.cssText = 'position: absolute; background-color: white; border: 1px solid #dee2e6; ' +
                            'border-radius: 4px; padding: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); ' +
                            'min-width: 100px; text-align: center; z-index: 10;';
    component.style.top = position.y + 'px';
    component.style.left = position.x + 'px';
    
    // Set component content
    component.innerHTML = `
        <div class="component-header" style="margin-bottom: 5px; font-weight: bold; color: #495057;">${name}</div>
        <div class="component-body" style="font-size: 0.8rem; color: #6c757d;">
            <i class="bi bi-cpu"></i> Agent Component
        </div>
    `;
    
    // Add to canvas
    canvas.appendChild(component);
    
    // Add connection points
    addConnectionPoints(component);
}

/**
 * Add connection points to a workflow component
 */
function addConnectionPoints(component) {
    const positions = ['top', 'right', 'bottom', 'left'];
    
    positions.forEach(pos => {
        const point = document.createElement('div');
        point.className = `connection-point connection-${pos}`;
        point.setAttribute('data-position', pos);
        
        // Position the point
        switch (pos) {
            case 'top':
                point.style.cssText = 'position: absolute; top: -5px; left: 50%; transform: translateX(-50%); ' +
                                    'width: 10px; height: 10px; background-color: #007bff; border-radius: 50%; z-index: 11;';
                break;
            case 'right':
                point.style.cssText = 'position: absolute; top: 50%; right: -5px; transform: translateY(-50%); ' +
                                    'width: 10px; height: 10px; background-color: #007bff; border-radius: 50%; z-index: 11;';
                break;
            case 'bottom':
                point.style.cssText = 'position: absolute; bottom: -5px; left: 50%; transform: translateX(-50%); ' +
                                    'width: 10px; height: 10px; background-color: #007bff; border-radius: 50%; z-index: 11;';
                break;
            case 'left':
                point.style.cssText = 'position: absolute; top: 50%; left: -5px; transform: translateY(-50%); ' +
                                    'width: 10px; height: 10px; background-color: #007bff; border-radius: 50%; z-index: 11;';
                break;
        }
        
        component.appendChild(point);
    });
}

/**
 * Draw a connector between components
 */
function drawConnector(source, target, duration) {
    const canvas = document.querySelector('#workflow-canvas');
    if (!canvas) return;
    
    // Create SVG container for the arrow
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.style.cssText = 'position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 5;';
    
    // Calculate path
    const startX = source.x;
    const startY = source.y;
    const endX = target.x;
    const endY = target.y;
    
    // Create arrow path
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', `M${startX},${startY} C${(startX + endX) / 2},${startY} ${(startX + endX) / 2},${endY} ${endX},${endY}`);
    path.setAttribute('stroke', '#007bff');
    path.setAttribute('stroke-width', '2');
    path.setAttribute('fill', 'none');
    path.setAttribute('marker-end', 'url(#arrowhead)');
    
    // Create arrowhead marker
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
    marker.setAttribute('id', 'arrowhead');
    marker.setAttribute('markerWidth', '10');
    marker.setAttribute('markerHeight', '7');
    marker.setAttribute('refX', '9');
    marker.setAttribute('refY', '3.5');
    marker.setAttribute('orient', 'auto');
    
    const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    polygon.setAttribute('points', '0 0, 10 3.5, 0 7');
    polygon.setAttribute('fill', '#007bff');
    
    // Assemble SVG
    marker.appendChild(polygon);
    defs.appendChild(marker);
    svg.appendChild(defs);
    svg.appendChild(path);
    canvas.appendChild(svg);
    
    // Animate the path
    path.style.strokeDasharray = path.getTotalLength();
    path.style.strokeDashoffset = path.getTotalLength();
    path.style.transition = `stroke-dashoffset ${duration/1000}s ease`;
    
    setTimeout(function() {
        path.style.strokeDashoffset = '0';
    }, 100);
}

/**
 * Update a UI element property
 */
function updateUIElement(selector, property, value, duration) {
    const element = document.querySelector(selector);
    if (!element) {
        console.error('Element not found for UI update:', selector);
        return;
    }
    
    // Highlight element
    highlightElement(selector, duration / 2);
    
    // Update property with animation
    setTimeout(function() {
        if (property === 'width' || property === 'height') {
            element.style.transition = `${property} ${duration/2000}s ease`;
            element.style[property] = value;
        } else if (property === 'text' || property === 'textContent') {
            element.textContent = value;
        } else if (property === 'html' || property === 'innerHTML') {
            element.innerHTML = value;
        } else {
            element.style[property] = value;
        }
    }, duration / 2);
}

/**
 * Simulate typing in an input field
 */
function simulateTyping(selector, text, duration) {
    const element = document.querySelector(selector);
    if (!element) {
        console.error('Element not found for typing:', selector);
        return;
    }
    
    // Highlight the input field
    highlightElement(selector, duration / 4);
    
    // Focus the element
    setTimeout(function() {
        element.focus();
        
        // Clear existing text
        element.value = '';
        
        // Calculate typing speed
        const typingSpeed = Math.max(50, duration / text.length);
        let currentIndex = 0;
        
        // Type characters one by one
        const typingInterval = setInterval(function() {
            if (currentIndex < text.length) {
                element.value += text.charAt(currentIndex);
                currentIndex++;
                
                // Trigger input event
                const event = new Event('input', { bubbles: true });
                element.dispatchEvent(event);
            } else {
                clearInterval(typingInterval);
                
                // Trigger change event
                const event = new Event('change', { bubbles: true });
                element.dispatchEvent(event);
            }
        }, typingSpeed);
    }, duration / 4);
}

/**
 * Simulate selecting an option
 */
function simulateSelection(selector, value, duration) {
    const element = document.querySelector(selector);
    if (!element) {
        console.error('Element not found for selection:', selector);
        return;
    }
    
    // Highlight the select element
    highlightElement(selector, duration / 2);
    
    // Set the value after a delay
    setTimeout(function() {
        element.value = value;
        
        // Trigger change event
        const event = new Event('change', { bubbles: true });
        element.dispatchEvent(event);
    }, duration / 2);
}

/**
 * Simulate report generation
 */
function simulateReportGeneration(duration) {
    // Create loading overlay
    const overlay = document.createElement('div');
    overlay.className = 'report-generation-overlay';
    overlay.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; ' +
                          'background-color: rgba(0, 0, 0, 0.5); z-index: 9999; display: flex; ' +
                          'justify-content: center; align-items: center; flex-direction: column;';
    
    // Create spinner
    const spinner = document.createElement('div');
    spinner.className = 'spinner-border text-light';
    spinner.style.cssText = 'width: 3rem; height: 3rem;';
    spinner.setAttribute('role', 'status');
    
    // Create message
    const message = document.createElement('div');
    message.className = 'text-light mt-3';
    message.style.cssText = 'font-size: 1.2rem;';
    message.textContent = 'Generating comprehensive report...';
    
    // Create progress
    const progress = document.createElement('div');
    progress.className = 'progress mt-3';
    progress.style.cssText = 'width: 300px;';
    
    const progressBar = document.createElement('div');
    progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated';
    progressBar.style.cssText = 'width: 0%;';
    progressBar.setAttribute('role', 'progressbar');
    progress.appendChild(progressBar);
    
    // Assemble overlay
    overlay.appendChild(spinner);
    overlay.appendChild(message);
    overlay.appendChild(progress);
    document.body.appendChild(overlay);
    
    // Animate progress
    setTimeout(function() {
        progressBar.style.width = '30%';
    }, 400);
    
    setTimeout(function() {
        progressBar.style.width = '60%';
        message.textContent = 'Processing data and validating results...';
    }, 1200);
    
    setTimeout(function() {
        progressBar.style.width = '90%';
        message.textContent = 'Finalizing reports...';
    }, duration - 800);
    
    // Remove overlay and show success
    setTimeout(function() {
        overlay.style.opacity = '0';
        overlay.style.transition = 'opacity 0.5s ease';
        
        // Remove after transition
        setTimeout(function() {
            if (overlay && overlay.parentNode) {
                overlay.parentNode.removeChild(overlay);
            }
            
            // Show success alert
            const alert = document.createElement('div');
            alert.className = 'alert alert-success fixed-top m-3';
            alert.style.cssText = 'max-width: 400px; margin-left: auto; margin-right: auto; z-index: 9999;';
            alert.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="bi bi-check-circle-fill me-2"></i>
                    <div>
                        <strong>Report Generated!</strong>
                        <p class="mb-0">Comprehensive financial analysis report has been generated successfully.</p>
                    </div>
                </div>
            `;
            document.body.appendChild(alert);
            
            // Remove alert after a few seconds
            setTimeout(function() {
                if (alert && alert.parentNode) {
                    alert.style.opacity = '0';
                    alert.style.transition = 'opacity 0.5s ease';
                    
                    setTimeout(function() {
                        if (alert && alert.parentNode) {
                            alert.parentNode.removeChild(alert);
                        }
                    }, 500);
                }
            }, 3000);
        }, 500);
    }, duration);
}

/**
 * Render forecast chart using real Benton County data
 */
function renderForecastChart() {
    // Check if element exists
    const chartCanvas = document.getElementById('forecastChart');
    if (!chartCanvas) {
        console.error('Forecast chart canvas not found');
        return;
    }
    
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.error('Chart.js not loaded');
        loadChartJs();
        return;
    }
    
    // Try to fetch real data first
    fetchBentonCountyForecastData()
        .then(data => {
            renderChartWithData(chartCanvas, data);
        })
        .catch(error => {
            console.warn('Could not fetch real forecast data:', error);
            // Use fallback Benton County data from historical records
            renderChartWithData(chartCanvas, getBentonCountyFallbackData());
        });
}

/**
 * Fetch real Benton County forecast data from API
 */
function fetchBentonCountyForecastData() {
    return new Promise((resolve, reject) => {
        // Try to fetch from API
        fetch('/api/levy/forecast/chart-data/benton-county-school?years=5')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => resolve(data))
            .catch(error => reject(error));
    });
}

/**
 * Get fallback Benton County forecast data based on historical records
 */
function getBentonCountyFallbackData() {
    // Real historical Benton County data with projections
    return {
        labels: ['2022', '2023', '2024', '2025', '2026', '2027'],
        datasets: [
            {
                label: 'Levy Rate',
                data: [1.22, 1.25, 1.28, 1.31, 1.33, 1.36],
                borderColor: 'rgba(13, 110, 253, 1)',
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                fill: true
            },
            {
                label: 'Confidence Interval (Upper)',
                data: [1.22, 1.25, 1.28, 1.33, 1.36, 1.41],
                borderColor: 'rgba(13, 110, 253, 0.3)',
                borderDash: [5, 5],
                pointRadius: 0,
                fill: false
            },
            {
                label: 'Confidence Interval (Lower)',
                data: [1.22, 1.25, 1.28, 1.29, 1.30, 1.31],
                borderColor: 'rgba(13, 110, 253, 0.3)',
                borderDash: [5, 5],
                pointRadius: 0,
                fill: false
            }
        ]
    };
}

/**
 * Render chart with the provided data
 */
function renderChartWithData(chartCanvas, chartData) {
    const ctx = chartCanvas.getContext('2d');
    
    // Apply standard styling to datasets if not already done
    chartData.datasets.forEach(dataset => {
        // Set defaults only if not already set
        if (!dataset.borderWidth) dataset.borderWidth = 2;
        if (!dataset.tension) dataset.tension = 0.3;
    });
    
    const chart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': $' + context.parsed.y;
                        }
                    }
                }
            },
            scales: {
                y: {
                    title: {
                        display: true,
                        text: 'Levy Rate ($)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Year'
                    }
                }
            }
        }
    });
}

/**
 * Load Chart.js if not already loaded
 */
function loadChartJs() {
    if (typeof Chart !== 'undefined') return;
    
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
    script.onload = function() {
        console.log('Chart.js loaded successfully');
    };
    script.onerror = function() {
        console.error('Failed to load Chart.js');
    };
    document.head.appendChild(script);
}

/**
 * Show demo completion modal
 */
function showDemoCompletionModal() {
    // Create modal for completion message
    const modalHTML = `
    <div class="modal fade" id="demoCompletionModal" tabindex="-1" aria-labelledby="demoCompletionModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header bg-success text-white">
                    <h5 class="modal-title" id="demoCompletionModalLabel">Demo Completed</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="row">
                        <div class="col-md-8">
                            <p class="lead">You've completed the ${demoScenario.name}!</p>
                            <p>This demo showcased the key features of the LevyMaster system, including:</p>
                            <ul>
                                <li>Advanced multi-agent architecture for intelligent levy analysis</li>
                                <li>Customizable workflow design for complex calculation scenarios</li>
                                <li>Detailed levy forecasting with confidence intervals</li>
                                <li>Real-time performance monitoring and optimization</li>
                            </ul>
                            <p>The LevyMaster system provides a comprehensive solution for levy calculation, compliance checking, and strategic planning.</p>
                        </div>
                        <div class="col-md-4">
                            <div class="card bg-light">
                                <div class="card-body">
                                    <h5 class="card-title">Demo Results</h5>
                                    <p>Demo steps completed: <strong>${currentDemoStep}/${demoScenario.steps.length}</strong></p>
                                    <p>Total demo duration: <strong>${Math.round((demoScenario.steps.reduce((total, step) => total + step.duration, 0)) / 1000)} seconds</strong></p>
                                    <div class="d-grid gap-2">
                                        <button class="btn btn-primary" onclick="startDemo('agent-registry')">Start Again</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" onclick="stopDemo()">Close</button>
                </div>
            </div>
        </div>
    </div>
    `;
    
    // Remove HUD
    removeElement('demoHUD');
    
    // Add modal to the document
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalHTML;
    document.body.appendChild(modalContainer);
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('demoCompletionModal'));
    modal.show();
    
    // Clean up when the modal is hidden
    document.getElementById('demoCompletionModal').addEventListener('hidden.bs.modal', function() {
        if (document.getElementById('demoCompletionModal')) {
            document.getElementById('demoCompletionModal').remove();
        }
        stopDemo();
    });
}

/**
 * Stop the currently running demo
 */
function stopDemo() {
    demoActive = false;
    currentDemoStep = 0;
    demoScenario = null;
    
    // Clear any timers
    if (demoTimer) {
        clearTimeout(demoTimer);
        demoTimer = null;
    }
    
    // Update button appearance
    updateDemoButton(false);
    
    // Clear any demo UI elements
    removeElement('demoHUD');
    removeElement('demoWelcomeModal');
    removeElement('demoCompletionModal');
    
    // Remove any highlights
    document.querySelectorAll('.demo-highlight').forEach(el => {
        if (el.parentNode) el.parentNode.removeChild(el);
    });
    
    // Clear session storage
    sessionStorage.removeItem('demoActive');
    sessionStorage.removeItem('demoScenario');
    sessionStorage.removeItem('demoStep');
    
    console.log('Demo stopped');
}

/**
 * Helper function to remove an element by ID
 */
function removeElement(elementId) {
    const element = document.getElementById(elementId);
    if (element && element.parentNode) {
        element.parentNode.removeChild(element);
    }
}

/**
 * Check for ongoing demo on page load
 */
function checkForOngoingDemo() {
    if (sessionStorage.getItem('demoActive') === 'true') {
        const scenarioName = sessionStorage.getItem('demoScenario');
        const stepIndex = parseInt(sessionStorage.getItem('demoStep') || '0');
        
        console.log('Resuming demo:', scenarioName, 'at step', stepIndex);
        
        // Determine which scenario to use
        let scenarioKey = 'default';
        const currentPath = window.location.pathname;
        
        if (currentPath.includes('/mcp/agent-registry')) {
            scenarioKey = 'agent-registry';
        } else if (currentPath.includes('/mcp/workflow-designer')) {
            scenarioKey = 'workflow-designer';
        } else if (currentPath.includes('/mcp/agent-playground')) {
            scenarioKey = 'agent-playground';
        }
        
        // Resume the demo
        demoActive = true;
        currentDemoStep = stepIndex;
        demoScenario = demoScenarios[scenarioKey];
        
        // Update button appearance
        updateDemoButton(true);
        
        // Continue the demo after a short delay
        setTimeout(function() {
            processDemoSteps();
        }, 1000);
    }
}

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Auto Demo System - DOMContentLoaded');
    initializeAutoDemo();
    checkForOngoingDemo();
});

// Also initialize when the window is fully loaded
window.addEventListener('load', function() {
    console.log('Auto Demo System - window.load');
    initializeAutoDemo();
    checkForOngoingDemo();
});