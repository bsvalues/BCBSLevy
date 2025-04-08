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
    
    // Add a hidden helper button to force-clear loading overlays
    addClearLoadingButton();
    
    // Add keyboard shortcut (Ctrl+Alt+L) to clear loading overlays
    document.addEventListener('keydown', function(e) {
      if (e.ctrlKey && e.altKey && e.key === 'l') {
        console.log('Keyboard shortcut triggered: clearing loading overlays');
        if (typeof window.hideLevyLoadingAll === 'function') {
          window.hideLevyLoadingAll(true);
        }
      }
    });
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

/**
 * Add a hidden button to clear loading overlays
 * This is accessible via the keyboard shortcut or through the browser console
 */
function addClearLoadingButton() {
  const button = document.createElement('button');
  button.id = 'clear-loading-button';
  button.textContent = 'Clear Loading';
  button.style.position = 'fixed';
  button.style.bottom = '10px';
  button.style.right = '10px';
  button.style.zIndex = '99999';
  button.style.padding = '10px';
  button.style.backgroundColor = '#ff4c4c';
  button.style.color = 'white';
  button.style.border = 'none';
  button.style.borderRadius = '5px';
  button.style.cursor = 'pointer';
  button.style.display = 'none'; // Hidden by default
  
  button.addEventListener('click', function() {
    if (typeof window.hideLevyLoadingAll === 'function') {
      window.hideLevyLoadingAll(true);
    }
  });
  
  document.body.appendChild(button);
  
  // Expose function to show the button in case of emergency
  window.showClearLoadingButton = function() {
    document.getElementById('clear-loading-button').style.display = 'block';
  };
}