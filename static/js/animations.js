/**
 * animations.js
 * 
 * This module provides animations and visual effects for the LevyMaster application.
 * It handles fading effects, transitions, and other animation-related functionality.
 */

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log("Initializing animations...");
    initializeAnimations();
    console.log("Animations initialized");
});

/**
 * Initialize animation effects throughout the application
 */
function initializeAnimations() {
    // Add fade-in effect to dashboard cards
    animateDashboardCards();
    
    // Add hover effects to action buttons
    setupButtonHoverEffects();
    
    // Setup scroll animations
    setupScrollAnimations();
}

/**
 * Add fade-in animation to dashboard cards
 */
function animateDashboardCards() {
    const cards = document.querySelectorAll('.dashboard-card');
    if (cards.length > 0) {
        cards.forEach((card, index) => {
            // Add a staggered delay based on the index
            setTimeout(() => {
                card.classList.add('fade-in');
            }, 100 * index);
        });
    }
}

/**
 * Set up hover animations for buttons
 */
function setupButtonHoverEffects() {
    const actionButtons = document.querySelectorAll('.action-button, .btn-primary, .btn-success');
    if (actionButtons.length > 0) {
        actionButtons.forEach(button => {
            button.addEventListener('mouseover', function() {
                this.classList.add('button-hover');
            });
            
            button.addEventListener('mouseout', function() {
                this.classList.remove('button-hover');
            });
        });
    }
}

/**
 * Set up animations that trigger on scroll
 */
function setupScrollAnimations() {
    // Get all elements that should animate on scroll
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    
    if (animateElements.length > 0) {
        // Function to check if an element is in viewport
        function isInViewport(element) {
            const rect = element.getBoundingClientRect();
            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
            );
        }
        
        // Function to handle scroll events
        function handleScrollAnimations() {
            animateElements.forEach(element => {
                if (isInViewport(element) && !element.classList.contains('animated')) {
                    element.classList.add('animated');
                }
            });
        }
        
        // Add scroll event listener
        window.addEventListener('scroll', handleScrollAnimations);
        
        // Trigger once on load to animate elements already in viewport
        handleScrollAnimations();
    }
}