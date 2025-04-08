/**
 * Animations Aggregator
 * 
 * This file imports and initializes all animation modules in the application.
 * It serves as a central entry point for animation-related functionality.
 */

document.addEventListener('DOMContentLoaded', function() {
  console.log('Animation aggregator initialized');
  
  // Load the tax-themed loading animations script
  loadScript('/static/js/animations/loading-animations.js', function() {
    console.log('Loading animations loaded successfully');
  });
});

/**
 * Dynamically load a script
 * 
 * @param {string} src - The source URL of the script to load
 * @param {Function} callback - Function to call when script is loaded
 */
function loadScript(src, callback) {
  const script = document.createElement('script');
  script.src = src;
  script.onload = callback;
  script.onerror = function() {
    console.error('Error loading script:', src);
  };
  document.head.appendChild(script);
}