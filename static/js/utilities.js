/**
 * Shared utility functions for the LevyMaster application.
 * 
 * This file contains utility functions that are used across multiple
 * JavaScript modules, particularly formatting functions and data transformations.
 */

/**
 * Format a number as currency with $ sign and commas
 * @param {number} value - The number to format
 * @returns {string} The formatted currency string
 */
function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

/**
 * Format a number as a rate with 4 decimal places
 * @param {number} value - The number to format
 * @returns {string} The formatted rate string
 */
function formatRate(value) {
  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 4,
    maximumFractionDigits: 4,
  }).format(value);
}

/**
 * Format a number with commas as thousands separators
 * @param {number} value - The number to format
 * @returns {string} The formatted number string
 */
function formatNumber(value) {
  return new Intl.NumberFormat("en-US").format(value);
}

/**
 * Format a number as a percentage
 * @param {number} value - The number to format (0.01 = 1%)
 * @returns {string} The formatted percentage string
 */
function formatPercent(value) {
  return new Intl.NumberFormat("en-US", {
    style: "percent",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}