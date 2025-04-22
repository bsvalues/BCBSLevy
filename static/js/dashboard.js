// Dashboard.js - Client-side JavaScript for the dashboard

document.addEventListener("DOMContentLoaded", function () {
  // Initialize any interactive elements
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]'),
  );
  const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Handle file upload form
  const fileUploadForm = document.getElementById("fileUploadForm");
  if (fileUploadForm) {
    fileUploadForm.addEventListener("submit", function () {
      const submitBtn = document.getElementById("uploadSubmitBtn");
      const spinner = document.getElementById("uploadSpinner");

      if (submitBtn && spinner) {
        submitBtn.disabled = true;
        spinner.classList.remove("d-none");
      }
    });
  }

  // Handle file input change to display selected filename
  const fileInput = document.getElementById("csvFileInput");
  const fileLabel = document.getElementById("csvFileLabel");

  if (fileInput && fileLabel) {
    fileInput.addEventListener("change", function () {
      if (fileInput.files.length > 0) {
        fileLabel.textContent = fileInput.files[0].name;
      } else {
        fileLabel.textContent = "Choose CSV file...";
      }
    });
  }

  // Load chart data if charts container exists
  const chartsContainer = document.getElementById("chartsContainer");
  if (chartsContainer) {
    fetch("/api/tax-codes")
      .then((response) => response.json())
      .then((data) => {
        initializeCharts(data.data);
      })
      .catch((error) => {
        console.error("Error fetching chart data:", error);
      });
  }
});
