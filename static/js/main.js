/**
 * Web Scraper Application - Main JavaScript
 * 
 * This file contains the main JavaScript functions for the web scraper application.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add fade-in animation to content
    document.querySelectorAll('.card').forEach(card => {
        card.classList.add('fade-in');
    });
    
    // Show tooltip for URLs that are truncated
    const truncatedElements = document.querySelectorAll('.text-truncate');
    truncatedElements.forEach(el => {
        const originalText = el.textContent;
        if (el.offsetWidth < el.scrollWidth) {
            el.setAttribute('title', originalText);
        }
    });
    
    // Add loading state to forms when submitted
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...';
                submitBtn.disabled = true;
            }
        });
    });
    
    // Automatically fade out alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.classList.add('fade');
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.parentNode.removeChild(alert);
                    }
                }, 500);
            }
        }, 5000);
    });
});