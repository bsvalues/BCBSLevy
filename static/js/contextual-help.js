/**
 * Contextual Help System
 * 
 * Provides AI-powered contextual help explanations throughout the TerraFusion platform.
 * Features include:
 * - Help icons next to complex terms with hover/click tooltips
 * - AI-generated explanations using the Claude API
 * - Chart interpretation assistance
 * - Context-aware help based on user role and page location
 */

// Initialize global variables
const TerraFusionHelp = {
    tooltips: {},
    popovers: {},
    explanationCache: {},
    tooltipEnabled: true,
    isLoading: false
};

/**
 * Initialize the contextual help system
 */
function initContextualHelp() {
    console.log("Initializing contextual help system...");
    
    // Initialize tooltips and popovers if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        // Enable tooltips globally
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        TerraFusionHelp.tooltips = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl, {
                html: true,
                container: 'body'
            });
        });
        
        // Enable popovers globally
        var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        TerraFusionHelp.popovers = popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl, {
                html: true,
                container: 'body',
                trigger: 'click',
                placement: 'auto'
            });
        });
    }
    
    // Add the help icons to all elements with data-help-topic attributes
    addHelpIcons();
    
    // Add help buttons to charts
    addChartHelpButtons();
    
    console.log("Contextual help system initialized");
}

/**
 * Add help icons to elements with data-help-topic attributes
 */
function addHelpIcons() {
    const helpElements = document.querySelectorAll('[data-help-topic]');
    
    helpElements.forEach(element => {
        const topicId = element.getAttribute('data-help-topic');
        const placement = element.getAttribute('data-help-placement') || 'top';
        const type = element.getAttribute('data-help-type') || 'tooltip';
        
        // Create help icon
        const helpIcon = document.createElement('i');
        helpIcon.className = 'fas fa-question-circle help-icon ms-1';
        helpIcon.style.cursor = 'pointer';
        helpIcon.style.color = '#0d6efd';
        helpIcon.style.fontSize = '0.875em';
        
        // Add tooltip or popover functionality
        if (type === 'tooltip') {
            helpIcon.setAttribute('data-bs-toggle', 'tooltip');
            helpIcon.setAttribute('data-bs-placement', placement);
            helpIcon.setAttribute('title', 'Loading...');
            helpIcon.setAttribute('data-help-topic-id', topicId);
            
            // Initialize tooltip
            if (typeof bootstrap !== 'undefined') {
                const tooltip = new bootstrap.Tooltip(helpIcon, {
                    html: true,
                    container: 'body'
                });
                
                // Load explanation when tooltip is shown
                helpIcon.addEventListener('mouseenter', function() {
                    loadExplanation(topicId, helpIcon, 'tooltip');
                });
            }
        } else if (type === 'popover') {
            helpIcon.setAttribute('data-bs-toggle', 'popover');
            helpIcon.setAttribute('data-bs-placement', placement);
            helpIcon.setAttribute('data-bs-title', 'Loading...');
            helpIcon.setAttribute('data-bs-content', 'Please wait...');
            helpIcon.setAttribute('data-help-topic-id', topicId);
            
            // Initialize popover
            if (typeof bootstrap !== 'undefined') {
                const popover = new bootstrap.Popover(helpIcon, {
                    html: true,
                    container: 'body',
                    trigger: 'click'
                });
                
                // Load explanation when popover is shown
                helpIcon.addEventListener('click', function() {
                    loadExplanation(topicId, helpIcon, 'popover');
                });
            }
        }
        
        // Append the help icon to the element
        element.appendChild(helpIcon);
    });
}

/**
 * Add help buttons to chart containers
 */
function addChartHelpButtons() {
    const chartContainers = document.querySelectorAll('.chart-container');
    
    chartContainers.forEach(container => {
        // Get the chart type from the container
        const chartId = container.querySelector('canvas')?.id;
        let chartType = '';
        
        if (chartId) {
            if (chartId.includes('levy-rate') || chartId.includes('levyRates')) {
                chartType = 'levy_rate_chart';
            } else if (chartId.includes('levy-amount') || chartId.includes('levyAmounts')) {
                chartType = 'levy_amount_chart';
            } else if (chartId.includes('assessed-value')) {
                chartType = 'assessed_value_chart';
            }
        }
        
        if (!chartType) return;
        
        // Create help button
        const helpButton = document.createElement('button');
        helpButton.className = 'btn btn-sm btn-light chart-help-btn';
        helpButton.innerHTML = '<i class="fas fa-lightbulb"></i> Interpret this chart';
        helpButton.style.position = 'absolute';
        helpButton.style.top = '5px';
        helpButton.style.right = '5px';
        helpButton.style.zIndex = '10';
        helpButton.style.opacity = '0.7';
        
        // Add hover effect
        helpButton.addEventListener('mouseenter', function() {
            helpButton.style.opacity = '1';
        });
        
        helpButton.addEventListener('mouseleave', function() {
            helpButton.style.opacity = '0.7';
        });
        
        // Add click handler to show chart explanation
        helpButton.addEventListener('click', function() {
            showChartExplanation(chartType, container);
        });
        
        // Make sure container has position relative for proper button positioning
        if (getComputedStyle(container).position === 'static') {
            container.style.position = 'relative';
        }
        
        // Add the button to the container
        container.appendChild(helpButton);
    });
}

/**
 * Load explanation for a topic
 * 
 * @param {string} topicId - The topic identifier
 * @param {Element} element - The DOM element to update
 * @param {string} type - The type of help (tooltip or popover)
 */
function loadExplanation(topicId, element, type) {
    // Check cache first
    if (TerraFusionHelp.explanationCache[topicId]) {
        updateElementWithExplanation(element, TerraFusionHelp.explanationCache[topicId], type);
        return;
    }
    
    // Get current page context
    const pageContext = window.location.pathname;
    
    // Fetch explanation from API
    fetch(`/api/help/explain/${topicId}?context=${encodeURIComponent(pageContext)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.explanation) {
                // Cache the explanation
                TerraFusionHelp.explanationCache[topicId] = data.explanation;
                
                // Update the element
                updateElementWithExplanation(element, data.explanation, type);
            } else {
                console.error('Failed to load explanation:', data.error || 'Unknown error');
                
                // Show error in tooltip/popover
                if (type === 'tooltip') {
                    element.setAttribute('title', 'Could not load explanation. Try again later.');
                    bootstrap.Tooltip.getInstance(element).update();
                } else if (type === 'popover') {
                    element.setAttribute('data-bs-title', 'Error');
                    element.setAttribute('data-bs-content', 'Could not load explanation. Try again later.');
                    bootstrap.Popover.getInstance(element).update();
                }
            }
        })
        .catch(error => {
            console.error('Error fetching explanation:', error);
            
            // Show error in tooltip/popover
            if (type === 'tooltip') {
                element.setAttribute('title', 'Could not load explanation. Try again later.');
                bootstrap.Tooltip.getInstance(element).update();
            } else if (type === 'popover') {
                element.setAttribute('data-bs-title', 'Error');
                element.setAttribute('data-bs-content', 'Could not load explanation. Try again later.');
                bootstrap.Popover.getInstance(element).update();
            }
        });
}

/**
 * Update element with explanation data
 * 
 * @param {Element} element - The DOM element to update
 * @param {Object} explanation - The explanation data
 * @param {string} type - The type of help (tooltip or popover)
 */
function updateElementWithExplanation(element, explanation, type) {
    if (type === 'tooltip') {
        // Create a simplified tooltip with just key information
        const tooltipContent = `
            <strong>${explanation.title}</strong><br>
            <span class="text-muted">${explanation.explanation.split('.')[0]}.</span>
            <br><small>(Click for more info)</small>
        `;
        
        element.setAttribute('title', tooltipContent);
        bootstrap.Tooltip.getInstance(element).update();
        
        // Add click handler to show full explanation
        element.removeEventListener('click', showFullExplanation);
        element.addEventListener('click', showFullExplanation);
        
    } else if (type === 'popover') {
        // Get first paragraph for title, rest for content
        const firstPeriodIndex = explanation.explanation.indexOf('.');
        let title = explanation.title;
        let content = explanation.explanation;
        
        if (firstPeriodIndex > 0) {
            const firstSentence = explanation.explanation.substring(0, firstPeriodIndex + 1);
            content = explanation.explanation.substring(firstPeriodIndex + 1).trim();
            title = `${explanation.title} <span class="badge bg-light text-dark">${explanation.category}</span>`;
        }
        
        // Add "AI Generated" badge and icon
        content += `
            <div class="mt-2 text-muted">
                <small><i class="fas fa-robot me-1"></i> AI-generated explanation</small>
            </div>
        `;
        
        element.setAttribute('data-bs-title', title);
        element.setAttribute('data-bs-content', content);
        bootstrap.Popover.getInstance(element).update();
    }
}

/**
 * Show full explanation in a modal
 * 
 * @param {Event} event - The click event
 */
function showFullExplanation(event) {
    // Prevent default tooltip behavior
    event.preventDefault();
    event.stopPropagation();
    
    // Hide any open tooltips
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.forEach(function (tooltipTriggerEl) {
            const tooltip = bootstrap.Tooltip.getInstance(tooltipTriggerEl);
            if (tooltip) {
                tooltip.hide();
            }
        });
    }
    
    // Get topic ID from element
    const topicId = event.currentTarget.getAttribute('data-help-topic-id');
    
    // Get explanation from cache
    const explanation = TerraFusionHelp.explanationCache[topicId];
    
    if (!explanation) {
        console.error('Explanation not found in cache for topic:', topicId);
        return;
    }
    
    // Create a modal to show the full explanation
    createExplanationModal(explanation);
}

/**
 * Create a modal to show a full explanation
 * 
 * @param {Object} explanation - The explanation data
 */
function createExplanationModal(explanation) {
    // Check if a modal already exists and remove it
    const existingModal = document.getElementById('helpExplanationModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Create modal elements
    const modalDiv = document.createElement('div');
    modalDiv.className = 'modal fade';
    modalDiv.id = 'helpExplanationModal';
    modalDiv.tabIndex = '-1';
    modalDiv.setAttribute('aria-labelledby', 'helpExplanationModalLabel');
    modalDiv.setAttribute('aria-hidden', 'true');
    
    // Set modal content
    modalDiv.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="helpExplanationModalLabel">
                        ${explanation.title}
                        <span class="badge bg-light text-dark ms-2">${explanation.category}</span>
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="help-content">
                        ${explanation.explanation}
                    </div>
                    <div class="help-footer mt-3">
                        <p class="text-muted">
                            <small>
                                <i class="fas fa-robot me-1"></i> AI-generated explanation
                                <span class="ms-2">
                                    Generated: ${explanation.generated_at ? explanation.generated_at.split('T')[0] : 'N/A'}
                                </span>
                            </small>
                        </p>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to document
    document.body.appendChild(modalDiv);
    
    // Initialize and show the modal
    if (typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(modalDiv);
        modal.show();
    }
}

/**
 * Show explanation for a chart
 * 
 * @param {string} chartType - The type of chart (levy_rate_chart, levy_amount_chart, etc.)
 * @param {Element} container - The chart container element
 */
function showChartExplanation(chartType, container) {
    // Get chart data
    let chartData = {};
    const canvasId = container.querySelector('canvas')?.id;
    
    if (canvasId && window.terrafusionCharts) {
        const chart = window.terrafusionCharts[canvasId] || 
                      window.terrafusionCharts.levyRatesChart || 
                      window.terrafusionCharts.levyAmountsChart;
        
        if (chart) {
            chartData = {
                labels: chart.data.labels,
                datasets: chart.data.datasets.map(ds => ({
                    label: ds.label,
                    data: ds.data
                }))
            };
        }
    }
    
    // Show loading feedback
    const loadingModal = createLoadingModal('Analyzing Chart Data', 'Our AI assistant is analyzing this chart to provide helpful insights...');
    
    // Request explanation from API
    fetch('/api/help/chart/' + chartType, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            data_context: chartData
        })
    })
    .then(response => response.json())
    .then(data => {
        // Close loading modal
        loadingModal.hide();
        
        if (data.success && data.explanation) {
            // Cache the explanation
            TerraFusionHelp.explanationCache[chartType] = data.explanation;
            
            // Show explanation in modal
            createChartExplanationModal(data.explanation, chartType);
        } else {
            console.error('Failed to load chart explanation:', data.error || 'Unknown error');
            showErrorModal('Could not load chart explanation', 'Please try again later.');
        }
    })
    .catch(error => {
        // Close loading modal
        loadingModal.hide();
        
        console.error('Error fetching chart explanation:', error);
        showErrorModal('Error Loading Explanation', 'An error occurred while analyzing the chart. Please try again later.');
    });
}

/**
 * Create a modal to show a chart explanation
 * 
 * @param {Object} explanation - The explanation data
 * @param {string} chartType - The type of chart
 */
function createChartExplanationModal(explanation, chartType) {
    // Check if a modal already exists and remove it
    const existingModal = document.getElementById('chartExplanationModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Get chart title based on type
    let chartTitle = 'Chart Analysis';
    if (chartType === 'levy_rate_chart') {
        chartTitle = 'Levy Rate Chart Analysis';
    } else if (chartType === 'levy_amount_chart') {
        chartTitle = 'Levy Amount Chart Analysis';
    } else if (chartType === 'assessed_value_chart') {
        chartTitle = 'Assessed Value Chart Analysis';
    }
    
    // Create modal elements
    const modalDiv = document.createElement('div');
    modalDiv.className = 'modal fade';
    modalDiv.id = 'chartExplanationModal';
    modalDiv.tabIndex = '-1';
    modalDiv.setAttribute('aria-labelledby', 'chartExplanationModalLabel');
    modalDiv.setAttribute('aria-hidden', 'true');
    
    // Set modal content
    modalDiv.innerHTML = `
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="chartExplanationModalLabel">
                        <i class="fas fa-chart-bar me-2"></i> ${chartTitle}
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="chart-explanation-content">
                        ${explanation.explanation}
                    </div>
                    <div class="chart-explanation-footer mt-3">
                        <p class="text-muted">
                            <small>
                                <i class="fas fa-robot me-1"></i> AI-generated analysis
                                <span class="ms-2">
                                    Generated: ${explanation.generated_at ? explanation.generated_at.split('T')[0] : 'N/A'}
                                </span>
                            </small>
                        </p>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to document
    document.body.appendChild(modalDiv);
    
    // Initialize and show the modal
    if (typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(modalDiv);
        modal.show();
    }
}

/**
 * Create a loading modal
 * 
 * @param {string} title - The modal title
 * @param {string} message - The loading message
 * @returns {bootstrap.Modal} The bootstrap modal instance
 */
function createLoadingModal(title, message) {
    // Check if a modal already exists and remove it
    const existingModal = document.getElementById('loadingModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Create modal elements
    const modalDiv = document.createElement('div');
    modalDiv.className = 'modal fade';
    modalDiv.id = 'loadingModal';
    modalDiv.tabIndex = '-1';
    modalDiv.setAttribute('aria-labelledby', 'loadingModalLabel');
    modalDiv.setAttribute('aria-hidden', 'true');
    modalDiv.setAttribute('data-bs-backdrop', 'static');
    modalDiv.setAttribute('data-bs-keyboard', 'false');
    
    // Set modal content
    modalDiv.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="loadingModalLabel">${title}</h5>
                </div>
                <div class="modal-body text-center">
                    <div class="spinner-border text-primary mb-3" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p>${message}</p>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to document
    document.body.appendChild(modalDiv);
    
    // Initialize and show the modal
    if (typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(modalDiv);
        modal.show();
        return modal;
    }
    
    return null;
}

/**
 * Show an error modal
 * 
 * @param {string} title - The error title
 * @param {string} message - The error message
 */
function showErrorModal(title, message) {
    // Check if a modal already exists and remove it
    const existingModal = document.getElementById('errorModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Create modal elements
    const modalDiv = document.createElement('div');
    modalDiv.className = 'modal fade';
    modalDiv.id = 'errorModal';
    modalDiv.tabIndex = '-1';
    modalDiv.setAttribute('aria-labelledby', 'errorModalLabel');
    modalDiv.setAttribute('aria-hidden', 'true');
    
    // Set modal content
    modalDiv.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header bg-danger text-white">
                    <h5 class="modal-title" id="errorModalLabel">
                        <i class="fas fa-exclamation-triangle me-2"></i> ${title}
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <p>${message}</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to document
    document.body.appendChild(modalDiv);
    
    // Initialize and show the modal
    if (typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(modalDiv);
        modal.show();
    }
}

/**
 * Toggle contextual help globally
 */
function toggleContextualHelp() {
    TerraFusionHelp.tooltipEnabled = !TerraFusionHelp.tooltipEnabled;
    
    // Update visibility of help icons
    const helpIcons = document.querySelectorAll('.help-icon');
    helpIcons.forEach(icon => {
        icon.style.display = TerraFusionHelp.tooltipEnabled ? 'inline-block' : 'none';
    });
    
    // Update visibility of chart help buttons
    const chartHelpButtons = document.querySelectorAll('.chart-help-btn');
    chartHelpButtons.forEach(button => {
        button.style.display = TerraFusionHelp.tooltipEnabled ? 'block' : 'none';
    });
    
    // Toggle the control button text if it exists
    const toggleButton = document.getElementById('toggleHelpButton');
    if (toggleButton) {
        toggleButton.innerHTML = TerraFusionHelp.tooltipEnabled ? 
            '<i class="fas fa-question-circle"></i> Hide Help' : 
            '<i class="fas fa-question-circle"></i> Show Help';
    }
}

// Add global functions to window
window.TerraFusionHelp = TerraFusionHelp;
window.initContextualHelp = initContextualHelp;
window.toggleContextualHelp = toggleContextualHelp;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize contextual help
    initContextualHelp();
    
    // Add a toggle button to the navbar if there's a navbar-nav
    const navbarNav = document.querySelector('.navbar-nav');
    if (navbarNav) {
        const toggleButton = document.createElement('button');
        toggleButton.id = 'toggleHelpButton';
        toggleButton.className = 'btn btn-outline-info btn-sm ms-2';
        toggleButton.innerHTML = '<i class="fas fa-question-circle"></i> Hide Help';
        toggleButton.addEventListener('click', toggleContextualHelp);
        
        // Create a navbar item to contain the button
        const navItem = document.createElement('li');
        navItem.className = 'nav-item d-flex align-items-center ms-2';
        navItem.appendChild(toggleButton);
        
        // Add to navbar
        navbarNav.appendChild(navItem);
    }
});