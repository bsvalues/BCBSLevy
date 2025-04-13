/**
 * Guided Tour JavaScript
 * 
 * This script handles the guided tour functionality for the LevyMaster application.
 * It uses the intro.js library to create interactive step-by-step tours of the interface.
 */

// Initialize guided tour functionality when document is ready
$(document).ready(function() {
    // Check if we need to start a tour automatically (from URL parameter)
    const urlParams = new URLSearchParams(window.location.search);
    const tourToStart = urlParams.get('start_tour');
    
    if (tourToStart) {
        // Remove the parameter from URL to prevent tour restarting on refresh
        if (history.pushState) {
            let newUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
            window.history.pushState({path: newUrl}, '', newUrl);
        }
        
        // Start the requested tour after a short delay
        setTimeout(function() {
            startTour(tourToStart);
        }, 500);
    }
    
    // Add CSS for guided tours
    if (!$('link[href*="guided_tour.css"]').length) {
        $('head').append('<link rel="stylesheet" href="/static/css/guided_tour.css">');
    }
    
    // Add CSS for intro.js if not already present
    if (!$('link[href*="introjs.min.css"]').length) {
        $('head').append('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/intro.js/6.0.0/introjs.min.css">');
    }
    
    // Add intro.js script if not already present
    if (typeof introJs === 'undefined') {
        $.getScript("https://cdnjs.cloudflare.com/ajax/libs/intro.js/6.0.0/intro.min.js", function() {
            console.log("intro.js loaded dynamically");
        });
    }
});

/**
 * Starts a guided tour based on its ID
 * @param {string} tourId - The ID of the tour to start
 */
function startTour(tourId) {
    console.log("Starting tour:", tourId);
    
    // If intro.js is not loaded yet, try again after a delay
    if (typeof introJs === 'undefined') {
        console.log("Waiting for intro.js to load...");
        setTimeout(function() {
            startTour(tourId);
        }, 500);
        return;
    }
    
    // Define tour configurations
    const tourConfigs = {
        // Welcome Tour - Navigation Overview
        welcomeTour: {
            steps: [
                {
                    element: 'nav.navbar',
                    title: 'Welcome to LevyMaster',
                    intro: 'This guided tour will help you learn the basics of navigating the LevyMaster system. Let\'s start with the main navigation bar.'
                },
                {
                    element: '#dashboardDropdown',
                    title: 'Dashboard',
                    intro: 'The Dashboard section provides an overview of your tax districts, recent activity, and key metrics.'
                },
                {
                    element: '#taxManagementDropdown',
                    title: 'Tax Management',
                    intro: 'Here you\'ll find tools for managing tax districts, codes, and levy calculations.'
                },
                {
                    element: '#dataHubDropdown',
                    title: 'Data Hub',
                    intro: 'The Data Hub contains tools for importing, exporting, and managing your tax data.'
                },
                {
                    element: '#analyticsDropdown',
                    title: 'Analytics',
                    intro: 'Use these tools to analyze trends, compare districts, and gain insights from your data.'
                },
                {
                    element: '#aiDropdown',
                    title: 'AI & Agents',
                    intro: 'Access AI-powered features including the MCP Army system and Levy Audit Assistant.'
                },
                {
                    element: '#reportsDropdown',
                    title: 'Reports',
                    intro: 'Generate various reports including district summaries, trend reports, and compliance documentation.'
                },
                {
                    element: '#adminDropdown',
                    title: 'Admin',
                    intro: 'Administrative functions including user management, system settings, and database operations.'
                },
                {
                    element: '#helpMenuToggle',
                    title: 'Help',
                    intro: 'Click here to access the Help Menu with quick guides and FAQs.'
                },
                {
                    element: '#resourcesDropdown',
                    title: 'Resources',
                    intro: 'Access additional resources including documentation, glossary, and more guided tours.'
                },
                {
                    element: '.container',
                    title: 'Ready to Get Started',
                    intro: 'That completes our overview of the main navigation. You can now explore the system or take additional guided tours for specific features.'
                }
            ],
            options: {
                showProgress: true,
                showBullets: false,
                disableInteraction: false,
                tooltipClass: 'welcome-tour'
            }
        },
        
        // Dashboard Tour
        dashboardTour: {
            steps: [
                {
                    element: '.dashboard-header',
                    title: 'Dashboard Overview',
                    intro: 'The dashboard provides a comprehensive overview of your tax districts and levy data.'
                },
                {
                    element: '.summary-stats',
                    title: 'Summary Statistics',
                    intro: 'These cards show key metrics including total assessed value, average tax rates, and more.'
                },
                {
                    element: '.recent-activity',
                    title: 'Recent Activity',
                    intro: 'Track recent changes and activities in your tax districts.'
                },
                {
                    element: '.district-overview',
                    title: 'District Overview',
                    intro: 'This section provides a snapshot of all your tax districts with quick access links.'
                },
                {
                    element: '.dashboard-charts',
                    title: 'Visual Analytics',
                    intro: 'Interactive charts help you visualize key trends and comparisons.'
                }
            ],
            options: {
                showProgress: true,
                showBullets: false,
                disableInteraction: false,
                tooltipClass: 'dashboard-tour'
            }
        },
        
        // Calculator Tour
        calculatorTour: {
            steps: [
                {
                    element: '.calculator-container',
                    title: 'Levy Calculator',
                    intro: 'The Levy Calculator helps you calculate tax rates and levy amounts for your districts.'
                },
                {
                    element: '.district-selector',
                    title: 'Select Tax District',
                    intro: 'Start by selecting the tax district you want to work with.'
                },
                {
                    element: '.year-selector',
                    title: 'Select Year',
                    intro: 'Choose the assessment year for your calculations.'
                },
                {
                    element: '.assessed-value-input',
                    title: 'Enter Assessed Value',
                    intro: 'Enter the total assessed value for the district and year.'
                },
                {
                    element: '.levy-inputs',
                    title: 'Levy Inputs',
                    intro: 'Enter the levy amounts for each fund category.'
                },
                {
                    element: '.calculator-actions',
                    title: 'Calculate and Save',
                    intro: 'Click Calculate to determine the levy rate, then Save to store your results.'
                },
                {
                    element: '.calculation-results',
                    title: 'Results',
                    intro: 'View your calculation results including rates, compliance status, and historical comparison.'
                }
            ],
            options: {
                showProgress: true,
                showBullets: false,
                disableInteraction: false,
                tooltipClass: 'calculator-tour'
            }
        },
        
        // Data Hub Tour
        dataHubTour: {
            steps: [
                {
                    element: '.data-hub-container',
                    title: 'Data Hub',
                    intro: 'The Data Hub centralizes all data management operations for your tax system.'
                },
                {
                    element: '.import-section',
                    title: 'Data Import',
                    intro: 'Use these tools to import property, district, and tax code data from various file formats.'
                },
                {
                    element: '.export-section',
                    title: 'Data Export',
                    intro: 'Export your data in various formats including Excel, CSV, and PDF.'
                },
                {
                    element: '.data-validation',
                    title: 'Data Validation',
                    intro: 'Validate your data to ensure accuracy and completeness before processing.'
                },
                {
                    element: '.import-history',
                    title: 'Import History',
                    intro: 'Review past data imports with details on status, records processed, and errors.'
                }
            ],
            options: {
                showProgress: true,
                showBullets: false,
                disableInteraction: false,
                tooltipClass: 'datahub-tour'
            }
        },
        
        // MCP Army Tour
        mcpArmyTour: {
            steps: [
                {
                    element: '.mcp-dashboard',
                    title: 'AI Agent System',
                    intro: 'The MCP Army is an advanced AI system that helps analyze and optimize your levy calculations.'
                },
                {
                    element: '.agent-cards',
                    title: 'Specialized AI Agents',
                    intro: 'Each card represents a specialized AI agent with unique capabilities.'
                },
                {
                    element: '.agent-workflow',
                    title: 'Agent Workflow',
                    intro: 'This diagram shows how agents interact to process your data and provide insights.'
                },
                {
                    element: '.analysis-tools',
                    title: 'Analysis Tools',
                    intro: 'Launch specialized analyses including trend detection, compliance checks, and forecasting.'
                },
                {
                    element: '.conversation-interface',
                    title: 'Conversational Interface',
                    intro: 'Ask questions and get insights from the AI system using natural language.'
                }
            ],
            options: {
                showProgress: true,
                showBullets: false,
                disableInteraction: false,
                tooltipClass: 'ai-tour'
            }
        },
        
        // Reports Tour
        reportsTour: {
            steps: [
                {
                    element: '.reports-container',
                    title: 'Reports Center',
                    intro: 'Generate standardized and custom reports for your tax data.'
                },
                {
                    element: '.report-categories',
                    title: 'Report Categories',
                    intro: 'Choose from different report types including district summaries, trends, and compliance.'
                },
                {
                    element: '.report-parameters',
                    title: 'Report Parameters',
                    intro: 'Customize your report by selecting districts, date ranges, and other parameters.'
                },
                {
                    element: '.export-options',
                    title: 'Export Options',
                    intro: 'Export your reports in various formats including PDF, Excel, and CSV.'
                },
                {
                    element: '.saved-reports',
                    title: 'Saved Reports',
                    intro: 'Access previously generated reports without regenerating them.'
                }
            ],
            options: {
                showProgress: true,
                showBullets: false,
                disableInteraction: false
            }
        }
    };
    
    // If tour exists, start it
    if (tourConfigs[tourId]) {
        // Initialize the tour
        const tour = introJs();
        
        // Configure the tour
        tour.setOptions({
            ...tourConfigs[tourId].options,
            steps: tourConfigs[tourId].steps,
            exitOnOverlayClick: false,
            exitOnEsc: true,
            nextLabel: 'Next',
            prevLabel: 'Back',
            doneLabel: 'Finish'
        });
        
        // Define tour completion handler
        tour.oncomplete(function() {
            console.log("Tour completed:", tourId);
            recordTourCompletion(tourId);
        });
        
        // Define tour exit handler
        tour.onexit(function() {
            console.log("Tour exited:", tourId);
        });
        
        // Start the tour
        tour.start();
        
        // Add the tour identifier class to body
        $('body').addClass(tourId);
    } else {
        console.error("Tour not found:", tourId);
    }
}

/**
 * Records that a tour has been completed
 * @param {string} tourId - The ID of the completed tour
 */
function recordTourCompletion(tourId) {
    // Send tour completion to server
    $.ajax({
        url: '/tours/complete/' + tourId,
        method: 'POST',
        success: function(response) {
            console.log("Tour completion recorded:", tourId);
            
            // Show success message
            $('body').append(
                '<div class="tour-completion-toast">' +
                '  <div class="toast-header">' +
                '    <i class="bi bi-check-circle-fill text-success me-2"></i>' +
                '    <strong class="me-auto">Tour Completed</strong>' +
                '    <button type="button" class="btn-close" data-bs-dismiss="toast"></button>' +
                '  </div>' +
                '  <div class="toast-body">' +
                '    Congratulations! You\'ve completed the ' + tourId + ' tour.' +
                '  </div>' +
                '</div>'
            );
            
            // Remove the tour identifier class from body
            $('body').removeClass(tourId);
            
            // Update UI to show completion if on tours page
            $('.tour-card[data-tour-id="' + tourId + '"] .tour-status')
                .removeClass('badge-secondary')
                .addClass('badge-success')
                .html('<i class="bi bi-check-circle"></i> Completed');
        },
        error: function(xhr, status, error) {
            console.error("Error recording tour completion:", error);
        }
    });
}