/**
 * Historical data import/export preview functionality
 *
 * This module provides functionality for:
 * - Previewing historical data before export
 * - Previewing CSV data before import
 * - Downloading a CSV template for import
 */

/**
 * Historical data import/export preview functionality and tax code comparisons
 *
 * This module provides functionality for:
 * - Previewing historical data before export
 * - Previewing CSV data before import
 * - Downloading a CSV template for import
 * - Comparing multiple tax codes
 */

document.addEventListener("DOMContentLoaded", function () {
  // Export Preview Functionality
  const previewExportBtn = document.getElementById("previewExportBtn");
  if (previewExportBtn) {
    previewExportBtn.addEventListener("click", function () {
      // Get filter values
      const yearFilter = document.getElementById("export_year").value;
      const taxCodeFilter = document.getElementById("export_tax_code").value;

      // Build query string
      const queryParams = new URLSearchParams();
      if (yearFilter) queryParams.append("year", yearFilter);
      if (taxCodeFilter) queryParams.append("tax_code", taxCodeFilter);

      // Show the modal
      const exportPreviewModal = new bootstrap.Modal(
        document.getElementById("exportPreviewModal"),
      );
      exportPreviewModal.show();

      // Show loading state
      document
        .getElementById("exportPreviewLoading")
        .classList.remove("d-none");
      document.getElementById("exportPreviewContent").classList.add("d-none");
      document.getElementById("exportPreviewNoData").classList.add("d-none");

      // Fetch preview data
      fetch(`/api/historical_export_preview?${queryParams.toString()}`)
        .then((response) => response.json())
        .then((data) => {
          // Hide loading state
          document
            .getElementById("exportPreviewLoading")
            .classList.add("d-none");

          if (data.success && data.preview && data.preview.length > 0) {
            // Show preview content
            document
              .getElementById("exportPreviewContent")
              .classList.remove("d-none");

            // Populate the table
            const tbody = document.querySelector("#exportPreviewTable tbody");
            tbody.innerHTML = "";

            data.preview.forEach((row) => {
              const tr = document.createElement("tr");
              tr.innerHTML = `
                                <td>${row.tax_code}</td>
                                <td>${row.year}</td>
                                <td>${parseFloat(row.levy_rate).toFixed(4)}</td>
                                <td>${row.levy_amount ? parseFloat(row.levy_amount).toLocaleString() : "N/A"}</td>
                                <td>${row.total_assessed_value ? parseFloat(row.total_assessed_value).toLocaleString() : "N/A"}</td>
                            `;
              tbody.appendChild(tr);
            });

            // Set up confirm export button
            document.getElementById("confirmExportBtn").onclick = function () {
              const exportForm = document.querySelector(
                'form[name="export_form"]',
              );
              exportForm.querySelector(
                'input[name="export_historical_data"]',
              ).value = "true";
              exportForm.submit();
            };
          } else {
            // Show no data message
            document
              .getElementById("exportPreviewNoData")
              .classList.remove("d-none");
          }
        })
        .catch((error) => {
          console.error("Error fetching export preview:", error);
          document
            .getElementById("exportPreviewLoading")
            .classList.add("d-none");
          document
            .getElementById("exportPreviewNoData")
            .classList.remove("d-none");
          document.getElementById("exportPreviewNoData").textContent =
            "Error loading preview data. Please try again.";
        });
    });
  }

  // Import Preview Functionality
  const previewImportBtn = document.getElementById("previewImportBtn");
  if (previewImportBtn) {
    previewImportBtn.addEventListener("click", function () {
      const fileInput = document.getElementById("csv_file");

      if (fileInput.files.length === 0) {
        alert("Please select a CSV file first");
        return;
      }

      const file = fileInput.files[0];
      const formData = new FormData();
      formData.append("csv_file", file);

      // Show the modal
      const importPreviewModal = new bootstrap.Modal(
        document.getElementById("importPreviewModal"),
      );
      importPreviewModal.show();

      // Show loading state
      document
        .getElementById("importPreviewLoading")
        .classList.remove("d-none");
      document.getElementById("importPreviewContent").classList.add("d-none");
      document.getElementById("importPreviewNoData").classList.add("d-none");
      document.getElementById("importValidationErrors").classList.add("d-none");

      // Fetch preview data
      fetch("/api/historical_import_preview", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          // Hide loading state
          document
            .getElementById("importPreviewLoading")
            .classList.add("d-none");

          if (data.success) {
            // Show preview content
            document
              .getElementById("importPreviewContent")
              .classList.remove("d-none");

            // Update statistics
            document.getElementById("rowsToImport").textContent =
              data.stats.to_import;
            document.getElementById("rowsToUpdate").textContent =
              data.stats.to_update;
            document.getElementById("rowsToSkip").textContent =
              data.stats.to_skip;
            document.getElementById("uniqueTaxCodes").textContent =
              data.stats.unique_tax_codes;

            // Show validation errors if any
            if (data.warnings && data.warnings.length > 0) {
              document
                .getElementById("importValidationErrors")
                .classList.remove("d-none");
              const errorList = document.getElementById(
                "importValidationErrorsList",
              );
              errorList.innerHTML = "";

              data.warnings.forEach((warning) => {
                const li = document.createElement("li");
                li.textContent = warning;
                errorList.appendChild(li);
              });
            }

            // Populate the table
            if (data.preview && data.preview.length > 0) {
              const tbody = document.querySelector("#importPreviewTable tbody");
              tbody.innerHTML = "";

              data.preview.forEach((row, index) => {
                const tr = document.createElement("tr");

                // Determine row status
                let statusBadge = "";
                if (row.status === "new") {
                  statusBadge = '<span class="badge bg-success">New</span>';
                } else if (row.status === "update") {
                  statusBadge = '<span class="badge bg-warning">Update</span>';
                } else if (row.status === "skip") {
                  statusBadge = '<span class="badge bg-danger">Skip</span>';
                  tr.classList.add("table-danger");
                }

                tr.innerHTML = `
                                <td>${index + 1}</td>
                                <td>${row.tax_code || "N/A"}</td>
                                <td>${row.year || "N/A"}</td>
                                <td>${row.levy_rate ? parseFloat(row.levy_rate).toFixed(4) : "N/A"}</td>
                                <td>${row.levy_amount ? parseFloat(row.levy_amount).toLocaleString() : "N/A"}</td>
                                <td>${row.total_assessed_value ? parseFloat(row.total_assessed_value).toLocaleString() : "N/A"}</td>
                                <td>${statusBadge}</td>
                            `;
                tbody.appendChild(tr);
              });

              // Set up confirm import button
              document.getElementById("confirmImportBtn").onclick =
                function () {
                  document.getElementById("importForm").submit();
                };
            } else {
              document
                .getElementById("importPreviewNoData")
                .classList.remove("d-none");
            }
          } else {
            // Show error message
            document
              .getElementById("importPreviewNoData")
              .classList.remove("d-none");
            document.getElementById("importPreviewNoData").textContent =
              data.message || "Error analyzing CSV file";
          }
        })
        .catch((error) => {
          console.error("Error fetching import preview:", error);
          document
            .getElementById("importPreviewLoading")
            .classList.add("d-none");
          document
            .getElementById("importPreviewNoData")
            .classList.remove("d-none");
          document.getElementById("importPreviewNoData").textContent =
            "Error analyzing CSV file. Please try again.";
        });
    });
  }

  // Download Template Button
  const downloadTemplateBtn = document.getElementById("downloadTemplateBtn");
  if (downloadTemplateBtn) {
    downloadTemplateBtn.addEventListener("click", function () {
      // Create a CSV template string
      const headers = [
        "Tax Code",
        "Year",
        "Levy Rate",
        "Levy Amount",
        "Total Assessed Value",
      ];
      const sampleData = [
        ["100001", "2023", "0.1254", "1500000", "12000000"],
        ["100002", "2023", "0.1542", "2500000", "16000000"],
        ["100001", "2022", "0.1185", "1350000", "11400000"],
      ];

      let csvContent = headers.join(",") + "\n";
      sampleData.forEach((row) => {
        csvContent += row.join(",") + "\n";
      });

      // Create blob and download
      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "historical_rates_template.csv");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    });
  }

  // Compare Tax Codes Functionality
  const compareTaxCodesBtn = document.getElementById("compareTaxCodesBtn");
  const comparisonContainer = document.getElementById(
    "comparisonChartContainer",
  );
  const closeComparisonBtn = document.getElementById("closeComparisonBtn");

  if (compareTaxCodesBtn) {
    compareTaxCodesBtn.addEventListener("click", function () {
      // Get selected tax codes and years
      const taxCodeSelect = document.getElementById("compare_tax_codes");
      const yearSelect = document.getElementById("compare_years");

      const selectedTaxCodes = Array.from(taxCodeSelect.selectedOptions).map(
        (option) => option.value,
      );
      const selectedYears = Array.from(yearSelect.selectedOptions).map(
        (option) => option.value,
      );

      if (selectedTaxCodes.length === 0) {
        alert("Please select at least one tax code for comparison");
        return;
      }

      // Build query string
      const queryParams = new URLSearchParams();
      queryParams.append("tax_codes", selectedTaxCodes.join(","));
      if (selectedYears.length > 0) {
        queryParams.append("years", selectedYears.join(","));
      }

      // Show loading state
      comparisonContainer.classList.remove("d-none");
      const loadingHtml = `
                <div class="text-center py-4" id="comparisonLoading">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Loading comparison data...</p>
                </div>
            `;
      comparisonContainer.innerHTML = loadingHtml;

      // Fetch comparison data
      fetch(`/api/compare_tax_codes?${queryParams.toString()}`)
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            renderComparisonCharts(data.comparison_data);
          } else {
            comparisonContainer.innerHTML = `
                            <div class="alert alert-warning">
                                <i class="bi bi-exclamation-triangle-fill"></i> ${data.message || "Error loading comparison data"}
                            </div>
                        `;
          }
        })
        .catch((error) => {
          console.error("Error fetching comparison data:", error);
          comparisonContainer.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="bi bi-exclamation-triangle-fill"></i> Failed to load comparison data. Please try again.
                        </div>
                    `;
        });
    });
  }

  if (closeComparisonBtn) {
    closeComparisonBtn.addEventListener("click", function () {
      comparisonContainer.classList.add("d-none");
    });
  }

  /**
   * Renders the comparison charts using Chart.js
   */
  function renderComparisonCharts(comparisonData) {
    const taxCodes = comparisonData.tax_codes;
    const years = new Set();
    const taxCodeData = {};

    // Process data for each tax code
    for (const taxCode of taxCodes) {
      if (
        comparisonData.data[taxCode] &&
        comparisonData.data[taxCode].historical_data
      ) {
        const histData = comparisonData.data[taxCode].historical_data;
        taxCodeData[taxCode] = {
          years: [],
          rates: [],
          colors: [],
        };

        // Sort historical data by year (ascending)
        const sortedData = [...histData].sort((a, b) => a.year - b.year);

        sortedData.forEach((item) => {
          years.add(item.year);
          taxCodeData[taxCode].years.push(item.year);
          taxCodeData[taxCode].rates.push(item.levy_rate);
        });
      }
    }

    // Get unique years across all tax codes (sorted)
    const uniqueYears = Array.from(years).sort();

    // Generate colors for each tax code
    const colors = [
      "#007bff",
      "#6610f2",
      "#6f42c1",
      "#e83e8c",
      "#dc3545",
      "#fd7e14",
      "#ffc107",
      "#28a745",
      "#20c997",
      "#17a2b8",
      "#1e90ff",
      "#ff1493",
    ];

    // HTML for comparison charts
    let comparisonHtml = `
            <h6>
                <i class="bi bi-arrow-left-right"></i> Tax Code Comparison
                <button class="btn btn-sm btn-outline-secondary float-end" id="closeComparisonBtn">
                    <i class="bi bi-x"></i> Close
                </button>
            </h6>
            <div class="alert alert-info mb-3">
                <small>Comparing data for ${taxCodes.length} tax codes${comparisonData.years_filter ? ` (Years: ${comparisonData.years_filter.join(", ")})` : ""}.</small>
            </div>
            <div class="mb-4">
                <h6 class="small text-muted">Rate Comparison</h6>
                <canvas id="comparisonRateChart" width="400" height="200"></canvas>
            </div>
            <div class="mb-4">
                <h6 class="small text-muted">Year-over-Year Change Comparison</h6>
                <canvas id="comparisonChangeChart" width="400" height="200"></canvas>
            </div>
        `;

    comparisonContainer.innerHTML = comparisonHtml;

    // Re-attach close button listener
    document
      .getElementById("closeComparisonBtn")
      .addEventListener("click", function () {
        comparisonContainer.classList.add("d-none");
      });

    // Create datasets for rate comparison chart
    const rateDatasets = [];
    let colorIndex = 0;

    for (const taxCode of taxCodes) {
      if (taxCodeData[taxCode]) {
        rateDatasets.push({
          label: `Tax Code ${taxCode}`,
          data: taxCodeData[taxCode].rates,
          borderColor: colors[colorIndex % colors.length],
          backgroundColor: colors[colorIndex % colors.length] + "20",
          fill: false,
          tension: 0.1,
        });
        colorIndex++;
      }
    }

    // Create rate comparison chart
    const rateCtx = document
      .getElementById("comparisonRateChart")
      .getContext("2d");
    new Chart(rateCtx, {
      type: "line",
      data: {
        labels: uniqueYears,
        datasets: rateDatasets,
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: "Levy Rates by Year",
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                const label = context.dataset.label || "";
                const value = context.raw.toFixed(4);
                return `${label}: ${value}`;
              },
            },
          },
        },
        scales: {
          x: {
            title: {
              display: true,
              text: "Year",
            },
          },
          y: {
            title: {
              display: true,
              text: "Levy Rate",
            },
            ticks: {
              callback: function (value) {
                return value.toFixed(4);
              },
            },
          },
        },
      },
    });

    // Create datasets for YOY change chart
    const changeDatasets = [];
    colorIndex = 0;

    for (const taxCode of taxCodes) {
      if (taxCodeData[taxCode] && taxCodeData[taxCode].rates.length > 1) {
        const rates = taxCodeData[taxCode].rates;
        const years = taxCodeData[taxCode].years;
        const changes = [];
        const changeLabels = [];

        for (let i = 1; i < rates.length; i++) {
          const prevRate = rates[i - 1];
          const currentRate = rates[i];
          const change = ((currentRate - prevRate) / prevRate) * 100;
          changes.push(change);
          changeLabels.push(`${years[i - 1]}-${years[i]}`);
        }

        changeDatasets.push({
          label: `Tax Code ${taxCode}`,
          data: changes,
          borderColor: colors[colorIndex % colors.length],
          backgroundColor: colors[colorIndex % colors.length] + "40",
          borderWidth: 1,
        });
        colorIndex++;
      }
    }

    // Create YOY change chart if we have enough data
    if (changeDatasets.length > 0) {
      const changeCtx = document
        .getElementById("comparisonChangeChart")
        .getContext("2d");
      new Chart(changeCtx, {
        type: "bar",
        data: {
          labels: changeDatasets[0].data.map(
            (_, i) => `${uniqueYears[i]}-${uniqueYears[i + 1]}`,
          ),
          datasets: changeDatasets,
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: "Year-over-Year Percent Change",
            },
            tooltip: {
              callbacks: {
                label: function (context) {
                  const label = context.dataset.label || "";
                  const value = context.raw.toFixed(2);
                  return `${label}: ${value}%`;
                },
              },
            },
          },
          scales: {
            x: {
              title: {
                display: true,
                text: "Year Range",
              },
            },
            y: {
              title: {
                display: true,
                text: "Percent Change",
              },
              ticks: {
                callback: function (value) {
                  return value.toFixed(2) + "%";
                },
              },
            },
          },
        },
      });
    } else {
      document.getElementById("comparisonChangeChart").parentElement.innerHTML =
        '<div class="alert alert-info">Not enough historical data to calculate year-over-year changes.</div>';
    }
  }
});
