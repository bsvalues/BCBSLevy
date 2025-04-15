/**
 * guided_tour.js
 * 
 * This module provides functionality for the guided tour feature using IntroJS.
 * It works with help_menu.js to provide contextual guided tours for different
 * sections of the application.
 */

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log("Initializing guided tour...");
    setupTourButtons();
    console.log("Guided tour initialized");
});

/**
 * Set up event listeners for tour-related buttons
 */
function setupTourButtons() {
    // Set up contact support functionality
    setupContactButtons();
    
    // Set up tour buttons in the navigation and help menu
    const tourButtons = document.querySelectorAll('[data-tour]');
    tourButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tourName = this.getAttribute('data-tour');
            if (typeof startTour === 'function') {
                startTour(tourName);
            } else if (typeof window.startTour === 'function') {
                window.startTour(tourName);
            } else {
                console.error('Tour function not found');
            }
        });
    });
}

/**
 * Set up event listeners for contact support buttons
 */
function setupContactButtons() {
    // Contact support button in help menu
    const contactSupportBtn = document.getElementById('contactSupportBtn');
    if (contactSupportBtn) {
        contactSupportBtn.addEventListener('click', function() {
            // Close help menu first
            const helpMenu = document.getElementById('helpMenu');
            if (helpMenu && helpMenu.classList.contains('active')) {
                toggleHelpMenu(false);
            }
            
            // Redirect to contact page or show contact form
            window.location.href = '/contact';
        });
    }
}