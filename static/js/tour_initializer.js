/**
 * Tour Initializer - Manages guided tours in the Levy Calculation System
 * 
 * This script initializes and manages IntroJS tours for different pages
 * of the application. It loads tour configurations and handles tour
 * completion and user preferences.
 */

// Tour configuration object
const tourConfigurations = {
    // Dashboard tour
    dashboard: {
        steps: [
            {
                element: '.dashboard-overview',
                title: 'Dashboard Overview',
                intro: 'Welcome to your dashboard! This is where you can see an overview of your tax districts, properties, and recent levy calculations.',
                position: 'right'
            },
            {
                element: '.dashboard-metrics',
                title: 'Key Metrics',
                intro: 'These cards show you the key metrics about your tax districts, such as total assessed value and levy amounts.',
                position: 'bottom'
            },
            {
                element: '.dashboard-recent-activity',
                title: 'Recent Activity',
                intro: 'Here you can see your recent activity, including imports, exports, and calculations.',
                position: 'left'
            },
            {
                element: '.dashboard-charts',
                title: 'Charts and Visualizations',
                intro: 'These charts provide visual representations of your tax data to help you identify trends and patterns.',
                position: 'top'
            },
            {
                element: '.dashboard-actions',
                title: 'Quick Actions',
                intro: 'These buttons allow you to quickly access common actions like starting a new calculation or importing data.',
                position: 'left'
            },
            {
                element: '.dashboard-notifications',
                title: 'Notifications',
                intro: 'You\'ll receive important notifications here about compliance issues, upcoming deadlines, and system updates.',
                position: 'bottom'
            }
        ]
    },
    
    // Levy calculator tour
    levy_calculator: {
        steps: [
            {
                element: '.calculator-header',
                title: 'Levy Calculator',
                intro: 'This is the levy calculator, where you can calculate property tax levies for different scenarios.',
                position: 'bottom'
            },
            {
                element: '.tax-district-selector',
                title: 'Select Tax District',
                intro: 'Start by selecting the tax district you want to calculate levies for.',
                position: 'right'
            },
            {
                element: '.calculation-inputs',
                title: 'Input Parameters',
                intro: 'Enter the required information such as year, assessed values, and rate adjustments.',
                position: 'left'
            },
            {
                element: '.scenario-options',
                title: 'Scenario Options',
                intro: 'You can create different scenarios to compare various levy outcomes.',
                position: 'top'
            },
            {
                element: '.calculate-button',
                title: 'Calculate Button',
                intro: 'Click this button to calculate the levy based on your inputs.',
                position: 'bottom'
            }
        ]
    },
    
    // Data import tour
    data_import: {
        steps: [
            {
                element: '.import-header',
                title: 'Data Import',
                intro: 'This page allows you to import tax district and property data into the system.',
                position: 'bottom'
            },
            {
                element: '.file-upload',
                title: 'File Upload',
                intro: 'You can upload files in various formats including TXT, XLS, XLSX, and XML.',
                position: 'right'
            },
            {
                element: '.import-options',
                title: 'Import Options',
                intro: 'Configure how the data should be imported with these options.',
                position: 'left'
            },
            {
                element: '.submit-import',
                title: 'Submit Import',
                intro: 'Click this button to start the import process.',
                position: 'bottom'
            }
        ]
    },
    
    // Property search tour
    property_search: {
        steps: [
            {
                element: '.search-header',
                title: 'Property Search',
                intro: 'This page allows you to search for properties in the system.',
                position: 'bottom'
            },
            {
                element: '.search-form',
                title: 'Search Criteria',
                intro: 'Enter your search criteria here to find specific properties.',
                position: 'right'
            },
            {
                element: '.search-results',
                title: 'Search Results',
                intro: 'The search results will appear here, showing matching properties.',
                position: 'top'
            },
            {
                element: '.property-details',
                title: 'Property Details',
                intro: 'Click on a property to view its detailed information.',
                position: 'left'
            }
        ]
    },
    
    // Admin dashboard tour
    'admin-dashboard': {
        steps: [
            {
                element: '.admin-header',
                title: 'Admin Dashboard',
                intro: 'Welcome to the Admin Dashboard! Here you can manage all aspects of the Levy Calculation System.',
                position: 'bottom'
            },
            {
                element: '.admin-users',
                title: 'User Management',
                intro: 'Manage system users, including creating new accounts and setting permissions.',
                position: 'right'
            },
            {
                element: '.admin-districts',
                title: 'Tax District Management',
                intro: 'Administer tax districts, including creation, deletion, and configuration.',
                position: 'left'
            },
            {
                element: '.admin-settings',
                title: 'System Settings',
                intro: 'Configure system-wide settings such as default values, display options, and calculation parameters.',
                position: 'top'
            },
            {
                element: '.admin-logs',
                title: 'System Logs',
                intro: 'Review system logs to monitor activity and troubleshoot issues.',
                position: 'bottom'
            }
        ]
    },
    
    // Public lookup tour
    'public-lookup': {
        steps: [
            {
                element: '.public-header',
                title: 'Property Tax Lookup',
                intro: 'Welcome to the Public Property Tax Lookup! This tool allows you to search for properties and view their tax information.',
                position: 'bottom'
            },
            {
                element: '.lookup-form',
                title: 'Search Form',
                intro: 'Enter your property details here to find specific property tax information.',
                position: 'right'
            },
            {
                element: '.search-options',
                title: 'Search Options',
                intro: 'Use these options to refine your search by district, year, or other criteria.',
                position: 'top'
            },
            {
                element: '.district-list',
                title: 'Tax District List',
                intro: 'Browse tax districts to find your property or view district-wide information.',
                position: 'left'
            }
        ]
    },
    
    // Reports tour
    'reports': {
        steps: [
            {
                element: '.reports-header',
                title: 'Reports Dashboard',
                intro: 'Welcome to the Reports Dashboard! Here you can generate and view various reports about tax levies and properties.',
                position: 'bottom'
            },
            {
                element: '.report-selector',
                title: 'Report Selection',
                intro: 'Choose from different report types such as district summaries, historical trends, and compliance reports.',
                position: 'right'
            },
            {
                element: '.report-filters',
                title: 'Report Filters',
                intro: 'Customize your report by applying filters for specific time periods, districts, or properties.',
                position: 'top'
            },
            {
                element: '.export-options',
                title: 'Export Options',
                intro: 'Download your report in various formats including PDF, Excel, or CSV for sharing and analysis.',
                position: 'left'
            },
            {
                element: '.saved-reports',
                title: 'Saved Reports',
                intro: 'Access your previously generated reports or reports shared with you by other users.',
                position: 'bottom'
            }
        ]
    },
    
    // Levy calculation tour (alternative to levy_calculator with different CSS selectors)
    'levy-calculation': {
        steps: [
            {
                element: '#calculator-container',
                title: 'Levy Calculation Tool',
                intro: 'Welcome to the Levy Calculation Tool! This powerful calculator helps you determine property tax levies for your districts.',
                position: 'bottom'
            },
            {
                element: '#district-select',
                title: 'District Selection',
                intro: 'Select the tax district you want to calculate levies for from this dropdown menu.',
                position: 'right'
            },
            {
                element: '#year-select',
                title: 'Year Selection',
                intro: 'Choose the tax year for which you want to calculate the levy.',
                position: 'left'
            },
            {
                element: '#assessment-input',
                title: 'Assessment Value',
                intro: 'Enter the total assessed value for the district or leave blank to use the value from the database.',
                position: 'top'
            },
            {
                element: '#rate-adjustment',
                title: 'Rate Adjustment',
                intro: 'Apply adjustments to the levy rate based on special circumstances or legal requirements.',
                position: 'bottom'
            },
            {
                element: '#calculate-button',
                title: 'Calculate Levy',
                intro: 'Click this button to calculate the levy based on your inputs and view the results.',
                position: 'right'
            }
        ]
    },
    
    // Property Lookup tour for homepage button
    'property-lookup': {
        steps: [
            {
                element: '#property-lookup-container',
                title: 'Property Lookup Tool',
                intro: 'Welcome to the Property Lookup Tool! This tool helps you find detailed information about properties in your district.',
                position: 'bottom'
            },
            {
                element: '#property-search-form',
                title: 'Search Form',
                intro: 'Use this form to search for properties by address, PIN, or tax code.',
                position: 'right'
            },
            {
                element: '#property-search-results',
                title: 'Search Results',
                intro: 'Your search results will appear here with property details and tax information.',
                position: 'top'
            }
        ]
    },
    
    // Public Search tour for homepage button
    'public-search': {
        steps: [
            {
                element: '#public-search-container',
                title: 'Public Property Search',
                intro: 'Welcome to the Public Property Search! This tool allows the public to search for property tax information.',
                position: 'bottom'
            },
            {
                element: '#search-criteria',
                title: 'Search Criteria',
                intro: 'Enter your search criteria to find property tax information.',
                position: 'right'
            },
            {
                element: '#public-search-results',
                title: 'Results',
                intro: 'Your search results will display here with public tax information.',
                position: 'top'
            }
        ]
    },
    
    // Historical Analysis tour for homepage card
    'historical-analysis': {
        steps: [
            {
                element: '#historical-analysis-container',
                title: 'Historical Analysis Tool',
                intro: 'Welcome to the Historical Analysis Tool! This powerful tool helps you analyze historical tax trends.',
                position: 'bottom'
            },
            {
                element: '#historical-filters',
                title: 'Analysis Filters',
                intro: 'Use these filters to focus your analysis on specific time periods, districts, or properties.',
                position: 'right'
            },
            {
                element: '#historical-charts',
                title: 'Trend Visualization',
                intro: 'These charts visualize historical trends to help identify patterns and anomalies.',
                position: 'top'
            },
            {
                element: '#export-analysis',
                title: 'Export Analysis',
                intro: 'Export your analysis results in various formats for reporting and presentations.',
                position: 'left'
            }
        ]
    },
    
    // Compliance tour for homepage card
    'compliance': {
        steps: [
            {
                element: '#compliance-container',
                title: 'Compliance Verification',
                intro: 'Welcome to the Compliance Verification Tool! This tool helps ensure your tax calculations comply with all applicable laws and regulations.',
                position: 'bottom'
            },
            {
                element: '#compliance-checks',
                title: 'Compliance Checks',
                intro: 'Run these automated checks to verify compliance with various requirements.',
                position: 'right'
            },
            {
                element: '#compliance-reports',
                title: 'Compliance Reports',
                intro: 'Generate detailed compliance reports for auditing and documentation purposes.',
                position: 'top'
            },
            {
                element: '#compliance-history',
                title: 'Compliance History',
                intro: 'Review historical compliance data to track improvements over time.',
                position: 'left'
            }
        ]
    }
};

/**
 * Check if a tour should be automatically shown based on the current page and user preferences.
 */
function checkForAutomaticTour() {
    // Check the current path
    const path = window.location.pathname;
    
    // Check if there's a tour parameter in the URL
    const urlParams = new URLSearchParams(window.location.search);
    const tourParam = urlParams.get('tour');
    
    // If there's a tour parameter, start that tour
    if (tourParam && tourConfigurations[tourParam]) {
        startTour(tourParam);
        return;
    }
    
    // Check if auto tours are enabled
    const enableAutoTours = localStorage.getItem('enable_auto_tours') !== 'false';
    if (!enableAutoTours) {
        return;
    }
    
    // Determine which tour to show based on the current path
    let tourToShow = null;
    
    if (path === '/dashboard' || path === '/') {
        tourToShow = 'dashboard';
    } else if (path === '/levy-calculator') {
        tourToShow = 'levy-calculation';
    } else if (path === '/import') {
        tourToShow = 'data_import';
    } else if (path === '/property-lookup') {
        tourToShow = 'property_search';
    } else if (path === '/admin' || path === '/admin/dashboard') {
        tourToShow = 'admin-dashboard';
    } else if (path === '/public/lookup') {
        tourToShow = 'public-lookup';
    } else if (path === '/reports') {
        tourToShow = 'reports';
    }
    
    // Start the tour if it's relevant to the current page and hasn't been completed
    if (tourToShow && !isTourCompleted(tourToShow)) {
        startTour(tourToShow);
    }
}

/**
 * Check if a tour has been completed by the user.
 * 
 * @param {string} tourName - The name of the tour to check
 * @returns {boolean} - True if the tour has been completed
 */
function isTourCompleted(tourName) {
    return localStorage.getItem(`tour_${tourName}_completed`) === 'true';
}

/**
 * Mark a tour as completed.
 * 
 * @param {string} tourName - The name of the tour to mark as completed
 */
function markTourCompleted(tourName) {
    localStorage.setItem(`tour_${tourName}_completed`, 'true');
}

/**
 * Start a guided tour.
 * 
 * @param {string} tourName - The name of the tour to start
 */
function startTour(tourName) {
    // Check if the tour exists
    if (!tourConfigurations[tourName]) {
        console.error(`Tour '${tourName}' not found`);
        return;
    }
    
    const tourConfig = tourConfigurations[tourName];
    
    // Skip if the tour has no steps
    if (!tourConfig.steps || tourConfig.steps.length === 0) {
        console.error(`Tour '${tourName}' has no steps`);
        return;
    }
    
    // Check if introJs is available
    if (typeof introJs === 'undefined') {
        console.error('IntroJS library not loaded');
        return;
    }
    
    // Initialize introjs with the tour configuration
    const intro = introJs();
    
    // Configure the tour
    intro.setOptions({
        steps: tourConfig.steps,
        showProgress: localStorage.getItem('show_progress_bar') !== 'false',
        showBullets: localStorage.getItem('show_bullets') !== 'false',
        exitOnOverlayClick: localStorage.getItem('exit_on_overlay_click') !== 'false',
        scrollToElement: localStorage.getItem('scroll_to_element') !== 'false',
        doneLabel: 'Finish',
        nextLabel: 'Next →',
        prevLabel: '← Back',
        skipLabel: 'Skip'
    });
    
    // Add event listeners
    intro.oncomplete(function() {
        // Mark the tour as completed when the user finishes it
        markTourCompleted(tourName);
    });
    
    intro.onexit(function() {
        // Don't mark as completed if user exits early
    });
    
    // Start the tour
    intro.start();
}

/**
 * Safe event listener addition with element existence check
 * @param {string} selector - The CSS selector for the elements
 * @param {string} event - The event to listen for
 * @param {Function} callback - The callback function
 */
function safeAddEventListener(selector, event, callback) {
    const elements = document.querySelectorAll(selector);
    if (elements && elements.length > 0) {
        elements.forEach(element => {
            element.addEventListener(event, callback);
        });
    }
}

// Initialize when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('LevyMaster JS initialized successfully');
    
    // Don't automatically start tours on page load
    // checkForAutomaticTour();
    
    // Add event listeners to tour trigger buttons (safely)
    safeAddEventListener('[data-tour]', 'click', function() {
        const tourName = this.getAttribute('data-tour');
        startTour(tourName);
    });
});

// Export functions for use in other scripts
window.tourInitializer = {
    startTour: startTour,
    checkForAutomaticTour: checkForAutomaticTour,
    isTourCompleted: isTourCompleted,
    markTourCompleted: markTourCompleted
};
