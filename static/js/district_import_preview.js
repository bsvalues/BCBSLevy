/**
 * District Import Preview functionality
 *
 * This script handles the animated preview functionality for district data imports,
 * showing the data that will be imported before committing it to the database.
 * Enhanced with micro-interactions for improved user experience.
 */

document.addEventListener("DOMContentLoaded", function () {
  const previewForm = document.getElementById("district-preview-form");
  const importForm = document.getElementById("district-import-form");
  const previewContainer = document.getElementById("preview-container");
  const previewResults = document.getElementById("preview-results");
  const previewLoader = document.getElementById("preview-loader");
  const previewError = document.getElementById("preview-error");
  const confirmImportBtn = document.getElementById("confirm-import");
  const cancelPreviewBtn = document.getElementById("cancel-preview");
  const fileInput = document.getElementById("preview-file");

  // Skip if we're not on the district import page
  if (!previewForm) return;

  // Initialize form validations and micro-interactions
  initFormValidation();
  initFileInput(fileInput);

  previewForm.addEventListener("submit", function (e) {
    e.preventDefault();

    // Check form validity first
    if (!previewForm.checkValidity()) {
      e.stopPropagation();
      previewForm.classList.add("was-validated");

      // Show shake animation on invalid fields
      const invalidField = previewForm.querySelector(":invalid");
      if (invalidField) {
        invalidField.classList.add("animate-shake");
        setTimeout(() => invalidField.classList.remove("animate-shake"), 500);
      }
      return;
    }

    previewForm.classList.add("was-validated");

    // Show loader and hide previous results
    previewLoader.classList.remove("d-none");
    previewError.classList.add("d-none");
    previewResults.classList.add("d-none");
    previewContainer.classList.remove("d-none");

    // Add loading state to button
    const submitButton = previewForm.querySelector('button[type="submit"]');
    const loadingButton =
      submitButton.closest(".loading-button") || submitButton;

    if (loadingButton.classList.contains("loading-button")) {
      loadingButton.classList.add("is-loading");
    }
    submitButton.disabled = true;

    // Get form data
    const formData = new FormData(previewForm);

    // Send AJAX request to preview endpoint
    fetch("/data/api/preview-district-import", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        // Hide loader
        previewLoader.classList.add("d-none");

        // Restore button state
        if (loadingButton.classList.contains("loading-button")) {
          loadingButton.classList.remove("is-loading");
        }
        submitButton.disabled = false;

        if (data.success) {
          // Show success results with animation
          previewResults.classList.remove("d-none");
          previewResults.style.animation = "fade-in 0.3s ease-in-out";

          // Populate preview table
          const previewTable = document.getElementById("preview-table");
          const tbody = previewTable.querySelector("tbody");
          tbody.innerHTML = "";

          // Create header based on first district's fields
          const thead = previewTable.querySelector("thead");
          const headerRow = thead.querySelector("tr");
          headerRow.innerHTML = "";

          if (data.districts && data.districts.length > 0) {
            // Extract columns from the first district
            const columns = Object.keys(data.districts[0]);

            // Create header row
            columns.forEach((column) => {
              const th = document.createElement("th");
              th.textContent = column
                .replace(/_/g, " ")
                .replace(/\b\w/g, (l) => l.toUpperCase()); // Capitalize words
              headerRow.appendChild(th);
            });

            // Add rows with animation delay
            data.districts.forEach((district, index) => {
              const row = document.createElement("tr");
              row.style.opacity = 0;
              row.style.transform = "translateY(20px)";
              row.style.transition = "opacity 0.3s ease, transform 0.3s ease";
              row.style.transitionDelay = `${index * 0.1}s`;

              columns.forEach((column) => {
                const td = document.createElement("td");

                // Format the value based on column type
                if (column === "levy_rate" && district[column] !== null) {
                  td.textContent = district[column]
                    ? `${district[column].toFixed(4)}%`
                    : "";
                } else if (
                  column === "levy_amount" &&
                  district[column] !== null
                ) {
                  td.textContent = district[column]
                    ? `$${district[column].toLocaleString()}`
                    : "";
                } else {
                  td.textContent =
                    district[column] !== null ? district[column] : "";
                }

                row.appendChild(td);
              });

              tbody.appendChild(row);

              // Trigger animation after a short delay
              setTimeout(() => {
                row.style.opacity = 1;
                row.style.transform = "translateY(0)";
              }, 50);
            });

            // Update summary with animation
            const countElements = document.querySelectorAll(
              "#preview-count, #preview-sample-count",
            );
            countElements.forEach((element) => {
              element.style.transition = "color 0.3s ease";
              element.style.color = "#0d6efd";
              element.textContent =
                element.id === "preview-count"
                  ? data.total_count
                  : data.sample_count;

              setTimeout(() => {
                element.style.color = "";
              }, 1000);
            });

            // Show confirmation buttons with animation
            confirmImportBtn.classList.remove("d-none");
            cancelPreviewBtn.classList.remove("d-none");

            // Add subtle entrance animation
            confirmImportBtn.style.animation = "fade-in 0.5s ease-in-out";
            cancelPreviewBtn.style.animation = "fade-in 0.5s ease-in-out";

            // Prepare import form data
            const fileInput = previewForm.querySelector('input[type="file"]');
            const yearInput = previewForm.querySelector('select[name="year"]');

            // Update hidden fields in the import form
            const importFileInput = document.getElementById("import-file-data");
            const importYearInput = document.getElementById("import-year");

            // We can't transfer the file directly, so we'll submit both forms
            importYearInput.value = yearInput.value;

            // Set up confirm button to trigger the actual import
            confirmImportBtn.addEventListener("click", function () {
              // Show loading state
              const importButtonWrapper =
                confirmImportBtn.closest(".loading-button");
              if (importButtonWrapper) {
                importButtonWrapper.classList.add("is-loading");
              }
              confirmImportBtn.disabled = true;

              // Clone the file input to the import form
              const originalFile = fileInput.files[0];
              const dataTransfer = new DataTransfer();
              dataTransfer.items.add(originalFile);

              const importFormFileInput =
                document.getElementById("import-file");
              importFormFileInput.files = dataTransfer.files;

              // Submit the import form
              importForm.submit();
            });
          } else {
            // No districts found - show error with animation
            previewError.textContent =
              "No valid district data found in the file";
            previewError.classList.remove("d-none");
            previewError.style.animation = "fade-in 0.3s ease-in-out";
            previewResults.classList.add("d-none");
          }
        } else {
          // Show error with shake animation
          previewError.textContent =
            data.message || "Failed to preview district data";
          previewError.classList.remove("d-none");
          previewError.style.animation = "animate-shake 0.4s ease-in-out";
          previewResults.classList.add("d-none");
        }
      })
      .catch((error) => {
        // Hide loader and show error
        previewLoader.classList.add("d-none");

        // Restore button state
        if (loadingButton.classList.contains("loading-button")) {
          loadingButton.classList.remove("is-loading");
        }
        submitButton.disabled = false;

        // Show error with animation
        previewError.textContent =
          error.message || "An unexpected error occurred";
        previewError.classList.remove("d-none");
        previewError.style.animation = "animate-shake 0.4s ease-in-out";
        previewResults.classList.add("d-none");
      });
  });

  // Cancel preview button event with animation
  if (cancelPreviewBtn) {
    cancelPreviewBtn.addEventListener("click", function () {
      previewContainer.style.animation = "fade-out 0.3s ease-in-out";

      setTimeout(() => {
        previewContainer.classList.add("d-none");
        previewContainer.style.animation = "";
      }, 300);
    });
  }

  // Helper functions for micro-interactions
  function initFormValidation() {
    // Add validation styles on input change
    const inputs = previewForm.querySelectorAll("input, select");
    inputs.forEach((input) => {
      input.addEventListener("change", function () {
        validateField(this);
      });

      input.addEventListener("input", function () {
        // Add a debounce for better performance
        clearTimeout(this.validateTimeout);
        this.validateTimeout = setTimeout(() => {
          validateField(this);
        }, 300);
      });
    });
  }

  function validateField(field) {
    // Skip validation if the field hasn't been "touched"
    if (!field.classList.contains("dirty")) return;

    // Check validity
    if (field.checkValidity()) {
      field.classList.remove("is-invalid");
      field.classList.add("is-valid");
    } else {
      field.classList.remove("is-valid");
      field.classList.add("is-invalid");
    }
  }

  function initFileInput(input) {
    if (!input) return;

    // Mark as touched when selected
    input.addEventListener("change", function () {
      this.classList.add("dirty");

      // Show file name feedback
      const fileNameEl = input
        .closest(".custom-file-container")
        ?.querySelector(".file-name");
      if (fileNameEl && this.files && this.files.length > 0) {
        const fileName = this.files[0].name;
        fileNameEl.textContent = fileName;

        const container = input
          .closest(".custom-file-container")
          ?.querySelector(".file-upload-indicator");
        if (container) {
          container.style.display = "inline-block";
          container.style.animation = "fade-in 0.3s ease-in-out";
        }

        // Validate after file selected
        validateField(this);
      }
    });
  }
});

// Define CSS keyframes for animations if needed
if (!document.getElementById("district-import-keyframes")) {
  const styleSheet = document.createElement("style");
  styleSheet.id = "district-import-keyframes";
  styleSheet.textContent = `
        @keyframes fade-in {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes fade-out {
            from { opacity: 1; transform: translateY(0); }
            to { opacity: 0; transform: translateY(-10px); }
        }
        
        @keyframes animate-shake {
            0% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            50% { transform: translateX(5px); }
            75% { transform: translateX(-5px); }
            100% { transform: translateX(0); }
        }
    `;
  document.head.appendChild(styleSheet);
}
