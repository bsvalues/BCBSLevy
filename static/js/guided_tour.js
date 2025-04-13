/**
 * Guided Tour Implementation for LevyMaster
 * 
 * This module provides interactive onboarding tours for the LevyMaster application
 * using intro.js. It implements multiple tour paths based on user role and context.
 */

// Wait for document to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tour system
    initGuidedTours();
});

/**
 * Initialize the guided tour system
 */
function initGuidedTours() {
    // Check if we should start a tour based on URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const startTour = urlParams.get('start_tour');
    
    if (startTour) {
        // Start the specified tour after a short delay to ensure page is fully rendered
        setTimeout(() => {
            startGuidedTour(startTour);
        }, 800);
    }
    
    // Add event listeners for tour triggers
    setupTourTriggers();
}

/**
 * Setup event listeners for tour trigger buttons
 */
function setupTourTriggers() {
    // Add event listeners to tour start buttons
    document.querySelectorAll('[data-tour]').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const tourName = this.getAttribute('data-tour');
            startGuidedTour(tourName);
        });
    });
    
    // Add tour links to help menu if it exists
    const helpMenu = document.querySelector('.help-menu-body');
    if (helpMenu) {
        const toursSection = helpMenu.querySelector('.help-section:first-child');
        if (toursSection) {
            // Check if tour section already exists to avoid duplicates
            if (!toursSection.querySelector('.tour-links')) {
                const tourLinks = document.createElement('div');
                tourLinks.classList.add('tour-links', 'mt-3');
                tourLinks.innerHTML = `
                    <h6>Guided Tours</h6>
                    <ul class="list-unstyled">
                        <li><a href="#" data-tour="welcomeTour"><i class="bi bi-info-circle me-2"></i>Welcome Tour</a></li>
                        <li><a href="#" data-tour="dashboardTour"><i class="bi bi-speedometer2 me-2"></i>Dashboard Tour</a></li>
                        <li><a href="#" data-tour="calculatorTour"><i class="bi bi-calculator me-2"></i>Levy Calculator</a></li>
                        <li><a href="#" data-tour="dataHubTour"><i class="bi bi-database me-2"></i>Data Hub</a></li>
                        <li><a href="#" data-tour="mcpArmyTour"><i class="bi bi-robot me-2"></i>AI & Agents</a></li>
                    </ul>
                `;
                
                toursSection.appendChild(tourLinks);
                
                // Add event listeners to the new links
                tourLinks.querySelectorAll('[data-tour]').forEach(link => {
                    link.addEventListener('click', function(e) {
                        e.preventDefault();
                        const tourName = this.getAttribute('data-tour');
                        startGuidedTour(tourName);
                    });
                });
            }
        }
    }
}

/**
 * Start a guided tour by name
 * @param {string} tourName - The name of the tour to start
 */
function startGuidedTour(tourName) {
    // Get tour configuration
    const tourConfig = getTourConfig(tourName);
    
    if (!tourConfig) {
        console.error(`Tour "${tourName}" not found`);
        return;
    }
    
    // Initialize the tour
    const tour = introJs();
    
    // Configure tour options
    tour.setOptions({
        steps: tourConfig,
        showStepNumbers: true,
        showBullets: true,
        showProgress: true,
        hideNext: false,
        hidePrev: false,
        nextLabel: 'Next →',
        prevLabel: '← Back',
        skipLabel: 'Skip',
        doneLabel: 'Done',
        tooltipClass: 'levy-tour-tooltip',
        highlightClass: 'levy-tour-highlight',
        exitOnEsc: true,
        exitOnOverlayClick: false,
        disableInteraction: false
    });
    
    // Log tour start
    console.log(`Starting guided tour: ${tourName}`);
    
    // Handle tour completion
    tour.oncomplete(function() {
        markTourComplete(tourName);
        checkPendingTours();
    });
    
    // Handle tour exit
    tour.onexit(function() {
        console.log(`Tour exited: ${tourName}`);
    });
    
    // Start the tour
    tour.start();
}

/**
 * Mark a tour as completed in local storage
 * @param {string} tourName - The name of the tour to mark as completed
 */
function markTourComplete(tourName) {
    try {
        // Get completed tours from local storage
        let completedTours = JSON.parse(localStorage.getItem('completedTours') || '[]');
        
        // Add current tour if not already in the list
        if (!completedTours.includes(tourName)) {
            completedTours.push(tourName);
            localStorage.setItem('completedTours', JSON.stringify(completedTours));
        }
        
        // Log to server if API available
        if (typeof fetch !== 'undefined') {
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
            
            if (csrfToken) {
                fetch('/tours/complete/' + tourName, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    }
                }).catch(error => {
                    console.warn('Failed to log tour completion to server:', error);
                });
            }
        }
    } catch (e) {
        console.error('Error marking tour as complete:', e);
    }
}

/**
 * Check for any pending tours that should be shown next
 */
function checkPendingTours() {
    try {
        // Check for pending tours in local storage
        const pendingToursStr = localStorage.getItem('pendingTours');
        
        if (pendingToursStr) {
            const pendingTours = JSON.parse(pendingToursStr);
            
            if (pendingTours.length > 0) {
                // Get the next tour from the queue
                const nextTour = pendingTours.shift();
                
                // Update the pending tours
                localStorage.setItem('pendingTours', JSON.stringify(pendingTours));
                
                // Start the next tour after a short delay
                setTimeout(() => {
                    startGuidedTour(nextTour);
                }, 1000);
            } else {
                // No more tours in the queue, remove the item
                localStorage.removeItem('pendingTours');
            }
        }
    } catch (e) {
        console.error('Error checking pending tours:', e);
    }
}

/**
 * Check if a user is new and show the welcome dialog
 */
function checkFirstTimeUser() {
    try {
        // Check if this is the first visit
        const hasCompletedTours = localStorage.getItem('completedTours');
        const hasSeenWelcome = localStorage.getItem('hasSeenWelcome');
        
        if (!hasCompletedTours && !hasSeenWelcome && document.querySelector('.navbar')) {
            // Mark that the user has seen the welcome dialog
            localStorage.setItem('hasSeenWelcome', 'true');
            
            // Show welcome dialog
            showWelcomeDialog();
        }
    } catch (e) {
        console.error('Error checking first time user:', e);
    }
}

/**
 * Show the welcome dialog for new users
 */
function showWelcomeDialog() {
    // Create modal element
    const modalElement = document.createElement('div');
    modalElement.classList.add('modal', 'fade');
    modalElement.id = 'welcomeTourModal';
    modalElement.setAttribute('tabindex', '-1');
    modalElement.setAttribute('aria-hidden', 'true');
    
    modalElement.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header bg-primary text-white">
                    <h5 class="modal-title">Welcome to LevyMaster</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <p>Would you like a guided tour of the system?</p>
                    
                    <div class="d-flex flex-column gap-2 mb-4">
                        <div class="form-check">
                            <input class="form-check-input tour-option" type="checkbox" id="tourCheck1" value="welcomeTour" checked>
                            <label class="form-check-label" for="tourCheck1">
                                Navigation Overview
                            </label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input tour-option" type="checkbox" id="tourCheck2" value="dashboardTour" checked>
                            <label class="form-check-label" for="tourCheck2">
                                Dashboard Tour
                            </label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input tour-option" type="checkbox" id="tourCheck3" value="dataHubTour">
                            <label class="form-check-label" for="tourCheck3">
                                Data Hub Tour
                            </label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input tour-option" type="checkbox" id="tourCheck4" value="calculatorTour">
                            <label class="form-check-label" for="tourCheck4">
                                Levy Calculator Tour
                            </label>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Skip Tours</button>
                    <button type="button" class="btn btn-primary" id="startSelectedTours">Start Tours</button>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to the DOM
    document.body.appendChild(modalElement);
    
    // Create and show the modal
    const welcomeModal = new bootstrap.Modal(modalElement);
    welcomeModal.show();
    
    // Handle start button click
    document.getElementById('startSelectedTours')?.addEventListener('click', function() {
        // Get selected tours
        const selectedTours = Array.from(
            document.querySelectorAll('.tour-option:checked')
        ).map(checkbox => checkbox.value);
        
        // Hide modal
        welcomeModal.hide();
        
        // Start first tour if any are selected
        if (selectedTours.length > 0) {
            // Start the first tour
            startGuidedTour(selectedTours[0]);
            
            // Queue remaining tours
            if (selectedTours.length > 1) {
                localStorage.setItem('pendingTours', JSON.stringify(selectedTours.slice(1)));
            }
        }
    });
}

/**
 * Get the configuration for a specified tour
 * @param {string} tourName - The name of the tour
 * @returns {Array} - The tour configuration steps
 */
function getTourConfig(tourName) {
    // Tour configuration map
    const tours = {
        // Welcome tour - Navigation Overview
        welcomeTour: [
            {
                element: '.navbar-brand',
                title: 'Welcome to LevyMaster',
                intro: 'Welcome to Benton County\'s Levy Calculation System. This quick tour will familiarize you with the main navigation elements.'
            },
            {
                element: '.navbar',
                title: 'Navigation Menu',
                intro: 'We\'ve redesigned the navigation for easier access to all features. The menu is now organized into 8 logical categories.'
            },
            {
                element: 'a.nav-link[href*="dashboard"]',
                title: 'Dashboard',
                intro: 'The Dashboard provides an overview of key metrics, recent activities, and important notifications.'
            },
            {
                element: '#taxDropdown',
                title: 'Tax Management',
                intro: 'Access core tax calculation tools including the Levy Calculator, Tax Districts, and Bill Impact tools.'
            },
            {
                element: '#dataHubDropdown',
                title: 'Data Hub',
                intro: 'The Data Hub centralizes all data operations including imports, exports, and search functionality.'
            },
            {
                element: '#analyticsDropdown',
                title: 'Analytics',
                intro: 'Access advanced analytics tools including forecasting, historical analysis, and data visualization.'
            },
            {
                element: '#aiDropdown',
                title: 'AI & Agents',
                intro: 'LevyMaster includes intelligent AI agents that can assist with complex tasks and provide insights.'
            },
            {
                element: '#reportsDropdown',
                title: 'Reports',
                intro: 'Generate standardized and custom reports for different stakeholders and purposes.'
            },
            {
                element: '#adminDropdown',
                title: 'Administration',
                intro: 'System administrators can manage users, settings, and monitor system performance.'
            },
            {
                element: '#helpMenuToggle',
                title: 'Help Center',
                intro: 'Access the Help Center for guides, documentation, and support resources.'
            },
            {
                element: '#resourcesDropdown',
                title: 'Resources',
                intro: 'Access additional resources including guided tours, glossary, and training materials.'
            },
            {
                title: 'Tour Complete',
                intro: 'You\'ve completed the navigation overview tour. You can access more specific tours from the Help Center or Resources menu.'
            }
        ],
        
        // Dashboard tour
        dashboardTour: [
            {
                element: '.dashboard-header',
                title: 'Dashboard Overview',
                intro: 'The dashboard provides a comprehensive overview of your levy calculation system.'
            },
            {
                element: '.dashboard-kpi-cards',
                title: 'Key Performance Indicators',
                intro: 'These cards show important metrics at a glance, including active districts, total assessed value, and levy rates.'
            },
            {
                element: '.dashboard-chart-section',
                title: 'Performance Charts',
                intro: 'Visual representations of key data help you quickly identify trends and patterns.'
            },
            {
                element: '.dashboard-recent-activity',
                title: 'Recent Activity',
                intro: 'Track recent changes and updates to your data, including imports, exports, and calculations.'
            },
            {
                element: '.dashboard-quick-actions',
                title: 'Quick Actions',
                intro: 'Perform common tasks directly from the dashboard without navigating to other sections.'
            },
            {
                element: '.dashboard-alerts',
                title: 'System Alerts',
                intro: 'Important notifications about system status, data quality issues, or required actions.'
            },
            {
                title: 'Dashboard Tour Complete',
                intro: 'You now know how to use the dashboard effectively. Explore other sections or take additional tours from the Help menu.'
            }
        ],
        
        // Levy Calculator tour
        calculatorTour: [
            {
                element: '.calculator-header',
                title: 'Levy Calculator',
                intro: 'The Levy Calculator helps you calculate accurate property tax levies for districts.'
            },
            {
                element: '.calculator-district-select',
                title: 'District Selection',
                intro: 'Start by selecting the tax district you want to calculate a levy for.'
            },
            {
                element: '.calculator-year-select',
                title: 'Year Selection',
                intro: 'Select the year for the levy calculation. Historical data will be loaded accordingly.'
            },
            {
                element: '.calculator-input-section',
                title: 'Input Values',
                intro: 'Enter the necessary values for your levy calculation, such as assessed values and prior year data.'
            },
            {
                element: '.calculator-action-buttons',
                title: 'Calculation Controls',
                intro: 'Use these buttons to run the calculation, reset values, or save your work.'
            },
            {
                element: '.calculator-results-section',
                title: 'Results Section',
                intro: 'View the calculated results, including levy amounts, rates, and compliance status.'
            },
            {
                element: '.calculator-export-options',
                title: 'Export Options',
                intro: 'Export your calculations in various formats for reporting or further analysis.'
            },
            {
                title: 'Calculator Tour Complete',
                intro: 'You now know how to use the Levy Calculator. Try performing a calculation on your own.'
            }
        ],
        
        // Data Hub tour
        dataHubTour: [
            {
                element: '#dataHubDropdown',
                title: 'Data Hub',
                intro: 'The Data Hub is your central location for all data operations in LevyMaster.'
            },
            {
                element: 'a.dropdown-item[href*="import_data"]',
                title: 'Data Import',
                intro: 'Import data from various sources, including CSV files, Excel spreadsheets, and other systems.'
            },
            {
                element: 'a.dropdown-item[href*="export_data"]',
                title: 'Data Export',
                intro: 'Export your data in multiple formats for reporting, analysis, or integration with other systems.'
            },
            {
                element: 'a.dropdown-item[href*="search"]',
                title: 'Data Search',
                intro: 'Quickly find specific records across the entire database using our powerful search feature.'
            },
            {
                element: 'a.dropdown-item[href*="import_history"]',
                title: 'Import History',
                intro: 'Review past import operations, including status, timestamps, and affected records.'
            },
            {
                element: 'a.dropdown-item[href*="data_quality"]',
                title: 'Data Quality',
                intro: 'Monitor and improve the quality of your data with validation tools and error reports.'
            },
            {
                title: 'Data Hub Tour Complete',
                intro: 'You now understand the data management capabilities of LevyMaster. Start by importing some data or exploring the existing dataset.'
            }
        ],
        
        // MCP Army tour
        mcpArmyTour: [
            {
                element: '#aiDropdown',
                title: 'AI & Agents',
                intro: 'LevyMaster includes advanced AI capabilities through our MCP (Master Control Program) Army system.'
            },
            {
                element: 'a.dropdown-item[href*="mcp-army-dashboard"]',
                title: 'MCP Army Dashboard',
                intro: 'The command center for our AI agent system, showing agent status and recent activities.'
            },
            {
                element: 'a.dropdown-item[href*="agent-dashboard"]',
                title: 'Agent Configuration',
                intro: 'Configure and customize individual agents to suit your specific requirements.'
            },
            {
                element: 'a.dropdown-item[href*="workflow"]',
                title: 'Workflow Orchestration',
                intro: 'Design and manage automated workflows that coordinate multiple AI agents for complex tasks.'
            },
            {
                element: 'a.dropdown-item[href*="levy_audit"]',
                title: 'Levy Audit Assistant',
                intro: 'This specialized agent helps validate levy calculations and identify compliance issues.'
            },
            {
                element: 'a.dropdown-item[href*="collaborative"]',
                title: 'Collaborative Workflows',
                intro: 'Enable collaboration between human users and AI agents for optimal results.'
            },
            {
                title: 'AI & Agents Tour Complete',
                intro: 'You now have an overview of the AI capabilities in LevyMaster. Explore the MCP Army Dashboard to see these tools in action.'
            }
        ]
    };
    
    // Return the requested tour configuration
    return tours[tourName] || null;
}

// Trigger first-time user check on page load
setTimeout(checkFirstTimeUser, 1500);