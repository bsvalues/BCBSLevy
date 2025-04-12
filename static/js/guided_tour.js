/**
 * Guided Tour Implementation using intro.js
 * 
 * This module provides interactive onboarding tours for the LevyMaster application.
 * It includes multiple tour paths based on user role and context.
 */

// Configuration for different tour paths
const tourConfig = {
    // New user welcome tour
    welcomeTour: [
        {
            element: '.navbar-brand',
            title: 'Welcome to LevyMaster',
            intro: 'Welcome to the Benton County Levy Calculation System. This guided tour will help you get familiar with the interface and key features.',
            position: 'bottom'
        },
        {
            element: '#navbarNav',
            title: 'Navigation Menu',
            intro: 'The navigation menu is organized into logical sections. We\'ve streamlined it to make finding features easier.',
            position: 'bottom'
        },
        {
            element: '[href$="dashboard"]',
            title: 'Dashboard',
            intro: 'Your central hub shows key metrics, recent activity, and system status.',
            position: 'right'
        },
        {
            element: '#taxDropdown',
            title: 'Tax Management',
            intro: 'Access core tax calculation and analysis tools here, including the Levy Calculator and Tax Districts.',
            position: 'right'
        },
        {
            element: '#dataDropdown',
            title: 'Data Hub',
            intro: 'Import, export, and search for data. This central location manages all your data operations.',
            position: 'right'
        },
        {
            element: '#analyticsDropdown',
            title: 'Analytics & Insights',
            intro: 'Powerful analysis tools including forecasting, historical analysis, and data visualization.',
            position: 'right'
        },
        {
            element: '#aiDropdown',
            title: 'AI & Agents',
            intro: 'Our intelligent assistant system helps with complex calculations and data analysis.',
            position: 'right'
        },
        {
            element: '#reportsDropdown',
            title: 'Reports',
            intro: 'Generate standardized and custom reports for different stakeholders.',
            position: 'left'
        },
        {
            element: '#helpMenuToggle',
            title: 'Help Center',
            intro: 'Click here anytime to access help resources, tutorials, and documentation.',
            position: 'left'
        },
        {
            element: '#resourcesDropdown',
            title: 'Resources',
            intro: 'Access guided tours, glossary, and training materials.',
            position: 'left'
        },
        {
            // No element - final step
            title: 'Ready to Start',
            intro: 'You\'re all set! You can restart this tour anytime from the Help menu. Click "Done" to begin using LevyMaster.',
        }
    ],

    // Dashboard specific tour
    dashboardTour: [
        {
            element: '.dashboard-kpi-cards',
            title: 'Key Performance Indicators',
            intro: 'These cards show important metrics at a glance.',
            position: 'bottom'
        },
        {
            element: '.dashboard-recent-activity',
            title: 'Recent Activity',
            intro: 'Track recent changes and updates to your data.',
            position: 'right'
        },
        {
            element: '.dashboard-quick-actions',
            title: 'Quick Actions',
            intro: 'Common tasks can be started directly from these buttons.',
            position: 'left'
        },
        {
            element: '.dashboard-visualization',
            title: 'Data Visualization',
            intro: 'Interactive charts show trends and patterns in your data.',
            position: 'top'
        },
        {
            // No element - final step
            title: 'Dashboard Tour Complete',
            intro: 'You now know how to use the dashboard. Explore the other sections of the application when you\'re ready.',
        }
    ],

    // Levy Calculator tour
    calculatorTour: [
        {
            element: '.calculator-district-select',
            title: 'Select Tax District',
            intro: 'Start by selecting the tax district you want to calculate levy for.',
            position: 'right'
        },
        {
            element: '.calculator-year-select',
            title: 'Select Year',
            intro: 'Choose the year for your levy calculation.',
            position: 'right'
        },
        {
            element: '.calculator-inputs',
            title: 'Calculation Inputs',
            intro: 'Enter or adjust values in these fields to see how they affect the levy calculation.',
            position: 'left'
        },
        {
            element: '.calculator-results',
            title: 'Calculation Results',
            intro: 'The calculated results will appear here in real-time as you update inputs.',
            position: 'top'
        },
        {
            element: '.calculator-actions',
            title: 'Save & Export',
            intro: 'Save your calculations or export them to various formats using these buttons.',
            position: 'left'
        },
        {
            // No element - final step
            title: 'Calculator Tour Complete',
            intro: 'You now know how to use the Levy Calculator. Try making a calculation on your own.',
        }
    ],

    // Data Import tour
    dataImportTour: [
        {
            element: '.import-source-select',
            title: 'Select Data Source',
            intro: 'Choose where your data is coming from.',
            position: 'right'
        },
        {
            element: '.import-file-upload',
            title: 'Upload Files',
            intro: 'Upload your data files here. We support CSV, Excel, and XML formats.',
            position: 'bottom'
        },
        {
            element: '.import-mapping',
            title: 'Field Mapping',
            intro: 'Map your data columns to our system fields. The system will try to match them automatically.',
            position: 'left'
        },
        {
            element: '.import-validation',
            title: 'Data Validation',
            intro: 'The system checks your data for errors before importing.',
            position: 'top'
        },
        {
            element: '.import-summary',
            title: 'Import Summary',
            intro: 'Review the import summary before finalizing.',
            position: 'right'
        },
        {
            // No element - final step
            title: 'Data Import Tour Complete',
            intro: 'You now know how to import data into the system.',
        }
    ],
};

// User preference storage for tours
const tourPreferences = {
    // Save whether user has completed specific tours
    markTourComplete: function(tourName) {
        localStorage.setItem(`tour_${tourName}_completed`, 'true');
    },
    
    // Check if user has completed a tour
    isTourCompleted: function(tourName) {
        return localStorage.getItem(`tour_${tourName}_completed`) === 'true';
    },
    
    // Reset tour completion status
    resetTourStatus: function(tourName) {
        localStorage.removeItem(`tour_${tourName}_completed`);
    },
    
    // Reset all tour completion statuses
    resetAllTours: function() {
        Object.keys(tourConfig).forEach(tourName => {
            this.resetTourStatus(tourName);
        });
    }
};

// Tour controller
const TourController = {
    // Current tour instance
    currentTour: null,
    
    // Initialize tour system
    init: function() {
        // Add tour buttons to the Help menu
        this.addTourMenuItems();
        
        // Check if first-time user
        this.checkFirstTimeUser();
        
        // Setup event listeners
        this.setupEventListeners();
    },
    
    // Add tour options to Help menu
    addTourMenuItems: function() {
        const helpMenu = document.querySelector('.help-menu-body');
        if (!helpMenu) return;
        
        // Create tours section if doesn't exist
        let toursSection = helpMenu.querySelector('.help-section:first-child');
        const tourItems = document.createElement('div');
        tourItems.classList.add('mt-3');
        tourItems.innerHTML = `
            <h6>Guided Tours</h6>
            <ul class="list-unstyled">
                <li><a href="#" id="start-welcome-tour"><i class="bi bi-info-circle me-2"></i>Navigation Overview</a></li>
                <li><a href="#" id="start-dashboard-tour"><i class="bi bi-speedometer2 me-2"></i>Dashboard Tour</a></li>
                <li><a href="#" id="start-calculator-tour"><i class="bi bi-calculator me-2"></i>Levy Calculator Guide</a></li>
                <li><a href="#" id="start-import-tour"><i class="bi bi-upload me-2"></i>Data Import Tutorial</a></li>
                <li class="mt-2"><a href="#" id="reset-all-tours"><i class="bi bi-arrow-counterclockwise me-2"></i>Reset All Tours</a></li>
            </ul>
        `;
        toursSection.appendChild(tourItems);
    },
    
    // Check if first-time user and show welcome dialog
    checkFirstTimeUser: function() {
        // First visit if no tour has been completed
        const isFirstVisit = !Object.keys(tourConfig).some(tourName => 
            tourPreferences.isTourCompleted(tourName)
        );
        
        if (isFirstVisit) {
            this.showWelcomeDialog();
        }
    },
    
    // Show welcome dialog for first-time users
    showWelcomeDialog: function() {
        // Create modal for welcome dialog
        const welcomeModal = document.createElement('div');
        welcomeModal.classList.add('modal', 'fade');
        welcomeModal.id = 'welcomeTourModal';
        welcomeModal.setAttribute('tabindex', '-1');
        welcomeModal.setAttribute('aria-hidden', 'true');
        
        welcomeModal.innerHTML = `
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
                                <input class="form-check-input tour-option" type="checkbox" id="tourCheck3" value="dataImportTour">
                                <label class="form-check-label" for="tourCheck3">
                                    Data Import/Export Basics
                                </label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input tour-option" type="checkbox" id="tourCheck4" value="calculatorTour">
                                <label class="form-check-label" for="tourCheck4">
                                    Levy Calculator Introduction
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
        
        document.body.appendChild(welcomeModal);
        
        // Show the modal
        const modal = new bootstrap.Modal(welcomeModal);
        modal.show();
        
        // Setup event listener for starting tours
        document.getElementById('startSelectedTours').addEventListener('click', () => {
            // Get selected tours
            const selectedTours = Array.from(
                document.querySelectorAll('.tour-option:checked')
            ).map(checkbox => checkbox.value);
            
            // Hide the modal
            modal.hide();
            
            // Start the first tour if any selected
            if (selectedTours.length > 0) {
                this.startTour(selectedTours[0]);
                
                // Save the remaining tours for later
                if (selectedTours.length > 1) {
                    localStorage.setItem('pendingTours', JSON.stringify(selectedTours.slice(1)));
                }
            }
        });
    },
    
    // Setup event listeners for tour buttons
    setupEventListeners: function() {
        // Welcome tour button
        document.getElementById('start-welcome-tour')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.startTour('welcomeTour');
        });
        
        // Dashboard tour button
        document.getElementById('start-dashboard-tour')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.startTour('dashboardTour');
        });
        
        // Calculator tour button
        document.getElementById('start-calculator-tour')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.startTour('calculatorTour');
        });
        
        // Data import tour button
        document.getElementById('start-import-tour')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.startTour('dataImportTour');
        });
        
        // Reset all tours button
        document.getElementById('reset-all-tours')?.addEventListener('click', (e) => {
            e.preventDefault();
            tourPreferences.resetAllTours();
            alert('All tour progress has been reset. Tours will now appear as new.');
        });
    },
    
    // Start a specific tour
    startTour: function(tourName) {
        // Make sure the requested tour exists
        if (!tourConfig[tourName]) {
            console.error(`Tour "${tourName}" not found in configuration`);
            return;
        }
        
        // Create and configure the tour
        this.currentTour = introJs();
        
        // Configure the tour options
        this.currentTour.setOptions({
            steps: tourConfig[tourName],
            showStepNumbers: false,
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
            scrollToElement: true
        });
        
        // Handle tour complete
        this.currentTour.oncomplete(() => {
            tourPreferences.markTourComplete(tourName);
            this.checkPendingTours();
        });
        
        // Handle tour exit
        this.currentTour.onexit(() => {
            this.currentTour = null;
        });
        
        // Start the tour
        this.currentTour.start();
    },
    
    // Check for pending tours to run after current tour completes
    checkPendingTours: function() {
        const pendingToursString = localStorage.getItem('pendingTours');
        
        if (pendingToursString) {
            const pendingTours = JSON.parse(pendingToursString);
            
            if (pendingTours.length > 0) {
                // Remove the next tour from the list
                const nextTour = pendingTours.shift();
                
                // Update the pending tours in storage
                localStorage.setItem('pendingTours', JSON.stringify(pendingTours));
                
                // Start the next tour after a short delay
                setTimeout(() => {
                    this.startTour(nextTour);
                }, 500);
            } else {
                // No more tours, remove the item
                localStorage.removeItem('pendingTours');
            }
        }
    },
    
    // Get the current page context to determine relevant tours
    getPageContext: function() {
        const path = window.location.pathname;
        
        if (path.includes('/dashboard')) {
            return 'dashboard';
        } else if (path.includes('/levy-calculator')) {
            return 'calculator';
        } else if (path.includes('/data/import')) {
            return 'import';
        }
        
        return 'general';
    },
    
    // Show context-specific tour based on current page
    showContextTour: function() {
        const context = this.getPageContext();
        
        switch (context) {
            case 'dashboard':
                if (!tourPreferences.isTourCompleted('dashboardTour')) {
                    this.startTour('dashboardTour');
                }
                break;
                
            case 'calculator':
                if (!tourPreferences.isTourCompleted('calculatorTour')) {
                    this.startTour('calculatorTour');
                }
                break;
                
            case 'import':
                if (!tourPreferences.isTourCompleted('dataImportTour')) {
                    this.startTour('dataImportTour');
                }
                break;
        }
    }
};

// Initialize the tour system when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Wait a moment to ensure all page elements are properly rendered
    setTimeout(() => {
        TourController.init();
        
        // Check if we should show a context-specific tour
        TourController.showContextTour();
    }, 1000);
});