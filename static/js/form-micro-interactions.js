/**
 * Form Micro-Interactions
 *
 * This JavaScript file enhances form elements with subtle animations and
 * interactive feedback to improve the user experience.
 *
 * Features:
 * - Real-time validation with visual feedback
 * - Animated form labels
 * - Button loading states
 * - Enhanced file inputs
 * - Improved checkbox and radio interactions
 */

document.addEventListener("DOMContentLoaded", function () {
  // Initialize all form enhancements
  initFormValidation();
  initFileInputs();
  initLoadingButtons();
  initRangeSliders();
  initFormFloatingLabels();
  initCheckboxRadioAnimations();
});

/**
 * Initialize form validation with animated feedback
 */
function initFormValidation() {
  // Get all forms that need validation
  const forms = document.querySelectorAll(".needs-validation");

  // Apply custom validation styles and animations
  Array.from(forms).forEach((form) => {
    // Add validation class when form is submitted
    form.addEventListener(
      "submit",
      function (event) {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();

          // Find the first invalid input and focus it
          const firstInvalid = form.querySelector(":invalid");
          if (firstInvalid) {
            firstInvalid.focus();

            // Add shake animation class
            firstInvalid.classList.add("animate-shake");

            // Remove animation class after it completes
            setTimeout(() => {
              firstInvalid.classList.remove("animate-shake");
            }, 500);
          }
        }

        form.classList.add("was-validated");
      },
      false,
    );

    // Add real-time validation for individual fields
    form.querySelectorAll("input, select, textarea").forEach((input) => {
      input.addEventListener("blur", function () {
        // Skip validation if the field hasn't been interacted with
        if (!this.classList.contains("dirty")) return;

        validateField(this);
      });

      input.addEventListener("input", function () {
        // Mark the field as dirty once user starts typing
        this.classList.add("dirty");

        // Validate after a short delay for better UX
        clearTimeout(this.validateTimeout);
        this.validateTimeout = setTimeout(() => {
          validateField(this);
        }, 300);
      });
    });
  });
}

/**
 * Validate an individual form field with animated feedback
 */
function validateField(field) {
  // Check validity
  const isValid = field.checkValidity();

  // Clear existing classes
  field.classList.remove("is-valid", "is-invalid");

  // Skip empty non-required fields
  if (field.value === "" && !field.hasAttribute("required")) {
    return;
  }

  // Add appropriate validation class
  if (isValid) {
    field.classList.add("is-valid");
  } else {
    field.classList.add("is-invalid");
  }
}

/**
 * Enhanced file input with visual feedback
 */
function initFileInputs() {
  const fileInputs = document.querySelectorAll('input[type="file"]');

  fileInputs.forEach((input) => {
    // Create visual indicator for selected files
    const fileIndicator = document.createElement("div");
    fileIndicator.className = "file-upload-indicator small text-muted mt-1";
    fileIndicator.innerHTML =
      '<i class="bi bi-check-circle-fill text-success me-1"></i><span class="file-name"></span>';

    // Insert indicator after the file input
    if (
      input.nextElementSibling &&
      input.nextElementSibling.classList.contains("form-text")
    ) {
      input.nextElementSibling.before(fileIndicator);
    } else {
      input.after(fileIndicator);
    }

    // Update indicator when files are selected
    input.addEventListener("change", function () {
      const fileNameSpan = fileIndicator.querySelector(".file-name");

      if (this.files && this.files.length > 0) {
        // Show selected file name(s)
        if (this.files.length === 1) {
          fileNameSpan.textContent = this.files[0].name;
        } else {
          fileNameSpan.textContent = `${this.files.length} files selected`;
        }

        // Apply animation
        fileIndicator.style.display = "block";
        fileIndicator.style.animation = "fade-in 0.3s ease-in-out";
      } else {
        // Hide indicator if no file is selected
        fileIndicator.style.display = "none";
      }
    });
  });
}

/**
 * Add loading state to buttons
 */
function initLoadingButtons() {
  const loadingButtons = document.querySelectorAll(".loading-button");

  loadingButtons.forEach((buttonWrapper) => {
    const button = buttonWrapper.querySelector("button");

    if (!button) return;

    // Create spinner container
    const spinnerContainer = document.createElement("div");
    spinnerContainer.className = "spinner-container";
    spinnerContainer.innerHTML =
      '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';

    // Wrap button text in a span for easier toggling
    const buttonText = button.innerHTML;
    button.innerHTML = `<span class="btn-label">${buttonText}</span>`;
    button.appendChild(spinnerContainer);

    // Add spinner and disable button when parent form is submitted
    const parentForm = button.closest("form");
    if (parentForm) {
      parentForm.addEventListener("submit", function (event) {
        // Don't add loading state for invalid forms
        if (!parentForm.checkValidity()) return;

        buttonWrapper.classList.add("is-loading");
        button.disabled = true;
      });
    }
  });
}

/**
 * Enhanced range sliders with visual feedback
 */
function initRangeSliders() {
  const rangeSliders = document.querySelectorAll('input[type="range"]');

  rangeSliders.forEach((slider) => {
    // Find or create value display element
    let valueDisplay = document.getElementById(slider.dataset.valueDisplay);

    if (!valueDisplay && slider.id) {
      // Look for an element with id matching slider-value-{sliderId}
      valueDisplay = document.getElementById(`${slider.id}-value`);
    }

    if (valueDisplay) {
      // Update value display when slider changes
      const updateValue = () => {
        let displayValue = slider.value;

        // Format value if needed
        if (slider.dataset.valuePrefix) {
          displayValue = slider.dataset.valuePrefix + displayValue;
        }
        if (slider.dataset.valueSuffix) {
          displayValue = displayValue + slider.dataset.valueSuffix;
        }

        valueDisplay.textContent = displayValue;

        // Add visual pulse effect
        valueDisplay.classList.add("pulse-animation");
        setTimeout(() => {
          valueDisplay.classList.remove("pulse-animation");
        }, 300);
      };

      // Set initial value
      updateValue();

      // Add event listeners for immediate feedback
      slider.addEventListener("input", updateValue);
      slider.addEventListener("change", updateValue);
    }
  });
}

/**
 * Add subtle animations to floating labels
 */
function initFormFloatingLabels() {
  // Check for non-Bootstrap floating labels
  const customFloatingFields = document.querySelectorAll(
    ".custom-floating-label",
  );

  customFloatingFields.forEach((field) => {
    const input = field.querySelector("input, textarea, select");
    const label = field.querySelector("label");

    if (!input || !label) return;

    // Move label up if input already has value
    if (input.value !== "") {
      field.classList.add("has-value");
    }

    // Add event listeners
    input.addEventListener("focus", () => {
      field.classList.add("is-focused");
    });

    input.addEventListener("blur", () => {
      field.classList.remove("is-focused");
      if (input.value !== "") {
        field.classList.add("has-value");
      } else {
        field.classList.remove("has-value");
      }
    });

    input.addEventListener("input", () => {
      if (input.value !== "") {
        field.classList.add("has-value");
      } else {
        field.classList.remove("has-value");
      }
    });
  });
}

/**
 * Add animations to checkboxes and radio buttons
 */
function initCheckboxRadioAnimations() {
  const checkboxes = document.querySelectorAll(
    '.form-check-input[type="checkbox"]',
  );
  const radios = document.querySelectorAll('.form-check-input[type="radio"]');

  // Add ripple effect to checkboxes
  checkboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", function () {
      // Add animation class
      this.classList.add("animate-pulse");

      // Remove class after animation completes
      setTimeout(() => {
        this.classList.remove("animate-pulse");
      }, 300);
    });
  });

  // Add ripple effect to radio buttons
  radios.forEach((radio) => {
    radio.addEventListener("change", function () {
      // Reset all radios in the same group
      document
        .querySelectorAll(`input[type="radio"][name="${this.name}"]`)
        .forEach((r) => {
          r.classList.remove("animate-pulse");
        });

      // Add animation class to the selected radio
      this.classList.add("animate-pulse");

      // Remove class after animation completes
      setTimeout(() => {
        this.classList.remove("animate-pulse");
      }, 300);
    });
  });
}

// Utility functions
// -----------------

/**
 * Add ripple effect to an element on click
 */
function addRippleEffect(element) {
  element.addEventListener("mousedown", function (e) {
    const rect = element.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const ripple = document.createElement("span");
    ripple.className = "ripple-effect";
    ripple.style.left = `${x}px`;
    ripple.style.top = `${y}px`;

    this.appendChild(ripple);

    setTimeout(() => {
      ripple.remove();
    }, 600);
  });
}

/**
 * Animate an element with a temporary class
 */
function animateElement(element, animationClass, duration = 300) {
  element.classList.add(animationClass);
  setTimeout(() => {
    element.classList.remove(animationClass);
  }, duration);
}

// Define CSS keyframes animations if not already in the CSS
if (!document.getElementById("micro-interactions-keyframes")) {
  const styleSheet = document.createElement("style");
  styleSheet.id = "micro-interactions-keyframes";
  styleSheet.textContent = `
        @keyframes animate-pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        
        @keyframes animate-shake {
            0% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            50% { transform: translateX(5px); }
            75% { transform: translateX(-5px); }
            100% { transform: translateX(0); }
        }
        
        @keyframes fade-in {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .animate-pulse {
            animation: animate-pulse 0.3s ease-in-out;
        }
        
        .animate-shake {
            animation: animate-shake 0.4s ease-in-out;
        }
        
        .pulse-animation {
            animation: animate-pulse 0.3s ease-in-out;
        }
        
        .ripple-effect {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.4);
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
        }
        
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
  document.head.appendChild(styleSheet);
}
