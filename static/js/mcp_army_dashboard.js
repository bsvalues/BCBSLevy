/**
 * MCP Army Dashboard JavaScript
 * 
 * This script provides the frontend functionality for the MCP Army Dashboard,
 * including real-time updates, data visualization, agent management, and workflow execution.
 */

// Global state
const state = {
    agents: [],
    commandStructure: {},
    agentRelationships: {},
    experiences: {},
    experienceStats: {},
    helpRequests: 0,
    notificationCount: 0
};

// DOM Elements
const elements = {
    // Status cards
    totalAgents: null, // Will be initialized during runtime
    activeAgents: null, // Will be initialized during runtime
    helpRequests: document.getElementById('help-request-count'),
    
    // Agent elements
    agentCards: null, // Will be initialized during runtime
    requestHelpButtons: null, // Will be initialized during runtime
    
    // Experience elements
    experienceStats: document.getElementById('experience-stats'),
    recentExperiences: document.getElementById('recent-experiences'),
    startTrainingBtn: document.getElementById('start-training-btn'),
    
    // Activity feed
    activityFeed: document.getElementById('activity-feed'),
    clearNotificationsBtn: document.getElementById('clear-notifications-btn'),
    
    // Modals
    agentDetailsModal: document.getElementById('agentDetailsModal'),
    agentDetailsContent: document.getElementById('agentDetailsContent'),
    workflowModal: document.getElementById('workflowModal'),
    workflowForm: document.getElementById('workflowForm'),
    workflowName: document.getElementById('workflowName'),
    executeWorkflowBtn: document.getElementById('executeWorkflowBtn'),
    
    // Visualization
    commandStructureDiagram: document.getElementById('command-structure-diagram'),
    communicationGraph: document.getElementById('communication-graph')
};

/**
 * Initialize the dashboard
 */
function initDashboard() {
    console.log('MCP Army Dashboard initializing...');
    
    try {
        // Load initial data
        fetchCommandStructure();
        fetchAgents();
        fetchExperienceStats();
        
        // Set up event listeners
        setupEventListeners();
        
        // Set up polling for updates
        setInterval(refreshDashboard, 30000); // Refresh every 30 seconds
        
        console.log('MCP Army Dashboard initialized');
    } catch (error) {
        console.error('Error initializing MCP Army Dashboard:', error);
    }
}

/**
 * Set up event listeners for dashboard interactivity
 */
function setupEventListeners() {
    // Agent card clicks
    document.querySelectorAll('.agent-card').forEach(card => {
        card.addEventListener('click', function() {
            const agentId = this.dataset.agentId;
            showAgentDetails(agentId);
        });
    });
    
    // Request help buttons
    document.querySelectorAll('.request-help-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation(); // Prevent triggering the card click
            const agentId = this.dataset.agentId;
            requestHelp(agentId);
        });
    });
    
    // Start training button
    document.getElementById('start-training-btn')?.addEventListener('click', startTraining);
    
    // Clear notifications button
    document.getElementById('clear-notifications-btn')?.addEventListener('click', clearNotifications);
    
    // Workflow buttons
    document.querySelectorAll('.workflow-btn').forEach(button => {
        button.addEventListener('click', function() {
            const workflowName = this.dataset.workflow;
            openWorkflowModal(workflowName);
        });
    });
    
    // Execute workflow button
    document.getElementById('executeWorkflowBtn')?.addEventListener('click', executeWorkflow);
}

/**
 * Fetch the command structure from the API
 */
function fetchCommandStructure() {
    fetch('/mcp-army/api/command-structure')
        .then(response => response.json())
        .then(data => {
            state.commandStructure = data.command_structure || {};
            state.agentRelationships = data.agent_relationships || {};
            console.log('Command structure loaded:', state.commandStructure);
            
            // Initialize the communication graph
            initCommunicationGraph();
        })
        .catch(error => {
            console.error('Error fetching command structure:', error);
            showToast('error', 'Error', 'Failed to load command structure. Try refreshing the page.');
        });
}

/**
 * Fetch agents from the API
 */
function fetchAgents() {
    fetch('/mcp-army/api/agents')
        .then(response => response.json())
        .then(data => {
            state.agents = data.agents || [];
            console.log('Agents loaded:', state.agents.length);
            
            // Update the agent count displays
            // Find all elements with class 'card-title' that contain 'Total Agents'
            document.querySelectorAll('.card-title').forEach(el => {
                if (el.textContent.includes('Total Agents')) {
                    const displayElement = el.nextElementSibling;
                    if (displayElement && displayElement.classList.contains('display-4')) {
                        displayElement.textContent = state.agents.length;
                    }
                }
            });
            
            const activeAgents = state.agents.filter(agent => agent.status.status === 'active');
            // Find all elements with class 'card-title' that contain 'Active Agents'
            document.querySelectorAll('.card-title').forEach(el => {
                if (el.textContent.includes('Active Agents')) {
                    const displayElement = el.nextElementSibling;
                    if (displayElement && displayElement.classList.contains('display-4')) {
                        displayElement.textContent = activeAgents.length;
                    }
                }
            });
            
            // Update agent cards
            updateAgentCards();
        })
        .catch(error => {
            console.error('Error fetching agents:', error);
            showToast('error', 'Error', 'Failed to load agents. Try refreshing the page.');
        });
}

/**
 * Fetch experience stats from the API
 */
function fetchExperienceStats() {
    fetch('/mcp-army/api/experiences/stats')
        .then(response => response.json())
        .then(data => {
            state.experienceStats = data;
            console.log('Experience stats loaded:', state.experienceStats);
            
            // Update the experience stats display
            updateExperienceStatsDisplay();
            
            // Fetch recent experiences for all agents
            if (state.agents && state.agents.length > 0) {
                fetchRecentExperiences(state.agents[0].agent_id);
            }
        })
        .catch(error => {
            console.error('Error fetching experience stats:', error);
            showToast('error', 'Error', 'Failed to load experience statistics.');
        });
}

/**
 * Fetch recent experiences for a specific agent
 */
function fetchRecentExperiences(agentId) {
    fetch(`/mcp-army/api/agents/${agentId}/experiences?limit=5`)
        .then(response => response.json())
        .then(data => {
            state.experiences[agentId] = data.experiences || [];
            console.log(`Experiences loaded for ${agentId}:`, state.experiences[agentId].length);
            
            // Update the recent experiences table
            updateRecentExperiencesDisplay();
        })
        .catch(error => {
            console.error(`Error fetching experiences for ${agentId}:`, error);
            showToast('error', 'Error', `Failed to load experiences for ${agentId}.`);
        });
}

/**
 * Update the agent cards with current data
 */
function updateAgentCards() {
    const agentContainer = document.querySelector('.agent-status .row');
    if (!agentContainer) return;
    
    // Clear existing cards
    agentContainer.innerHTML = '';
    
    // Create cards for each agent
    state.agents.forEach(agent => {
        const performance = agent.status.performance || { overall: 0.5 };
        const perfPercent = Math.round((performance.overall || 0.5) * 100);
        
        const card = document.createElement('div');
        card.className = 'col-md-6';
        card.innerHTML = `
            <div class="card agent-card" data-agent-id="${agent.agent_id}">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <span>${agent.agent_id}</span>
                    <span class="badge status-${agent.status.status || 'idle'} agent-status">${agent.status.status || 'idle'}</span>
                </div>
                <div class="card-body">
                    <p><strong>Type:</strong> ${agent.type || 'Unknown'}</p>
                    <p><strong>Role:</strong> ${agent.role || 'Agent'}</p>
                    <div class="d-flex justify-content-between mb-1">
                        <span>Performance:</span>
                        <span>${perfPercent}%</span>
                    </div>
                    <div class="performance-indicator">
                        <div class="performance-bar" style="width: ${perfPercent}%;"></div>
                    </div>
                    <div class="mt-3">
                        <button class="btn btn-sm btn-outline-secondary request-help-btn" data-agent-id="${agent.agent_id}">Request Help</button>
                    </div>
                </div>
            </div>
        `;
        
        agentContainer.appendChild(card);
    });
    
    // Re-attach event listeners
    document.querySelectorAll('.agent-card').forEach(card => {
        card.addEventListener('click', function() {
            const agentId = this.dataset.agentId;
            showAgentDetails(agentId);
        });
    });
    
    document.querySelectorAll('.request-help-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation(); // Prevent triggering the card click
            const agentId = this.dataset.agentId;
            requestHelp(agentId);
        });
    });
}

/**
 * Update the experience stats display
 */
function updateExperienceStatsDisplay() {
    const statsElement = document.getElementById('experience-stats');
    if (!statsElement) return;
    
    const stats = state.experienceStats;
    
    statsElement.innerHTML = `
        <div class="row">
            <div class="col-6">
                <div class="text-center">
                    <h3 class="display-4">${stats.total_experiences || 0}</h3>
                    <p class="text-muted">Total Experiences</p>
                </div>
            </div>
            <div class="col-6">
                <div class="text-center">
                    <h3 class="display-4">${Math.round((stats.utilization || 0) * 100)}%</h3>
                    <p class="text-muted">Utilization</p>
                </div>
            </div>
        </div>
        <div class="mt-3">
            <p><strong>Most Recent:</strong> ${formatDate(stats.most_recent)}</p>
        </div>
    `;
}

/**
 * Update the recent experiences display
 */
function updateRecentExperiencesDisplay() {
    const tableBody = document.getElementById('recent-experiences');
    if (!tableBody) return;
    
    // Clear existing rows
    tableBody.innerHTML = '';
    
    // Gather all experiences from all agents
    const allExperiences = [];
    Object.keys(state.experiences).forEach(agentId => {
        state.experiences[agentId].forEach(exp => {
            allExperiences.push({
                agentId,
                ...exp
            });
        });
    });
    
    // Sort by timestamp, newest first
    allExperiences.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    // Take the 5 most recent
    const recentExperiences = allExperiences.slice(0, 5);
    
    if (recentExperiences.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="3" class="text-center">No experiences recorded</td></tr>';
        return;
    }
    
    // Create a row for each experience
    recentExperiences.forEach(exp => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${exp.agentId}</td>
            <td>${formatEventType(exp.eventType)}</td>
            <td>${formatTimeAgo(exp.timestamp)}</td>
        `;
        tableBody.appendChild(row);
    });
}

/**
 * Initialize the communication graph visualization
 */
function initCommunicationGraph() {
    const graphElement = document.getElementById('communication-graph');
    if (!graphElement || !state.commandStructure || !state.agentRelationships) return;
    
    // Example implementation using a simple div-based visualization
    // In a real application, you might want to use a library like D3.js or vis.js
    
    graphElement.innerHTML = '<div class="p-3 text-center">Communication Graph Visualization<br>(Placeholder for visualization library)</div>';
    
    // Add a basic representation of the command structure
    const structureDiv = document.createElement('div');
    structureDiv.className = 'mt-3 p-3 border rounded';
    
    let structureHTML = '<div class="fw-bold mb-2">Command Structure:</div>';
    
    // Add architect prime
    if (state.commandStructure.architect_prime) {
        structureHTML += `<div class="mb-2">Architect Prime: ${state.commandStructure.architect_prime}</div>`;
    }
    
    // Add integration coordinator
    if (state.commandStructure.integration_coordinator) {
        structureHTML += `<div class="mb-2">Integration Coordinator: ${state.commandStructure.integration_coordinator}</div>`;
    }
    
    // Add component leads
    if (state.commandStructure.component_leads) {
        structureHTML += '<div class="mb-2">Component Leads:</div><ul>';
        Object.entries(state.commandStructure.component_leads).forEach(([component, lead]) => {
            structureHTML += `<li>${component}: ${lead}</li>`;
        });
        structureHTML += '</ul>';
    }
    
    // Add specialist agents
    if (state.commandStructure.specialist_agents) {
        structureHTML += '<div class="mb-2">Specialist Agents:</div><ul>';
        Object.entries(state.commandStructure.specialist_agents).forEach(([domain, agents]) => {
            structureHTML += `<li>${domain}: ${agents.join(', ')}</li>`;
        });
        structureHTML += '</ul>';
    }
    
    structureDiv.innerHTML = structureHTML;
    graphElement.appendChild(structureDiv);
}

/**
 * Show details for a specific agent in a modal
 */
function showAgentDetails(agentId) {
    console.log('Showing details for agent:', agentId);
    
    const modal = document.getElementById('agentDetailsModal');
    const contentElement = document.getElementById('agentDetailsContent');
    
    if (!modal || !contentElement) return;
    
    contentElement.innerHTML = '<p>Loading agent details...</p>';
    
    // Show the modal
    $(modal).modal('show');
    
    // Fetch agent details
    fetch(`/mcp-army/api/agents/${agentId}`)
        .then(response => response.json())
        .then(agent => {
            console.log('Agent details loaded:', agent);
            
            // Format the content
            let html = `
                <div class="mb-4">
                    <h4>${agent.agent_id}</h4>
                    <span class="badge status-${agent.status.status || 'idle'}">${agent.status.status || 'idle'}</span>
                </div>
                
                <div class="row mb-4">
                    <div class="col-md-6">
                        <h5>Basic Information</h5>
                        <table class="table table-sm">
                            <tr>
                                <th>Type</th>
                                <td>${agent.type || 'Unknown'}</td>
                            </tr>
                            <tr>
                                <th>Role</th>
                                <td>${agent.role || 'Agent'}</td>
                            </tr>
                            <tr>
                                <th>Domain</th>
                                <td>${agent.domain || 'General'}</td>
                            </tr>
                            <tr>
                                <th>Component</th>
                                <td>${agent.component || 'Default'}</td>
                            </tr>
                            <tr>
                                <th>Last Updated</th>
                                <td>${formatDate(agent.status.last_updated)}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <div class="col-md-6">
                        <h5>Performance Metrics</h5>
                        <table class="table table-sm">
                            <tr>
                                <th>Overall Performance</th>
                                <td>${Math.round((agent.status.performance?.overall || 0) * 100)}%</td>
                            </tr>
                            <tr>
                                <th>Task Success Rate</th>
                                <td>${Math.round((agent.status.performance?.task_success_rate || 0) * 100)}%</td>
                            </tr>
                            <tr>
                                <th>Response Time</th>
                                <td>${agent.status.performance?.response_time || 0} ms</td>
                            </tr>
                            <tr>
                                <th>Error Rate</th>
                                <td>${Math.round((agent.status.performance?.error_rate || 0) * 100)}%</td>
                            </tr>
                        </table>
                    </div>
                </div>
                
                <div class="mb-4">
                    <h5>Capabilities</h5>
                    <div class="row">
            `;
            
            // Add capabilities buttons
            if (agent.capabilities && agent.capabilities.length > 0) {
                agent.capabilities.forEach(capability => {
                    html += `
                        <div class="col-md-6 mb-2">
                            <button class="btn btn-sm btn-outline-primary w-100 text-start capability-btn" 
                                    data-agent-id="${agent.agent_id}" 
                                    data-capability="${capability}">
                                ${formatCapabilityName(capability)}
                            </button>
                        </div>
                    `;
                });
            } else {
                html += '<div class="col-12"><p class="text-muted">No capabilities listed</p></div>';
            }
            
            html += `
                    </div>
                </div>
                
                <div class="mb-4">
                    <h5>Recent Experiences</h5>
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Event Type</th>
                                    <th>Time</th>
                                    <th>Outcome</th>
                                </tr>
                            </thead>
                            <tbody id="agent-experiences-${agentId}">
                                <tr>
                                    <td colspan="3" class="text-center">Loading experiences...</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="d-flex">
                    <button class="btn btn-primary me-2 execute-capability-btn" data-agent-id="${agent.agent_id}">
                        Execute Capability
                    </button>
                    <button class="btn btn-outline-secondary request-help-btn" data-agent-id="${agent.agent_id}">
                        Request Help
                    </button>
                </div>
            `;
            
            // Update the modal content
            contentElement.innerHTML = html;
            
            // Attach event listeners
            document.querySelectorAll('.capability-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const agentId = this.dataset.agentId;
                    const capability = this.dataset.capability;
                    executeCapability(agentId, capability);
                });
            });
            
            document.querySelectorAll('.execute-capability-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const agentId = this.dataset.agentId;
                    showCapabilitySelector(agentId);
                });
            });
            
            // Load experiences for this agent
            fetchAgentExperiences(agentId);
        })
        .catch(error => {
            console.error(`Error fetching details for agent ${agentId}:`, error);
            contentElement.innerHTML = `<div class="alert alert-danger">Error loading agent details. Please try again.</div>`;
        });
}

/**
 * Fetch experiences for a specific agent
 */
function fetchAgentExperiences(agentId) {
    const tableBody = document.getElementById(`agent-experiences-${agentId}`);
    if (!tableBody) return;
    
    fetch(`/mcp-army/api/agents/${agentId}/experiences?limit=5`)
        .then(response => response.json())
        .then(data => {
            const experiences = data.experiences || [];
            
            // Update the state
            state.experiences[agentId] = experiences;
            
            // Clear the table
            tableBody.innerHTML = '';
            
            if (experiences.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="3" class="text-center">No experiences recorded</td></tr>';
                return;
            }
            
            // Add a row for each experience
            experiences.forEach(exp => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${formatEventType(exp.eventType)}</td>
                    <td>${formatTimeAgo(exp.timestamp)}</td>
                    <td>${exp.details?.outcome || 'N/A'}</td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error(`Error fetching experiences for agent ${agentId}:`, error);
            tableBody.innerHTML = '<tr><td colspan="3" class="text-center text-danger">Error loading experiences</td></tr>';
        });
}

/**
 * Show a selector for agent capabilities
 */
function showCapabilitySelector(agentId) {
    // Find the agent
    const agent = state.agents.find(a => a.agent_id === agentId);
    if (!agent || !agent.capabilities || agent.capabilities.length === 0) {
        showToast('warning', 'No Capabilities', `Agent ${agentId} has no registered capabilities.`);
        return;
    }
    
    // Create a modal for capability selection
    const modalHTML = `
        <div class="modal fade" id="capabilitySelectorModal" tabindex="-1" role="dialog" aria-hidden="true">
            <div class="modal-dialog" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Select Capability</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <p>Select a capability to execute for agent <strong>${agentId}</strong>:</p>
                        <div class="list-group">
                            ${agent.capabilities.map(capability => `
                                <button type="button" class="list-group-item list-group-item-action capability-select-btn"
                                        data-agent-id="${agentId}" data-capability="${capability}">
                                    ${formatCapabilityName(capability)}
                                </button>
                            `).join('')}
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add the modal to the document
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalHTML;
    document.body.appendChild(modalContainer);
    
    // Initialize the modal
    const modal = document.getElementById('capabilitySelectorModal');
    $(modal).modal('show');
    
    // Add event listeners
    document.querySelectorAll('.capability-select-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const agentId = this.dataset.agentId;
            const capability = this.dataset.capability;
            $(modal).modal('hide');
            
            // Execute the capability
            executeCapability(agentId, capability);
            
            // Remove the modal after hiding
            $(modal).on('hidden.bs.modal', function() {
                document.body.removeChild(modalContainer);
            });
        });
    });
    
    // Remove the modal when hidden
    $(modal).on('hidden.bs.modal', function() {
        document.body.removeChild(modalContainer);
    });
}

/**
 * Execute a capability for a specific agent
 */
function executeCapability(agentId, capability) {
    console.log(`Executing capability ${capability} for agent ${agentId}`);
    
    // Show toast
    showToast('info', 'Executing Capability', `Requesting ${formatCapabilityName(capability)} from ${agentId}...`);
    
    // Create a parameters modal
    const modalHTML = `
        <div class="modal fade" id="capabilityParamsModal" tabindex="-1" role="dialog" aria-hidden="true">
            <div class="modal-dialog" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Capability Parameters</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <p>Provide parameters for <strong>${formatCapabilityName(capability)}</strong>:</p>
                        <form id="capabilityParamsForm">
                            <div class="form-group">
                                <label for="capabilityParams">Parameters (JSON):</label>
                                <textarea class="form-control" id="capabilityParams" rows="5">{}</textarea>
                                <small class="form-text text-muted">Enter parameters as a valid JSON object</small>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="executeCapabilityBtn">Execute</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add the modal to the document
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalHTML;
    document.body.appendChild(modalContainer);
    
    // Initialize the modal
    const modal = document.getElementById('capabilityParamsModal');
    $(modal).modal('show');
    
    // Execute button handler
    document.getElementById('executeCapabilityBtn')?.addEventListener('click', function() {
        const paramsText = document.getElementById('capabilityParams')?.value || '{}';
        let params;
        
        try {
            params = JSON.parse(paramsText);
        } catch (error) {
            showToast('error', 'Invalid JSON', 'Please provide a valid JSON object for parameters.');
            return;
        }
        
        // Hide the modal
        $(modal).modal('hide');
        
        // Make the API call
        fetch(`/mcp-army/api/agents/${agentId}/capabilities/${capability}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        })
        .then(response => response.json())
        .then(result => {
            console.log('Capability execution result:', result);
            
            // Show success toast
            showToast('success', 'Capability Executed', `Successfully executed ${formatCapabilityName(capability)}.`);
            
            // Show the result in a modal
            showResultModal('Capability Result', result);
            
            // Add a notification to the activity feed
            addNotification('capability', `Agent ${agentId} executed ${formatCapabilityName(capability)}`);
        })
        .catch(error => {
            console.error(`Error executing capability ${capability} for agent ${agentId}:`, error);
            showToast('error', 'Execution Failed', `Failed to execute ${formatCapabilityName(capability)}.`);
        });
        
        // Remove the modal after hiding
        $(modal).on('hidden.bs.modal', function() {
            document.body.removeChild(modalContainer);
        });
    });
    
    // Remove the modal when hidden
    $(modal).on('hidden.bs.modal', function() {
        document.body.removeChild(modalContainer);
    });
}

/**
 * Show a result modal with JSON data
 */
function showResultModal(title, data) {
    // Create the modal HTML
    const modalHTML = `
        <div class="modal fade" id="resultModal" tabindex="-1" role="dialog" aria-hidden="true">
            <div class="modal-dialog modal-lg" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <pre class="result-json">${JSON.stringify(data, null, 2)}</pre>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add the modal to the document
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalHTML;
    document.body.appendChild(modalContainer);
    
    // Initialize the modal
    const modal = document.getElementById('resultModal');
    $(modal).modal('show');
    
    // Remove the modal when hidden
    $(modal).on('hidden.bs.modal', function() {
        document.body.removeChild(modalContainer);
    });
}

/**
 * Request help for an agent
 */
function requestHelp(agentId) {
    console.log('Requesting help for agent:', agentId);
    
    // Find suitable agents to help
    const helpers = state.agents.filter(agent => agent.agent_id !== agentId);
    
    if (helpers.length === 0) {
        showToast('warning', 'No Helpers', 'No other agents are available to help.');
        return;
    }
    
    // Create a modal for selecting a helper agent
    const modalHTML = `
        <div class="modal fade" id="helperSelectorModal" tabindex="-1" role="dialog" aria-hidden="true">
            <div class="modal-dialog" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Request Help</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <p>Select an agent to help <strong>${agentId}</strong>:</p>
                        <div class="list-group">
                            ${helpers.map(helper => `
                                <button type="button" class="list-group-item list-group-item-action helper-select-btn"
                                        data-agent-id="${agentId}" data-helper-id="${helper.agent_id}">
                                    ${helper.agent_id} (${helper.role || 'Agent'})
                                </button>
                            `).join('')}
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add the modal to the document
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalHTML;
    document.body.appendChild(modalContainer);
    
    // Initialize the modal
    const modal = document.getElementById('helperSelectorModal');
    $(modal).modal('show');
    
    // Add event listeners
    document.querySelectorAll('.helper-select-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const agentId = this.dataset.agentId;
            const helperId = this.dataset.helperId;
            $(modal).modal('hide');
            
            // Submit the help request
            submitHelpRequest(agentId, helperId);
            
            // Remove the modal after hiding
            $(modal).on('hidden.bs.modal', function() {
                document.body.removeChild(modalContainer);
            });
        });
    });
    
    // Remove the modal when hidden
    $(modal).on('hidden.bs.modal', function() {
        document.body.removeChild(modalContainer);
    });
}

/**
 * Submit a help request to the API
 */
function submitHelpRequest(agentId, helperId) {
    console.log(`Requesting help from ${helperId} for ${agentId}`);
    
    // Show toast
    showToast('info', 'Requesting Help', `Requesting assistance from ${helperId} for ${agentId}...`);
    
    // Make the API call
    fetch(`/mcp-army/api/agents/${helperId}/assistance/${agentId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            assistance_type: 'general'
        })
    })
    .then(response => response.json())
    .then(result => {
        console.log('Help request result:', result);
        
        // Show success toast
        showToast('success', 'Help Requested', `Successfully requested help from ${helperId}.`);
        
        // Increment help request count
        state.helpRequests++;
        document.getElementById('help-request-count').textContent = state.helpRequests;
        
        // Add a notification to the activity feed
        addNotification('assistance', `Agent ${helperId} is assisting ${agentId}`);
    })
    .catch(error => {
        console.error(`Error requesting help from ${helperId} for ${agentId}:`, error);
        showToast('error', 'Request Failed', `Failed to request help from ${helperId}.`);
    });
}

/**
 * Start a training cycle
 */
function startTraining() {
    console.log('Starting training cycle');
    
    // Show toast
    showToast('info', 'Training', 'Starting training cycle...');
    
    // Make the API call
    fetch('/mcp-army/api/training/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            batch_size: 32
        })
    })
    .then(response => response.json())
    .then(result => {
        console.log('Training result:', result);
        
        // Show success toast
        showToast('success', 'Training Started', 'Successfully started training cycle.');
        
        // Add a notification to the activity feed
        addNotification('training', 'Started agent training cycle');
    })
    .catch(error => {
        console.error('Error starting training:', error);
        showToast('error', 'Training Failed', 'Failed to start training cycle.');
    });
}

/**
 * Open the workflow execution modal
 */
function openWorkflowModal(workflowName) {
    console.log('Opening workflow modal for:', workflowName);
    
    // Set the workflow name
    document.getElementById('workflowName').value = workflowName;
    
    // Update the modal title
    document.getElementById('workflowModalLabel').textContent = `Execute ${formatWorkflowName(workflowName)} Workflow`;
    
    // Show the modal
    $('#workflowModal').modal('show');
}

/**
 * Execute a workflow
 */
function executeWorkflow() {
    const workflowName = document.getElementById('workflowName').value;
    const taxDistrictId = document.getElementById('taxDistrictId').value;
    const year = document.getElementById('year').value;
    const additionalParamsText = document.getElementById('additionalParams').value;
    
    console.log(`Executing workflow ${workflowName} for district ${taxDistrictId} in year ${year}`);
    
    if (!workflowName) {
        showToast('error', 'Validation Error', 'Workflow name is required.');
        return;
    }
    
    if (!taxDistrictId) {
        showToast('error', 'Validation Error', 'Tax district is required.');
        return;
    }
    
    // Parse additional parameters if provided
    let additionalParams = {};
    if (additionalParamsText.trim()) {
        try {
            additionalParams = JSON.parse(additionalParamsText);
        } catch (error) {
            showToast('error', 'Invalid JSON', 'Additional parameters must be valid JSON.');
            return;
        }
    }
    
    // Hide the modal
    $('#workflowModal').modal('hide');
    
    // Show a loading toast
    showToast('info', 'Executing Workflow', `Executing ${formatWorkflowName(workflowName)} workflow...`);
    
    // Prepare the parameters
    const params = {
        workflow_name: workflowName,
        parameters: {
            district_id: parseInt(taxDistrictId, 10),
            year: parseInt(year, 10),
            ...additionalParams
        }
    };
    
    // Make the API call
    fetch('/mcp-army/api/workflows/collaborative', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
    })
    .then(response => response.json())
    .then(result => {
        console.log('Workflow execution result:', result);
        
        // Show success toast
        showToast('success', 'Workflow Completed', `Successfully executed ${formatWorkflowName(workflowName)} workflow.`);
        
        // Show the result in a modal
        showResultModal('Workflow Result', result);
        
        // Add a notification to the activity feed
        addNotification('workflow', `Executed ${formatWorkflowName(workflowName)} workflow`);
    })
    .catch(error => {
        console.error(`Error executing workflow ${workflowName}:`, error);
        showToast('error', 'Execution Failed', `Failed to execute ${formatWorkflowName(workflowName)} workflow.`);
    });
}

/**
 * Clear all notifications from the activity feed
 */
function clearNotifications() {
    const activityFeed = document.getElementById('activity-feed');
    if (!activityFeed) return;
    
    // Clear the activity feed
    activityFeed.innerHTML = `
        <div class="card notification-card mb-2">
            <div class="card-body p-2">
                <div class="d-flex justify-content-between align-items-start">
                    <span class="badge bg-secondary">System</span>
                    <small class="text-muted">just now</small>
                </div>
                <p class="mb-0 mt-1">All notifications cleared</p>
            </div>
        </div>
    `;
    
    // Reset notification count
    state.notificationCount = 0;
}

/**
 * Add a notification to the activity feed
 */
function addNotification(type, message) {
    const activityFeed = document.getElementById('activity-feed');
    if (!activityFeed) return;
    
    // Determine badge class based on type
    let badgeClass;
    let badgeText;
    
    switch (type) {
        case 'capability':
            badgeClass = 'bg-primary';
            badgeText = 'Capability';
            break;
        case 'assistance':
            badgeClass = 'bg-info';
            badgeText = 'Assistance';
            break;
        case 'training':
            badgeClass = 'bg-warning';
            badgeText = 'Training';
            break;
        case 'workflow':
            badgeClass = 'bg-success';
            badgeText = 'Workflow';
            break;
        default:
            badgeClass = 'bg-secondary';
            badgeText = 'System';
    }
    
    // Create the notification card
    const notificationCard = document.createElement('div');
    notificationCard.className = 'card notification-card mb-2';
    notificationCard.innerHTML = `
        <div class="card-body p-2">
            <div class="d-flex justify-content-between align-items-start">
                <span class="badge ${badgeClass}">${badgeText}</span>
                <small class="text-muted">just now</small>
            </div>
            <p class="mb-0 mt-1">${message}</p>
        </div>
    `;
    
    // Add the notification to the top of the feed
    activityFeed.insertBefore(notificationCard, activityFeed.firstChild);
    
    // Limit to 10 notifications
    while (activityFeed.children.length > 10) {
        activityFeed.removeChild(activityFeed.lastChild);
    }
    
    // Increment notification count
    state.notificationCount++;
}

/**
 * Show a toast notification
 */
function showToast(type, title, message) {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;
    
    // Create the toast element
    const toastElement = document.createElement('div');
    toastElement.className = `toast toast-${type}`;
    toastElement.setAttribute('role', 'alert');
    toastElement.setAttribute('aria-live', 'assertive');
    toastElement.setAttribute('aria-atomic', 'true');
    toastElement.innerHTML = `
        <div class="toast-header">
            <strong class="me-auto">${title}</strong>
            <small>just now</small>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    // Add the toast to the container
    toastContainer.appendChild(toastElement);
    
    // Initialize the toast
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 5000
    });
    
    // Show the toast
    toast.show();
    
    // Remove the toast after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastContainer.removeChild(toastElement);
    });
}

/**
 * Refresh the dashboard data
 */
function refreshDashboard() {
    console.log('Refreshing dashboard data...');
    
    // Refresh all data
    fetchCommandStructure();
    fetchAgents();
    fetchExperienceStats();
}

/**
 * Format a date string to a readable format
 */
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleString();
    } catch (error) {
        return dateString;
    }
}

/**
 * Format a date string to a "time ago" format
 */
function formatTimeAgo(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffSec = Math.floor(diffMs / 1000);
        
        if (diffSec < 60) {
            return `${diffSec} second${diffSec !== 1 ? 's' : ''} ago`;
        }
        
        const diffMin = Math.floor(diffSec / 60);
        if (diffMin < 60) {
            return `${diffMin} minute${diffMin !== 1 ? 's' : ''} ago`;
        }
        
        const diffHour = Math.floor(diffMin / 60);
        if (diffHour < 24) {
            return `${diffHour} hour${diffHour !== 1 ? 's' : ''} ago`;
        }
        
        const diffDay = Math.floor(diffHour / 24);
        return `${diffDay} day${diffDay !== 1 ? 's' : ''} ago`;
    } catch (error) {
        return dateString;
    }
}

/**
 * Format an event type to a readable format
 */
function formatEventType(eventType) {
    if (!eventType) return 'Unknown';
    
    // Convert snake_case or camelCase to Title Case with spaces
    return eventType
        .replace(/_/g, ' ')
        .replace(/([A-Z])/g, ' $1')
        .replace(/^\w/, c => c.toUpperCase())
        .trim();
}

/**
 * Format a capability name to a readable format
 */
function formatCapabilityName(capability) {
    if (!capability) return 'Unknown';
    
    // Convert snake_case or camelCase to Title Case with spaces
    return capability
        .replace(/execute_workflow_/g, '')
        .replace(/_/g, ' ')
        .replace(/([A-Z])/g, ' $1')
        .replace(/^\w/, c => c.toUpperCase())
        .trim();
}

/**
 * Format a workflow name to a readable format
 */
function formatWorkflowName(workflow) {
    if (!workflow) return 'Unknown';
    
    // Convert snake_case or camelCase to Title Case with spaces
    return workflow
        .replace(/_/g, ' ')
        .replace(/([A-Z])/g, ' $1')
        .replace(/^\w/, c => c.toUpperCase())
        .trim();
}

// Initialize the dashboard when the DOM is ready
if (typeof jQuery !== 'undefined') {
    // Use jQuery if available
    $(document).ready(initDashboard);
} else {
    // Fallback to standard JavaScript
    document.addEventListener('DOMContentLoaded', initDashboard);
}

// Export functions for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initDashboard,
        fetchCommandStructure,
        fetchAgents,
        fetchExperienceStats,
        updateAgentCards,
        showAgentDetails,
        executeCapability,
        requestHelp,
        startTraining,
        executeWorkflow,
        showToast,
        addNotification,
        formatDate,
        formatTimeAgo,
        formatEventType,
        formatCapabilityName,
        formatWorkflowName
    };
}