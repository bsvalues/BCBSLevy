/**
 * Help Menu System for Levy Calculation Application
 * 
 * This module manages the dynamic help menu that provides
 * context-sensitive help and documentation to users.
 */

// Initialize the help menu system when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log("Initializing help menu...");
    
    // Set up event listeners for the help menu and tour buttons
    setupHelpMenuListeners();
    
    // Setup tour listeners if available
    if (typeof setupTourListeners === 'function') {
        setupTourListeners();
    }
    
    // Add support for help tabs if needed
    createHelpTabListeners();
    
    // Don't load content or display the menu automatically
    console.log("Help Menu System initialized");
});

/**
 * Initialize the help menu system
 */
function initHelpMenu() {
    // Set up event listeners
    setupHelpMenuListeners();
    setupTourListeners();
    
    // Load default help content for the current page
    loadPageSpecificContent();
}

/**
 * Set up event listeners for the guided tour functionality
 */
function setupTourListeners() {
    // Start tour button in navbar
    const startTourButton = document.getElementById('startTourButton');
    if (startTourButton) {
        startTourButton.addEventListener('click', function() {
            startGuidedTour();
        });
    }
    
    // Start tour button in help menu
    const helpMenuTourBtn = document.getElementById('startGuidedTourBtn');
    if (helpMenuTourBtn) {
        helpMenuTourBtn.addEventListener('click', function() {
            toggleHelpMenu(false); // Close help menu
            startGuidedTour();     // Start the tour
        });
    }
}

/**
 * Start a guided tour based on the current page
 */
function startGuidedTour() {
    // Get current page context
    const pageContext = getCurrentPageContext();
    
    // Use intro.js to start a tour
    const intro = introJs();
    
    // Set tour options based on the page
    switch(pageContext) {
        case 'dashboard':
            intro.setOptions({
                steps: [
                    {
                        element: '.dashboard-header',
                        intro: 'Welcome to the LevyMaster Dashboard! This gives you an overview of your tax districts and levy calculations.',
                        position: 'bottom'
                    },
                    {
                        element: '.dashboard-metrics',
                        intro: 'Here are key metrics showing important statistics about your tax system.',
                        position: 'right'
                    },
                    {
                        element: '.dashboard-charts',
                        intro: 'These charts visualize your levy data for better insights.',
                        position: 'left'
                    },
                    {
                        element: '.dashboard-actions',
                        intro: 'Quick action buttons give you easy access to the most common tasks.',
                        position: 'top'
                    }
                ],
                showProgress: true,
                showBullets: false,
                showStepNumbers: true,
                doneLabel: 'Finish Tour',
                nextLabel: 'Next →',
                prevLabel: '← Back'
            });
            break;
            
        case 'levy-calculator':
            intro.setOptions({
                steps: [
                    {
                        element: '.calculator-container',
                        intro: 'Welcome to the Levy Calculator! This tool helps you calculate property tax levies for your districts.',
                        position: 'bottom'
                    },
                    {
                        element: '.district-selector',
                        intro: 'First, select the tax district you want to calculate levies for.',
                        position: 'right'
                    },
                    {
                        element: '.calculator-inputs',
                        intro: 'Enter the calculation parameters here, such as year and assessment values.',
                        position: 'left'
                    },
                    {
                        element: '.calculation-results',
                        intro: 'Your calculation results will appear here with detailed breakdowns.',
                        position: 'top'
                    }
                ],
                showProgress: true,
                showBullets: false,
                showStepNumbers: true,
                doneLabel: 'Finish Tour',
                nextLabel: 'Next →',
                prevLabel: '← Back'
            });
            break;
            
        default:
            // Generic tour for any page
            intro.setOptions({
                steps: [
                    {
                        element: '.navbar',
                        intro: 'This navigation bar gives you access to all the key features of LevyMaster.',
                        position: 'bottom'
                    },
                    {
                        element: '#helpMenuToggle',
                        intro: 'Click here to access the Help Center with guides and tutorials.',
                        position: 'left'
                    },
                    {
                        element: '#resourcesDropdown',
                        intro: 'Access documentation, glossaries, and other learning resources here.',
                        position: 'left'
                    },
                    {
                        element: 'footer',
                        intro: 'The footer contains quick links and additional resources.',
                        position: 'top'
                    }
                ],
                showProgress: true,
                showBullets: false,
                showStepNumbers: true,
                doneLabel: 'Finish Tour',
                nextLabel: 'Next →',
                prevLabel: '← Back'
            });
    }
    
    // Start the tour
    intro.start();
}

/**
 * Get the current page context based on the URL or page elements
 * @returns {string} The page context identifier
 */
function getCurrentPageContext() {
    const path = window.location.pathname;
    
    // Check URL patterns to determine context
    if (path.includes('dashboard')) {
        return 'dashboard';
    } else if (path.includes('levy-calculator')) {
        return 'levy-calculator';
    } else if (path.includes('data-import')) {
        return 'data-import';
    } else if (path.includes('forecasting')) {
        return 'forecasting';
    }
    
    // Check for page-specific elements as a fallback
    if (document.querySelector('.dashboard-container')) {
        return 'dashboard';
    } else if (document.querySelector('.calculator-container')) {
        return 'levy-calculator';
    }
    
    // Default context
    return 'default';
}

/**
 * Load content specific to the current page
 */
function loadPageSpecificContent() {
    const context = getCurrentPageContext();
    loadHelpContent(context);
}

/**
 * Create the necessary DOM elements for the help menu
 */
function createHelpMenuElements() {
    // Check if help menu already exists
    if (document.querySelector('.help-menu')) {
        return;
    }
    
    // Create backdrop
    const backdrop = document.createElement('div');
    backdrop.className = 'help-menu-backdrop';
    document.body.appendChild(backdrop);
    
    // Create help menu container
    const helpMenu = document.createElement('div');
    helpMenu.className = 'help-menu';
    helpMenu.innerHTML = `
        <div class="help-menu-header">
            <h5 class="mb-0">Help & Documentation</h5>
            <button type="button" class="btn-close btn-close-white" id="close-help-menu" aria-label="Close"></button>
        </div>
        <div class="help-menu-content">
            <div class="d-flex justify-content-center my-3">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(helpMenu);
}

/**
 * Set up event listeners for the help menu
 */
function setupHelpMenuListeners() {
    // Toggle help menu on button click - New selector that matches our updated HTML
    const helpMenuToggle = document.getElementById('helpMenuToggle');
    if (helpMenuToggle) {
        helpMenuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            toggleHelpMenu();
        });
    }
    
    // Close help menu when clicking the close button
    const closeButton = document.getElementById('helpMenuClose');
    if (closeButton) {
        closeButton.addEventListener('click', function() {
            toggleHelpMenu(false);
        });
    }
    
    // Close help menu when clicking the backdrop
    const backdrop = document.getElementById('helpMenuBackdrop');
    if (backdrop) {
        backdrop.addEventListener('click', function() {
            toggleHelpMenu(false);
        });
    }
    
    // Close help menu when pressing Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const helpMenu = document.querySelector('.help-menu');
            if (helpMenu && helpMenu.classList.contains('active')) {
                toggleHelpMenu(false);
            }
        }
    });
    
    // Listen for context changes to update help content
    document.addEventListener('contextChange', function(e) {
        if (e.detail && e.detail.context) {
            loadHelpContent(e.detail.context);
        }
    });
}

/**
 * Set up event listeners for the help menu tabs
 */
function createHelpTabListeners() {
    // Add event listeners to the help menu tabs
    const helpTabs = document.querySelectorAll('#helpTabs .nav-link');
    if (helpTabs && helpTabs.length > 0) {
        helpTabs.forEach(tab => {
            tab.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Remove active class from all tabs
                helpTabs.forEach(t => t.classList.remove('active'));
                
                // Add active class to clicked tab
                this.classList.add('active');
                
                // Hide all tab content
                const tabContents = document.querySelectorAll('.tab-pane');
                tabContents.forEach(content => {
                    content.classList.remove('show', 'active');
                });
                
                // Show the corresponding tab content
                const targetId = this.getAttribute('data-bs-target');
                if (targetId) {
                    const targetContent = document.querySelector(targetId);
                    if (targetContent) {
                        targetContent.classList.add('show', 'active');
                    }
                }
            });
        });
    }
}

/**
 * Toggle the visibility of the help menu
 * 
 * @param {boolean|undefined} show - If true, show the menu; if false, hide it; if undefined, toggle
 */
function toggleHelpMenu(show) {
    const helpMenu = document.getElementById('helpMenu');
    const backdrop = document.getElementById('helpMenuBackdrop');
    
    if (!helpMenu || !backdrop) {
        console.warn('Help menu elements not found');
        return;
    }
    
    // Determine if we should show or hide
    if (show === undefined) {
        show = !helpMenu.classList.contains('active');
    }
    
    // Update classes based on show/hide
    if (show) {
        helpMenu.classList.add('active');
        backdrop.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Set focus to the search input for accessibility
        const searchInput = helpMenu.querySelector('input[type="text"]');
        if (searchInput) {
            setTimeout(() => searchInput.focus(), 100);
        }
    } else {
        helpMenu.classList.remove('active');
        backdrop.classList.remove('active');
        document.body.style.overflow = '';
    }
}

/**
 * Load help content based on the current context
 * 
 * @param {string} context - The context identifier for which to load help content
 */
function loadHelpContent(context) {
    const contentContainer = document.querySelector('.help-menu-content');
    
    if (!contentContainer) {
        return;
    }
    
    // We'd typically fetch this from a server based on context
    // For now, we'll use predefined content based on context
    
    // Show loading indicator
    contentContainer.innerHTML = `
        <div class="d-flex justify-content-center my-3">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
    
    // Simulate network delay
    setTimeout(() => {
        let content = '';
        
        switch(context) {
            case 'dashboard':
                content = getDashboardHelp();
                break;
            case 'levy-calculator':
                content = getLevyCalculatorHelp();
                break;
            case 'data-import':
                content = getDataImportHelp();
                break;
            case 'forecasting':
                content = getForecastingHelp();
                break;
            default:
                content = getDefaultHelp();
        }
        
        contentContainer.innerHTML = content;
        
        // Add event listeners to collapsible sections
        const accordionButtons = contentContainer.querySelectorAll('.accordion-button');
        accordionButtons.forEach(button => {
            button.addEventListener('click', function() {
                this.classList.toggle('collapsed');
                const target = document.getElementById(this.getAttribute('data-bs-target').substring(1));
                if (target) {
                    target.classList.toggle('show');
                }
            });
        });
    }, 500);
}

/**
 * Get default help content
 * @returns {string} HTML content
 */
function getDefaultHelp() {
    return `
        <div class="mb-4">
            <h4>Welcome to the Levy Calculation System</h4>
            <p>This system helps you calculate and manage property tax levies. Use the navigation menu to access the various features.</p>
        </div>
        
        <div class="accordion" id="helpAccordion">
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseGettingStarted">
                        Getting Started
                    </button>
                </h2>
                <div id="collapseGettingStarted" class="accordion-collapse collapse show">
                    <div class="accordion-body">
                        <p>New to the system? Here's how to get started:</p>
                        <ol>
                            <li>Navigate to the <strong>Dashboard</strong> to see an overview of your data</li>
                            <li>Import property data and tax districts using the <strong>Data Management</strong> section</li>
                            <li>Create levy calculations using the <strong>Levy Calculator</strong></li>
                            <li>Generate reports from the <strong>Reports</strong> section</li>
                        </ol>
                    </div>
                </div>
            </div>
            
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseKeyFeatures">
                        Key Features
                    </button>
                </h2>
                <div id="collapseKeyFeatures" class="accordion-collapse collapse">
                    <div class="accordion-body">
                        <ul>
                            <li><strong>Levy Calculator</strong>: Calculate property tax levies with statutory compliance checks</li>
                            <li><strong>Data Management</strong>: Import and export data for tax districts, tax codes, and properties</li>
                            <li><strong>Forecasting</strong>: Project future levy rates based on historical data</li>
                            <li><strong>Reports</strong>: Generate comprehensive reports for various stakeholders</li>
                            <li><strong>Historical Analysis</strong>: Analyze historical levy data for trends and patterns</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseQuickTips">
                        Quick Tips
                    </button>
                </h2>
                <div id="collapseQuickTips" class="accordion-collapse collapse">
                    <div class="accordion-body">
                        <ul>
                            <li>Use the <strong>Guided Tours</strong> for step-by-step instructions on specific features</li>
                            <li>Check the <strong>Glossary</strong> for definitions of levy-related terms</li>
                            <li>Enable <strong>Dark Mode</strong> for reduced eye strain in low-light environments</li>
                            <li>Access context-sensitive help by clicking the <strong>Help</strong> button while on any page</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Get dashboard help content
 * @returns {string} HTML content
 */
function getDashboardHelp() {
    return `
        <div class="mb-4">
            <h4>Dashboard Help</h4>
            <p>The dashboard provides an overview of your levy calculation system with key metrics and quick access to common tasks.</p>
        </div>
        
        <div class="accordion" id="dashboardHelpAccordion">
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseDashboardOverview">
                        Dashboard Overview
                    </button>
                </h2>
                <div id="collapseDashboardOverview" class="accordion-collapse collapse show">
                    <div class="accordion-body">
                        <p>The dashboard is divided into several sections:</p>
                        <ul>
                            <li><strong>Key Metrics</strong>: Shows count of tax districts, tax codes, properties, and average levy rate</li>
                            <li><strong>System Overview</strong>: Displays total assessed value, total levy amount, and tax year</li>
                            <li><strong>Quick Actions</strong>: Provides quick access to common tasks</li>
                            <li><strong>Recent Activity</strong>: Shows recent data imports and exports</li>
                            <li><strong>Compliance Check</strong>: Indicates whether levy calculations comply with statutory requirements</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseDashboardActions">
                        Using Quick Actions
                    </button>
                </h2>
                <div id="collapseDashboardActions" class="accordion-collapse collapse">
                    <div class="accordion-body">
                        <p>The Quick Actions section provides shortcuts to common tasks:</p>
                        <ul>
                            <li><strong>Calculate Levy</strong>: Start a new levy calculation</li>
                            <li><strong>Import Data</strong>: Import tax districts or properties</li>
                            <li><strong>Generate Report</strong>: Create summary reports</li>
                            <li><strong>Run Forecast</strong>: Project future levy rates</li>
                        </ul>
                        <p>Click on any action to navigate directly to that feature.</p>
                    </div>
                </div>
            </div>
            
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseDashboardCharts">
                        Understanding Charts
                    </button>
                </h2>
                <div id="collapseDashboardCharts" class="accordion-collapse collapse">
                    <div class="accordion-body">
                        <p>The dashboard includes a chart showing the distribution of levy amounts by district type:</p>
                        <ul>
                            <li>Each bar represents a different district type (School, County, City, etc.)</li>
                            <li>The height of each bar indicates the total levy amount for that district type</li>
                            <li>Hover over a bar to see the exact levy amount</li>
                        </ul>
                        <p>Use the year dropdown to view data for different tax years.</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Get levy calculator help content
 * @returns {string} HTML content
 */
function getLevyCalculatorHelp() {
    return `
        <div class="mb-4">
            <h4>Levy Calculator Help</h4>
            <p>The Levy Calculator helps you calculate property tax levies with statutory compliance checks.</p>
        </div>
        
        <div class="accordion" id="levyCalculatorHelpAccordion">
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseCalculatorOverview">
                        Calculator Overview
                    </button>
                </h2>
                <div id="collapseCalculatorOverview" class="accordion-collapse collapse show">
                    <div class="accordion-body">
                        <p>The Levy Calculator allows you to:</p>
                        <ul>
                            <li>Calculate levy rates based on assessed values and levy amounts</li>
                            <li>Check compliance with statutory limits</li>
                            <li>Apply various levy limits and adjustments</li>
                            <li>Save and compare multiple calculation scenarios</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseCalculationSteps">
                        Calculation Steps
                    </button>
                </h2>
                <div id="collapseCalculationSteps" class="accordion-collapse collapse">
                    <div class="accordion-body">
                        <ol>
                            <li>Select a tax district from the dropdown</li>
                            <li>Choose the tax year for the calculation</li>
                            <li>Enter the desired levy amount</li>
                            <li>Apply any adjustments (new construction, annexations, etc.)</li>
                            <li>Click "Calculate" to see the resulting levy rate</li>
                            <li>Review the compliance status and warnings</li>
                            <li>Save the calculation if desired</li>
                        </ol>
                    </div>
                </div>
            </div>
            
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseComplianceChecks">
                        Compliance Checks
                    </button>
                </h2>
                <div id="collapseComplianceChecks" class="accordion-collapse collapse">
                    <div class="accordion-body">
                        <p>The system performs these compliance checks:</p>
                        <ul>
                            <li><strong>Statutory Rate Limit</strong>: Ensures the levy rate doesn't exceed the maximum allowed by law</li>
                            <li><strong>101% Limit</strong>: Checks that the levy amount doesn't exceed 101% of the highest levy in the past three years</li>
                            <li><strong>Banked Capacity</strong>: Calculates available banked capacity if the district doesn't use its full levy authority</li>
                            <li><strong>New Construction</strong>: Validates adjustments for new construction</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Get data import help content
 * @returns {string} HTML content
 */
function getDataImportHelp() {
    return `
        <div class="mb-4">
            <h4>Data Import Help</h4>
            <p>The Data Import feature allows you to import property data, tax districts, and other information into the system.</p>
        </div>
        
        <div class="accordion" id="dataImportHelpAccordion">
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseImportOverview">
                        Import Overview
                    </button>
                </h2>
                <div id="collapseImportOverview" class="accordion-collapse collapse show">
                    <div class="accordion-body">
                        <p>You can import various types of data:</p>
                        <ul>
                            <li><strong>Tax Districts</strong>: Import levy authorities like school districts, fire districts, etc.</li>
                            <li><strong>Tax Codes</strong>: Import tax code areas that group multiple districts</li>
                            <li><strong>Properties</strong>: Import property data including assessed values</li>
                            <li><strong>Levy Rates</strong>: Import historical levy rates</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseFileFormats">
                        Supported File Formats
                    </button>
                </h2>
                <div id="collapseFileFormats" class="accordion-collapse collapse">
                    <div class="accordion-body">
                        <p>The system supports these file formats:</p>
                        <ul>
                            <li><strong>TXT</strong>: Standard fixed-width or delimiter-separated text files</li>
                            <li><strong>CSV</strong>: Comma-separated values</li>
                            <li><strong>XLSX</strong>: Microsoft Excel spreadsheets</li>
                            <li><strong>XLS</strong>: Legacy Microsoft Excel format</li>
                            <li><strong>XML</strong>: Extensible Markup Language files</li>
                        </ul>
                        <p>The system will attempt to automatically detect the format and structure of the file.</p>
                    </div>
                </div>
            </div>
            
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseImportSteps">
                        Import Steps
                    </button>
                </h2>
                <div id="collapseImportSteps" class="accordion-collapse collapse">
                    <div class="accordion-body">
                        <ol>
                            <li>Select the type of data you want to import</li>
                            <li>Choose the tax year for the imported data</li>
                            <li>Upload your file or select from previously uploaded files</li>
                            <li>Map columns to database fields if needed</li>
                            <li>Preview the data to ensure it looks correct</li>
                            <li>Click "Import" to process the data</li>
                            <li>Review the import results and fix any errors</li>
                        </ol>
                    </div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Get forecasting help content
 * @returns {string} HTML content
 */
function getForecastingHelp() {
    return `
        <div class="mb-4">
            <h4>Forecasting Help</h4>
            <p>The Forecasting feature helps you project future levy rates and amounts based on historical data and trends.</p>
        </div>
        
        <div class="accordion" id="forecastingHelpAccordion">
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseForecastOverview">
                        Forecasting Overview
                    </button>
                </h2>
                <div id="collapseForecastOverview" class="accordion-collapse collapse show">
                    <div class="accordion-body">
                        <p>The Forecasting tool allows you to:</p>
                        <ul>
                            <li>Project future levy rates based on historical trends</li>
                            <li>Model different growth scenarios</li>
                            <li>Analyze the impact of new construction and annexations</li>
                            <li>Generate visualizations of projected changes</li>
                            <li>Create "what-if" scenarios to support planning</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseForecastMethods">
                        Forecasting Methods
                    </button>
                </h2>
                <div id="collapseForecastMethods" class="accordion-collapse collapse">
                    <div class="accordion-body">
                        <p>The system supports several forecasting methods:</p>
                        <ul>
                            <li><strong>Linear Trend</strong>: Projects based on a linear trend line fitted to historical data</li>
                            <li><strong>Exponential Growth</strong>: Models exponential growth patterns</li>
                            <li><strong>ARIMA</strong>: Time series forecasting with Auto-Regressive Integrated Moving Average</li>
                            <li><strong>Ensemble</strong>: Combines multiple methods for improved accuracy</li>
                        </ul>
                        <p>Each method has different strengths and is suitable for different scenarios.</p>
                    </div>
                </div>
            </div>
            
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseForecastSteps">
                        Creating a Forecast
                    </button>
                </h2>
                <div id="collapseForecastSteps" class="accordion-collapse collapse">
                    <div class="accordion-body">
                        <ol>
                            <li>Select a tax district or tax code to forecast</li>
                            <li>Choose the base year as the starting point</li>
                            <li>Specify the number of years to forecast</li>
                            <li>Select a forecasting method</li>
                            <li>Input any adjustments or assumptions (new construction, annexations)</li>
                            <li>Click "Generate Forecast" to create projections</li>
                            <li>Review the results and confidence intervals</li>
                            <li>Save or export the forecast if desired</li>
                        </ol>
                    </div>
                </div>
            </div>
        </div>
    `;
}