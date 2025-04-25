/**
 * TerraLevy Utilities JavaScript
 * Common utility functions for the TerraLevy application
 */

// Utility function namespace
const TLUtils = {
  /**
   * Format a number as currency with proper formatting
   * @param {Number} value - The number to format
   * @param {String} currency - Currency code (default: USD)
   * @param {String} locale - Locale for formatting (default: en-US)
   * @returns {String} Formatted currency string
   */
  formatCurrency: function(value, currency = 'USD', locale = 'en-US') {
    if (value === null || value === undefined || isNaN(value)) {
      return '--';
    }
    
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  },
  
  /**
   * Format a number as percentage
   * @param {Number} value - The number to format (e.g., 0.15 for 15%)
   * @param {Number} decimalPlaces - Number of decimal places to display
   * @param {String} locale - Locale for formatting (default: en-US)
   * @returns {String} Formatted percentage string
   */
  formatPercent: function(value, decimalPlaces = 2, locale = 'en-US') {
    if (value === null || value === undefined || isNaN(value)) {
      return '--';
    }
    
    return new Intl.NumberFormat(locale, {
      style: 'percent',
      minimumFractionDigits: decimalPlaces,
      maximumFractionDigits: decimalPlaces
    }).format(value);
  },
  
  /**
   * Format a number with thousands separators
   * @param {Number} value - The number to format
   * @param {Number} decimalPlaces - Number of decimal places to display
   * @param {String} locale - Locale for formatting (default: en-US)
   * @returns {String} Formatted number string
   */
  formatNumber: function(value, decimalPlaces = 0, locale = 'en-US') {
    if (value === null || value === undefined || isNaN(value)) {
      return '--';
    }
    
    return new Intl.NumberFormat(locale, {
      minimumFractionDigits: decimalPlaces,
      maximumFractionDigits: decimalPlaces
    }).format(value);
  },
  
  /**
   * Format a date in a consistent manner
   * @param {Date|String} date - Date object or date string
   * @param {String} format - Format specifier (short, medium, long, full)
   * @param {String} locale - Locale for formatting (default: en-US)
   * @returns {String} Formatted date string
   */
  formatDate: function(date, format = 'short', locale = 'en-US') {
    if (!date) {
      return '--';
    }
    
    try {
      const dateObj = date instanceof Date ? date : new Date(date);
      
      if (isNaN(dateObj.getTime())) {
        return 'Invalid date';
      }
      
      let options = { year: 'numeric', month: 'numeric', day: 'numeric' };
      
      switch (format) {
        case 'medium':
          options = { year: 'numeric', month: 'short', day: 'numeric' };
          break;
        case 'long':
          options = { year: 'numeric', month: 'long', day: 'numeric' };
          break;
        case 'full':
          options = { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          };
          break;
      }
      
      return new Intl.DateTimeFormat(locale, options).format(dateObj);
    } catch (e) {
      console.error('Error formatting date:', e);
      return 'Error';
    }
  },
  
  /**
   * Calculate the difference between two values
   * @param {Number} current - Current value
   * @param {Number} previous - Previous value
   * @param {Boolean} asPercent - Return as percentage (default: true)
   * @returns {Number|String} Difference or percentage difference
   */
  calculateDifference: function(current, previous, asPercent = true) {
    if (current === null || previous === null || 
        current === undefined || previous === undefined ||
        isNaN(current) || isNaN(previous)) {
      return null;
    }
    
    const difference = current - previous;
    
    if (asPercent) {
      // Avoid division by zero
      if (previous === 0) {
        return current === 0 ? 0 : Infinity;
      }
      
      return difference / Math.abs(previous);
    }
    
    return difference;
  },
  
  /**
   * Debounce function to limit how often a function can be called
   * @param {Function} func - Function to debounce
   * @param {Number} wait - Milliseconds to wait
   * @param {Boolean} immediate - Execute immediately
   * @returns {Function} Debounced function
   */
  debounce: function(func, wait = 300, immediate = false) {
    let timeout;
    
    return function() {
      const context = this;
      const args = arguments;
      
      const later = function() {
        timeout = null;
        if (!immediate) func.apply(context, args);
      };
      
      const callNow = immediate && !timeout;
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
      
      if (callNow) func.apply(context, args);
    };
  },
  
  /**
   * Throttle function to limit how often a function can be called
   * @param {Function} func - Function to throttle
   * @param {Number} limit - Milliseconds to wait between executions
   * @returns {Function} Throttled function
   */
  throttle: function(func, limit = 300) {
    let inThrottle;
    
    return function() {
      const args = arguments;
      const context = this;
      
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  },
  
  /**
   * Get query parameters from URL
   * @param {String} param - Parameter name to get (optional)
   * @returns {Object|String} All parameters as object or specific parameter value
   */
  getQueryParams: function(param) {
    const urlSearchParams = new URLSearchParams(window.location.search);
    const params = Object.fromEntries(urlSearchParams.entries());
    
    if (param) {
      return params[param] || null;
    }
    
    return params;
  },
  
  /**
   * Safely get a nested property from an object without errors
   * @param {Object} obj - Object to get property from
   * @param {String} path - Dot notation path to property
   * @param {*} defaultValue - Default value if property doesn't exist
   * @returns {*} Property value or default value
   */
  getNestedProperty: function(obj, path, defaultValue = null) {
    if (!obj || !path) {
      return defaultValue;
    }
    
    const properties = path.split('.');
    let current = obj;
    
    for (let i = 0; i < properties.length; i++) {
      if (current === null || current === undefined || typeof current !== 'object') {
        return defaultValue;
      }
      
      current = current[properties[i]];
    }
    
    return current !== undefined ? current : defaultValue;
  },
  
  /**
   * Check if a value is empty (null, undefined, empty string, empty array, empty object)
   * @param {*} value - Value to check
   * @returns {Boolean} True if empty, false otherwise
   */
  isEmpty: function(value) {
    if (value === null || value === undefined) {
      return true;
    }
    
    if (typeof value === 'string' && value.trim() === '') {
      return true;
    }
    
    if (Array.isArray(value) && value.length === 0) {
      return true;
    }
    
    if (typeof value === 'object' && Object.keys(value).length === 0) {
      return true;
    }
    
    return false;
  },
  
  /**
   * Generate a random ID
   * @param {Number} length - Length of ID (default: 8)
   * @returns {String} Random ID
   */
  generateId: function(length = 8) {
    const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let result = '';
    
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    
    return result;
  },
  
  /**
   * Add commas as thousands separators
   * @param {Number|String} value - Value to format
   * @returns {String} Formatted value with commas
   */
  addCommas: function(value) {
    if (value === null || value === undefined || value === '') {
      return '--';
    }
    
    // Convert to string and handle decimal part separately
    const parts = String(value).split('.');
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    
    return parts.join('.');
  },
  
  /**
   * Calculate the levy rate based on levy amount and assessed value
   * @param {Number} levyAmount - The levy amount
   * @param {Number} assessedValue - The assessed value
   * @returns {Number} The calculated levy rate
   */
  calculateLevyRate: function(levyAmount, assessedValue) {
    if (!levyAmount || !assessedValue || assessedValue === 0) {
      return 0;
    }
    
    // Rate is typically per $1,000 of assessed value
    return (levyAmount / assessedValue) * 1000;
  },
  
  /**
   * Calculate levy amount based on rate and assessed value
   * @param {Number} levyRate - The levy rate
   * @param {Number} assessedValue - The assessed value
   * @returns {Number} The calculated levy amount
   */
  calculateLevyAmount: function(levyRate, assessedValue) {
    if (!levyRate || !assessedValue) {
      return 0;
    }
    
    // Rate is typically per $1,000 of assessed value
    return (levyRate * assessedValue) / 1000;
  },
  
  /**
   * Calculate the statutory maximum levy based on previous levy amount and limit factor
   * @param {Number} previousLevyAmount - Previous year levy amount
   * @param {Number} limitFactor - Limit factor (e.g., 1.01 for 1% increase)
   * @param {Number} newConstructionValue - Value of new construction
   * @param {Number} annexationValue - Value of annexation
   * @returns {Number} Maximum statutory levy amount
   */
  calculateMaximumLevy: function(previousLevyAmount, limitFactor, newConstructionValue = 0, annexationValue = 0) {
    if (!previousLevyAmount || !limitFactor) {
      return 0;
    }
    
    // Calculate base limit
    let maxLevy = previousLevyAmount * limitFactor;
    
    // Add new construction and annexation values if provided
    if (newConstructionValue) {
      // Calculate the previous levy rate to apply to new construction
      const impliedRate = previousLevyAmount / (previousLevyAmount * 1000 / limitFactor);
      maxLevy += (newConstructionValue * impliedRate) / 1000;
    }
    
    if (annexationValue) {
      // Similar calculation for annexation value
      const impliedRate = previousLevyAmount / (previousLevyAmount * 1000 / limitFactor);
      maxLevy += (annexationValue * impliedRate) / 1000;
    }
    
    return maxLevy;
  },
  
  /**
   * Format a levy rate with proper decimal places
   * @param {Number} rate - The levy rate to format
   * @param {Number} decimalPlaces - Number of decimal places (default: 4)
   * @returns {String} Formatted levy rate
   */
  formatLevyRate: function(rate, decimalPlaces = 4) {
    if (rate === null || rate === undefined || isNaN(rate)) {
      return '--';
    }
    
    return rate.toFixed(decimalPlaces);
  }
};

// Make utilities available globally
window.TLUtils = TLUtils;