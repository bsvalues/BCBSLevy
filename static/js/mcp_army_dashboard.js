/**
 * MCP Army Dashboard JavaScript
 * 
 * This script provides interactive functionality for the MCP Army dashboard,
 * including agent network visualization, message tracking, and real-time status updates.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    $('[data-toggle="tooltip"]').tooltip();
    
    // Load experience replay statistics
    loadExperienceStats();
    
    // Load recent experiences
    loadRecentExperiences();
    
    // Initialize communication network visualization
    initCommunicationGraph();
    
    // Set up event handlers
    setupEventHandlers();
    
    // Set up periodic refreshing
    setInterval(refreshDashboard, 30000); // Refresh every 30 seconds
    
    console.log("MCP Army Dashboard JS initialized");
});

/**
 * Load experience statistics from the API
 */
function loadExperienceStats() {
    fetch('/mcp-army/api/experiences/stats')
        .then(response => response.json())
        .then(data => {
            const statsDiv = document.getElementById('experience-stats');
            if (!statsDiv) return;
            
            // Build HTML for experience stats
            let html = '<div class="row">';
            
            // Total experiences
            html += `
                <div class="col-md-6">
                    <div class="card bg-light mb-3">
                        <div class="card-body text-center">
                            <h5 class="card-title">Total Experiences</h5>
                            <h2 class="display-5">${data.total_experiences || 0}</h2>
                        </div>
                    </div>
                </div>
            `;
            
            // Buffer utilization
            const utilizationPercent = Math.round((data.utilization || 0) * 100);
            html += `
                <div class="col-md-6">
                    <div class="card bg-light mb-3">
                        <div class="card-body text-center">
                            <h5 class="card-title">Buffer Utilization</h5>
                            <h2 class="display-5">${utilizationPercent}%</h2>
                            <div class="progress">
                                <div class="progress-bar" role="progressbar" style="width: ${utilizationPercent}%" 
                                    aria-valuenow="${utilizationPercent}" aria-valuemin="0" aria-valuemax="100"></div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            html += '</div>'; // End row
            
            // Add counts by agent if available
            if (data.by_agent && Object.keys(data.by_agent).length > 0) {
                html += '<h6>Experiences by Agent</h6>';
                html += '<div class="table-responsive"><table class="table table-sm"><thead><tr><th>Agent</th><th>Count</th></tr></thead><tbody>';
                
                for (const [agent, count] of Object.entries(data.by_agent)) {
                    html += `<tr><td>${agent}</td><td>${count}</td></tr>`;
                }
                
                html += '</tbody></table></div>';
            }
            
            // Add counts by event type if available
            if (data.by_event_type && Object.keys(data.by_event_type).length > 0) {
                html += '<h6>Experiences by Event Type</h6>';
                html += '<div class="table-responsive"><table class="table table-sm"><thead><tr><th>Event Type</th><th>Count</th></tr></thead><tbody>';
                
                for (const [eventType, count] of Object.entries(data.by_event_type)) {
                    html += `<tr><td>${eventType}</td><td>${count}</td></tr>`;
                }
                
                html += '</tbody></table></div>';
            }
            
            // Add most recent timestamp if available
            if (data.most_recent) {
                const date = new Date(data.most_recent);
                html += `<div class="text-muted mt-2">Last experience: ${date.toLocaleString()}</div>`;
            }
            
            // Update DOM
            statsDiv.innerHTML = html;
        })
        .catch(error => {
            console.error('Error loading experience stats:', error);
            document.getElementById('experience-stats').innerHTML = '<div class="alert alert-danger">Error loading experience statistics</div>';
        });
}

/**
 * Load recent experiences from the API
 */
function loadRecentExperiences() {
    // For now, initialize with an empty table
    document.getElementById('recent-experiences').innerHTML = 
        '<tr><td colspan="3" class="text-center">No experiences recorded yet</td></tr>';
    
    // In a future version, this could load actual data from an experience endpoint
}

/**
 * Initialize the agent communication network visualization
 */
function initCommunicationGraph() {
    const graphContainer = document.getElementById('communication-graph');
    if (!graphContainer) return;
    
    // Get the agent data from the page
    const agentsData = getAgentsData();
    
    // Create a network graph using D3.js if available, or fall back to a simpler visualization
    if (typeof d3 !== 'undefined') {
        // Create D3 force-directed graph
        createD3Graph(graphContainer, agentsData);
    } else {
        // Create simple HTML table-based visualization
        createSimpleGraph(graphContainer, agentsData);
    }
}

/**
 * Extract agent data from the page
 */
function getAgentsData() {
    const agents = [];
    const agentCards = document.querySelectorAll('.agent-card');
    
    agentCards.forEach(card => {
        const agentId = card.dataset.agentId;
        const status = card.querySelector('.agent-status').textContent;
        
        agents.push({
            id: agentId,
            status: status,
            type: card.querySelector('.card-body p').textContent.replace('Type:', '').trim()
        });
    });
    
    return agents;
}

/**
 * Create a simple HTML-based graph visualization
 */
function createSimpleGraph(container, agents) {
    // Fetch the command structure
    fetch('/mcp-army/api/command-structure')
        .then(response => response.json())
        .then(data => {
            const relationships = [];
            
            // Extract relationships from command structure
            const structure = data.command_structure;
            const agentRelationships = data.agent_relationships || {};
            
            // Add relationships based on command structure
            if (structure) {
                // Architect to coordinator relationship
                if (structure.architect_prime && structure.integration_coordinator) {
                    relationships.push({
                        source: structure.integration_coordinator,
                        target: structure.architect_prime,
                        type: 'reports_to'
                    });
                }
                
                // Component leads to coordinator relationships
                if (structure.component_leads) {
                    for (const [component, lead] of Object.entries(structure.component_leads)) {
                        relationships.push({
                            source: lead,
                            target: structure.integration_coordinator,
                            type: 'reports_to'
                        });
                        
                        // Specialist agents to component lead relationships
                        if (structure.specialist_agents && structure.specialist_agents[component]) {
                            structure.specialist_agents[component].forEach(agent => {
                                relationships.push({
                                    source: agent,
                                    target: lead,
                                    type: 'reports_to'
                                });
                            });
                        }
                    }
                }
            }
            
            // Create a simple table-based visualization
            let html = '<div class="table-responsive">';
            html += '<table class="table table-sm"><thead><tr><th>Agent</th><th>Reports To</th><th>Status</th></tr></thead><tbody>';
            
            agents.forEach(agent => {
                const reportsTo = relationships.find(r => r.source === agent.id)?.target || '-';
                html += `<tr>
                    <td>${agent.id}</td>
                    <td>${reportsTo}</td>
                    <td><span class="badge status-${agent.status.toLowerCase()}">${agent.status}</span></td>
                </tr>`;
            });
            
            html += '</tbody></table></div>';
            container.innerHTML = html;
        })
        .catch(error => {
            console.error('Error loading command structure:', error);
            container.innerHTML = '<div class="alert alert-danger">Error loading agent communication network</div>';
        });
}

/**
 * Create a D3.js force-directed graph visualization
 * Note: This requires D3.js to be loaded
 */
function createD3Graph(container, agents) {
    if (typeof d3 === 'undefined') {
        createSimpleGraph(container, agents);
        return;
    }
    
    // This is a placeholder - in a real implementation, this would create a D3 force-directed graph
    container.innerHTML = '<div class="alert alert-info">Interactive agent network visualization will be available in a future update.</div>';
}

/**
 * Set up event handlers for dashboard interactions
 */
function setupEventHandlers() {
    // Agent card click handler
    document.querySelectorAll('.agent-card').forEach(card => {
        card.addEventListener('click', function() {
            const agentId = this.dataset.agentId;
            showAgentDetails(agentId);
        });
    });
    
    // Request help button handler
    document.querySelectorAll('.request-help-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const agentId = this.dataset.agentId;
            requestHelp(agentId);
        });
    });
    
    // Clear notifications button
    const clearBtn = document.getElementById('clear-notifications-btn');
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            document.getElementById('activity-feed').innerHTML = '';
        });
    }
    
    // Start training button
    const trainingBtn = document.getElementById('start-training-btn');
    if (trainingBtn) {
        trainingBtn.addEventListener('click', startTrainingCycle);
    }
    
    // Workflow execution buttons
    document.querySelectorAll('.workflow-btn').forEach(button => {
        button.addEventListener('click', function() {
            const workflow = this.dataset.workflow;
            showWorkflowModal(workflow);
        });
    });
    
    // Execute workflow button in modal
    const executeBtn = document.getElementById('executeWorkflowBtn');
    if (executeBtn) {
        executeBtn.addEventListener('click', executeWorkflow);
    }
}

/**
 * Show agent details in a modal
 */
function showAgentDetails(agentId) {
    // Fetch agent details
    fetch(`/mcp-army/api/agents/${agentId}`)
        .then(response => response.json())
        .then(data => {
            const modal = document.getElementById('agentDetailsModal');
            const content = document.getElementById('agentDetailsContent');
            
            if (!modal || !content) return;
            
            // Build agent details HTML
            let html = `<h4>${agentId}</h4>`;
            html += `<div class="badge status-${data.status?.toLowerCase() || 'idle'} mb-3">${data.status || 'Idle'}</div>`;
            
            // Agent metadata
            html += '<div class="card mb-3"><div class="card-body">';
            if (data.type) html += `<p><strong>Type:</strong> ${data.type}</p>`;
            if (data.role) html += `<p><strong>Role:</strong> ${data.role}</p>`;
            if (data.component) html += `<p><strong>Component:</strong> ${data.component}</p>`;
            if (data.domain) html += `<p><strong>Domain:</strong> ${data.domain}</p>`;
            html += '</div></div>';
            
            // Agent capabilities
            if (data.capabilities && data.capabilities.length > 0) {
                html += '<h5>Capabilities</h5>';
                html += '<ul class="list-group mb-3">';
                data.capabilities.forEach(capability => {
                    html += `<li class="list-group-item">${capability}</li>`;
                });
                html += '</ul>';
            }
            
            // Agent performance metrics
            if (data.performance) {
                html += '<h5>Performance Metrics</h5>';
                html += '<div class="card"><div class="card-body">';
                
                for (const [metric, value] of Object.entries(data.performance)) {
                    html += `
                        <div class="mb-2">
                            <div class="d-flex justify-content-between">
                                <span>${metric}:</span>
                                <span>${(value * 100).toFixed(1)}%</span>
                            </div>
                            <div class="progress">
                                <div class="progress-bar" role="progressbar" style="width: ${value * 100}%" 
                                    aria-valuenow="${value * 100}" aria-valuemin="0" aria-valuemax="100"></div>
                            </div>
                        </div>
                    `;
                }
                
                html += '</div></div>';
            }
            
            // Update modal content and show
            content.innerHTML = html;
            $(modal).modal('show');
        })
        .catch(error => {
            console.error('Error loading agent details:', error);
            showToast('error', 'Error', `Could not load details for ${agentId}`);
        });
}

/**
 * Request help for an agent
 */
function requestHelp(agentId) {
    // Find a suitable helper agent - use MCP by default
    const helperAgentId = 'MCP';
    
    // Show a confirmation toast
    showToast('info', 'Help Requested', `Requesting assistance for ${agentId} from ${helperAgentId}`);
    
    // Make API call to request assistance
    fetch(`/mcp-army/api/agents/${agentId}/assistance/${helperAgentId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            assistance_type: 'general'
        })
    })
    .then(response => response.json())
    .then(data => {
        addActivityNotification('Assistance', `${helperAgentId} is assisting ${agentId}`);
        showToast('success', 'Help Initiated', `${helperAgentId} is now assisting ${agentId}`);
    })
    .catch(error => {
        console.error('Error requesting assistance:', error);
        showToast('error', 'Request Failed', `Could not request assistance for ${agentId}`);
    });
    
    // Prevent event bubbling
    return false;
}

/**
 * Start a training cycle using the experience replay buffer
 */
function startTrainingCycle() {
    const trainingBtn = document.getElementById('start-training-btn');
    if (trainingBtn) {
        trainingBtn.disabled = true;
        trainingBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Training...';
    }
    
    // Make API call to start training
    fetch('/mcp-army/api/training/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            batch_size: 32
        })
    })
    .then(response => response.json())
    .then(data => {
        addActivityNotification('Training', 'Experience replay training cycle completed');
        showToast('success', 'Training Complete', 'Agents have been updated with new experiences');
        
        // Re-enable button
        if (trainingBtn) {
            trainingBtn.disabled = false;
            trainingBtn.innerHTML = 'Start Training Cycle';
        }
        
        // Refresh stats
        loadExperienceStats();
    })
    .catch(error => {
        console.error('Error starting training cycle:', error);
        showToast('error', 'Training Failed', 'Could not complete the training cycle');
        
        // Re-enable button
        if (trainingBtn) {
            trainingBtn.disabled = false;
            trainingBtn.innerHTML = 'Start Training Cycle';
        }
    });
}

/**
 * Show the workflow execution modal
 */
function showWorkflowModal(workflowName) {
    const modal = document.getElementById('workflowModal');
    if (!modal) return;
    
    // Set workflow name
    document.getElementById('workflowName').value = workflowName;
    
    // Update modal title
    document.getElementById('workflowModalLabel').textContent = `Execute ${formatWorkflowName(workflowName)} Workflow`;
    
    // Load tax districts for dropdown
    loadTaxDistricts();
    
    // Show modal
    $(modal).modal('show');
}

/**
 * Format workflow name for display
 */
function formatWorkflowName(name) {
    return name
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

/**
 * Load tax districts for the workflow form
 */
function loadTaxDistricts() {
    const select = document.getElementById('taxDistrictId');
    if (!select) return;
    
    // Clear existing options
    select.innerHTML = '<option value="">Select a district...</option>';
    
    // Make API call to get districts
    fetch('/api/districts')
        .then(response => response.json())
        .then(data => {
            // Add districts to dropdown
            data.forEach(district => {
                const option = document.createElement('option');
                option.value = district.id;
                option.textContent = district.name;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading tax districts:', error);
            select.innerHTML += '<option value="" disabled>Error loading districts</option>';
        });
}

/**
 * Execute the selected workflow
 */
function executeWorkflow() {
    const workflowName = document.getElementById('workflowName').value;
    const taxDistrictId = document.getElementById('taxDistrictId').value;
    const year = document.getElementById('year').value;
    
    // Validate form
    if (!workflowName) {
        showToast('error', 'Error', 'No workflow selected');
        return;
    }
    
    // Get additional parameters
    let additionalParams = {};
    try {
        const paramsText = document.getElementById('additionalParams').value;
        if (paramsText) {
            additionalParams = JSON.parse(paramsText);
        }
    } catch (error) {
        showToast('error', 'Error', 'Invalid JSON in additional parameters');
        return;
    }
    
    // Prepare parameters
    const parameters = {
        ...additionalParams,
        year: parseInt(year)
    };
    
    if (taxDistrictId) {
        parameters.taxDistrictId = parseInt(taxDistrictId);
    }
    
    // Disable execute button
    const executeBtn = document.getElementById('executeWorkflowBtn');
    if (executeBtn) {
        executeBtn.disabled = true;
        executeBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Executing...';
    }
    
    // Make API call to execute workflow
    fetch('/mcp-army/api/workflows/collaborative', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            workflow_name: workflowName,
            parameters: parameters
        })
    })
    .then(response => response.json())
    .then(data => {
        // Hide modal
        $('#workflowModal').modal('hide');
        
        // Show success message
        showToast('success', 'Workflow Started', `${formatWorkflowName(workflowName)} workflow has been initiated`);
        
        // Add to activity feed
        addActivityNotification('Workflow', `${formatWorkflowName(workflowName)} workflow started`, 'primary');
        
        // Reset execute button
        if (executeBtn) {
            executeBtn.disabled = false;
            executeBtn.innerHTML = 'Execute';
        }
    })
    .catch(error => {
        console.error('Error executing workflow:', error);
        showToast('error', 'Execution Failed', `Could not execute ${formatWorkflowName(workflowName)} workflow`);
        
        // Reset execute button
        if (executeBtn) {
            executeBtn.disabled = false;
            executeBtn.innerHTML = 'Execute';
        }
    });
}

/**
 * Add a notification to the activity feed
 */
function addActivityNotification(type, message, styleClass = 'info') {
    const feed = document.getElementById('activity-feed');
    if (!feed) return;
    
    const now = new Date();
    const timeString = 'just now';
    
    const html = `
        <div class="card notification-card mb-2">
            <div class="card-body p-2">
                <div class="d-flex justify-content-between align-items-start">
                    <span class="badge bg-${styleClass}">${type}</span>
                    <small class="text-muted">${timeString}</small>
                </div>
                <p class="mb-0 mt-1">${message}</p>
            </div>
        </div>
    `;
    
    // Add to beginning of feed
    feed.insertAdjacentHTML('afterbegin', html);
}

/**
 * Show a toast notification
 */
function showToast(type, title, message) {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const id = 'toast-' + Date.now();
    const html = `
        <div id="${id}" class="toast toast-${type}" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <strong class="me-auto">${title}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', html);
    
    // Show toast
    const toastElement = document.getElementById(id);
    const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 5000 });
    toast.show();
    
    // Remove after hiding
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

/**
 * Refresh dashboard data
 */
function refreshDashboard() {
    // Update agent statuses
    document.querySelectorAll('.agent-card').forEach(card => {
        const agentId = card.dataset.agentId;
        
        fetch(`/mcp-army/api/agents/${agentId}`)
            .then(response => response.json())
            .then(data => {
                const statusBadge = card.querySelector('.agent-status');
                if (statusBadge) {
                    statusBadge.textContent = data.status || 'unknown';
                    statusBadge.className = `badge status-${(data.status || 'unknown').toLowerCase()} agent-status`;
                }
                
                const performanceBar = card.querySelector('.performance-bar');
                if (performanceBar && data.performance && data.performance.overall !== undefined) {
                    performanceBar.style.width = `${data.performance.overall * 100}%`;
                    
                    const performanceText = card.querySelector('.d-flex.justify-content-between.mb-1 span:last-child');
                    if (performanceText) {
                        performanceText.textContent = `${(data.performance.overall * 100).toFixed(2)}%`;
                    }
                }
            })
            .catch(error => {
                console.error(`Error updating status for ${agentId}:`, error);
            });
    });
    
    // Refresh experience stats
    loadExperienceStats();
}