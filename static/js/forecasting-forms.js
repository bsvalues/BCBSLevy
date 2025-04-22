/**
 * Forecasting Forms Micro-Interactions
 *
 * This script enhances the forecasting forms with micro-interactions
 * to provide better feedback and a more responsive user experience.
 */

document.addEventListener("DOMContentLoaded", function () {
  // Initialize district forecast form interactions
  initDistrictForecastForm();

  // Initialize AI dashboard forecast form interactions
  initAiDashboardForm();

  // Initialize range slider value displays
  initRangeSliders();
});

/**
 * Initialize district forecast form with validation and animations
 */
function initDistrictForecastForm() {
  const form = document.getElementById("district-forecast-form");
  if (!form) return;

  // Add validation to the form
  form.addEventListener(
    "submit",
    function (event) {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();

        // Find first invalid input and focus it with animation
        const firstInvalid = form.querySelector(":invalid");
        if (firstInvalid) {
          firstInvalid.focus();
          animateElement(firstInvalid, "animate-shake");
        }
      } else {
        // If valid, show loading animation
        const button = this.querySelector('button[type="submit"]');
        const loadingButton = button.closest(".loading-button");

        if (loadingButton) {
          loadingButton.classList.add("is-loading");
        }

        button.disabled = true;
      }

      form.classList.add("was-validated");
    },
    false,
  );

  // Add real-time validation for fields
  const inputs = form.querySelectorAll("input, select");
  inputs.forEach((input) => {
    input.addEventListener("change", function () {
      validateField(this);
    });

    input.addEventListener("input", function () {
      // Mark as dirty (interacted with)
      this.classList.add("dirty");

      // Debounce validation for better performance
      clearTimeout(this.validateTimeout);
      this.validateTimeout = setTimeout(() => {
        validateField(this);
      }, 300);
    });
  });
}

/**
 * Initialize AI dashboard forecast form with validation and animations
 */
function initAiDashboardForm() {
  const form = document.getElementById("forecastForm");
  if (!form) return;

  // Add validation to the form
  form.addEventListener(
    "submit",
    function (event) {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();

        // Find first invalid input and focus it with animation
        const firstInvalid = form.querySelector(":invalid");
        if (firstInvalid) {
          firstInvalid.focus();
          animateElement(firstInvalid, "animate-shake");
        }
      } else {
        // Show loading animation
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
          submitButton.disabled = true;

          // Add spinner
          const spinner = document.createElement("span");
          spinner.className = "spinner-border spinner-border-sm me-2";
          spinner.setAttribute("role", "status");
          spinner.setAttribute("aria-hidden", "true");

          submitButton.prepend(spinner);

          // Store original text
          submitButton.dataset.originalText = submitButton.textContent;
          submitButton.textContent = " Analyzing...";
          submitButton.prepend(spinner);
        }
      }

      form.classList.add("was-validated");
    },
    false,
  );

  // Enhance the tax code select with animation
  const taxCodeSelect = form.querySelector("#taxCodeSelect");
  if (taxCodeSelect) {
    taxCodeSelect.addEventListener("change", function () {
      if (this.value) {
        animateElement(this, "pulse-animation");
      }
      validateField(this);
    });
  }
}

/**
 * Initialize range sliders with visual value display
 */
function initRangeSliders() {
  const rangeSliders = document.querySelectorAll('input[type="range"]');

  rangeSliders.forEach((slider) => {
    // Find value display element
    const valueDisplay = document.getElementById(`${slider.id}-value`);
    if (!valueDisplay) return;

    // Format value with suffix if provided
    const formatValue = (value) => {
      let result = value;
      if (slider.dataset.valuePrefix) {
        result = slider.dataset.valuePrefix + result;
      }
      if (slider.dataset.valueSuffix) {
        result = result + slider.dataset.valueSuffix;
      }
      return result;
    };

    // Set initial value
    valueDisplay.textContent = formatValue(slider.value);

    // Update value display when slider changes
    slider.addEventListener("input", function () {
      valueDisplay.textContent = formatValue(this.value);
      animateElement(valueDisplay, "pulse-animation");
    });
  });
}

/**
 * Validate an individual field with visual feedback
 */
function validateField(field) {
  // Skip if not marked as dirty yet
  if (!field.classList.contains("dirty")) return;

  // Check validity
  const isValid = field.checkValidity();

  // Update classes
  field.classList.remove("is-valid", "is-invalid");

  if (field.value !== "") {
    if (isValid) {
      field.classList.add("is-valid");
    } else {
      field.classList.add("is-invalid");
    }
  }
}

/**
 * Animate an element with a CSS class temporarily
 */
function animateElement(element, animationClass, duration = 400) {
  element.classList.add(animationClass);
  setTimeout(() => {
    element.classList.remove(animationClass);
  }, duration);
}
