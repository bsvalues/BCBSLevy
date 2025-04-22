/**
 * API Status Page JavaScript
 *
 * This script provides real-time functionality for the API status page,
 * including checking API key status, displaying diagnostic information,
 * and providing interactive troubleshooting guidance.
 */

document.addEventListener("DOMContentLoaded", function () {
  // Initialize status checks
  checkApiStatus();
  loadApiStatistics();

  // Set up periodic refresh
  setInterval(checkApiStatus, 30000); // Refresh every 30 seconds
  setInterval(loadApiStatistics, 60000); // Refresh statistics every 60 seconds

  // Attach event listener to Refresh button if it exists
  const refreshButton = document.getElementById("refreshStatus");
  if (refreshButton) {
    refreshButton.addEventListener("click", function () {
      checkApiStatus();
    });
  }

  // Attach event listener to Refresh stats button
  const refreshStatsButton = document.getElementById("refreshStats");
  if (refreshStatsButton) {
    refreshStatsButton.addEventListener("click", function () {
      loadApiStatistics();
    });
  }
});

/**
 * Check API status and update UI
 */
function checkApiStatus() {
  fetch("/mcp/api/status")
    .then((response) => response.json())
    .then((data) => {
      updateStatusUI(data);
    })
    .catch((error) => {
      console.error("Error checking API status:", error);
      updateStatusError();
    });
}

/**
 * Load API call statistics and update the statistics UI
 */
function loadApiStatistics() {
  fetch("/mcp/api/statistics")
    .then((response) => response.json())
    .then((data) => {
      updateStatisticsUI(data);
    })
    .catch((error) => {
      console.error("Error loading API statistics:", error);
      updateStatisticsError();
    });
}

/**
 * Update the API statistics UI with the fetched data
 */
function updateStatisticsUI(data) {
  // Format timestamp
  const timestamp = data.timestamp ? new Date(data.timestamp) : new Date();
  const formattedTime = timestamp.toLocaleTimeString();
  const formattedDate = timestamp.toLocaleDateString();

  // Update total calls
  const totalCallsElement = document.getElementById("totalApiCalls");
  if (totalCallsElement) {
    totalCallsElement.textContent = data.total_calls || 0;
  }

  // Update timestamp
  const timestampElement = document.getElementById("apiCallsTimestamp");
  if (timestampElement) {
    timestampElement.textContent = `Last updated: ${formattedDate} ${formattedTime}`;
  }

  // Update success rate
  const successRateElement = document.getElementById("apiSuccessRate");
  if (successRateElement) {
    const successRate =
      data.total_calls > 0
        ? ((data.success_count / data.total_calls) * 100).toFixed(1)
        : 0;
    successRateElement.textContent = `${successRate}%`;

    // Update progress bar
    const successRateBar = document.getElementById("apiSuccessRateBar");
    if (successRateBar) {
      successRateBar.style.width = `${successRate}%`;
      successRateBar.setAttribute("aria-valuenow", successRate);

      // Change color based on success rate
      if (successRate >= 90) {
        successRateBar.className = "progress-bar bg-success";
      } else if (successRate >= 75) {
        successRateBar.className = "progress-bar bg-info";
      } else if (successRate >= 50) {
        successRateBar.className = "progress-bar bg-warning";
      } else {
        successRateBar.className = "progress-bar bg-danger";
      }
    }
  }

  // Update average response time
  const avgTimeElement = document.getElementById("apiAvgTime");
  if (avgTimeElement) {
    avgTimeElement.textContent = data.avg_duration_ms
      ? data.avg_duration_ms.toFixed(1)
      : "-";
  }

  // Update service breakdown table
  const serviceStatsElement = document.getElementById("apiServiceStats");
  if (serviceStatsElement && data.calls_by_service) {
    let tableHTML = "";

    if (Object.keys(data.calls_by_service).length === 0) {
      tableHTML =
        '<tr><td colspan="4" class="text-center">No data available</td></tr>';
    } else {
      for (const [service, count] of Object.entries(data.calls_by_service)) {
        // Estimate success/error counts based on overall rate
        const successCount =
          data.total_calls > 0
            ? Math.round((data.success_count / data.total_calls) * count)
            : 0;
        const errorCount = count - successCount;

        tableHTML += `
                    <tr>
                        <td>${service}</td>
                        <td>${count}</td>
                        <td><span class="badge bg-success">${successCount}</span></td>
                        <td><span class="badge bg-danger">${errorCount}</span></td>
                    </tr>
                `;
      }
    }

    serviceStatsElement.innerHTML = tableHTML;
  }
}

/**
 * Handle errors when loading API statistics
 */
function updateStatisticsError() {
  // Update total calls
  const totalCallsElement = document.getElementById("totalApiCalls");
  if (totalCallsElement) {
    totalCallsElement.textContent = "-";
  }

  // Update timestamp
  const timestampElement = document.getElementById("apiCallsTimestamp");
  if (timestampElement) {
    timestampElement.textContent = "Error loading statistics";
  }

  // Update success rate
  const successRateElement = document.getElementById("apiSuccessRate");
  if (successRateElement) {
    successRateElement.textContent = "-";
  }

  // Update average response time
  const avgTimeElement = document.getElementById("apiAvgTime");
  if (avgTimeElement) {
    avgTimeElement.textContent = "-";
  }

  // Update service breakdown table
  const serviceStatsElement = document.getElementById("apiServiceStats");
  if (serviceStatsElement) {
    serviceStatsElement.innerHTML = `
            <tr>
                <td colspan="4" class="text-center text-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Error loading API statistics
                </td>
            </tr>
        `;
  }
}

/**
 * Update the status UI with API status data
 */
function updateStatusUI(data) {
  // Update main status badge
  const statusBadge = document.getElementById("apiStatusBadge");
  if (statusBadge) {
    statusBadge.textContent = getStatusText(data.status);
    statusBadge.className = `badge ${getStatusBadgeClass(data.status)}`;
  }

  // Update status message
  const statusMessage = document.getElementById("apiStatusMessage");
  if (statusMessage) {
    statusMessage.innerHTML = getStatusMessageHTML(data);
  }

  // Update diagnostic statuses
  updateDiagnostics(data);
}

/**
 * Update diagnostic indicators
 */
function updateDiagnostics(data) {
  // Configuration status
  const configStatus = document.getElementById("configStatus");
  if (configStatus) {
    if (data.status === "missing") {
      configStatus.textContent = "Not Configured";
      configStatus.className = "badge bg-warning";
    } else if (data.status === "invalid") {
      configStatus.textContent = "Invalid";
      configStatus.className = "badge bg-danger";
    } else {
      configStatus.textContent = "Configured";
      configStatus.className = "badge bg-success";
    }
  }

  // Credit status
  const creditStatus = document.getElementById("creditStatus");
  if (creditStatus) {
    if (data.status === "no_credits") {
      creditStatus.textContent = "Insufficient";
      creditStatus.className = "badge bg-danger";
    } else if (data.status === "valid") {
      creditStatus.textContent = "Available";
      creditStatus.className = "badge bg-success";
    } else {
      creditStatus.textContent = "Unknown";
      creditStatus.className = "badge bg-secondary";
    }
  }

  // Response time
  const responseStatus = document.getElementById("responseStatus");
  if (responseStatus) {
    if (data.status === "valid") {
      responseStatus.textContent = "Good";
      responseStatus.className = "badge bg-success";
    } else if (data.status === "no_credits") {
      responseStatus.textContent = "Credit Issue";
      responseStatus.className = "badge bg-warning";
    } else {
      responseStatus.textContent = "Unavailable";
      responseStatus.className = "badge bg-secondary";
    }
  }

  // Model availability
  const modelStatus = document.getElementById("modelStatus");
  if (modelStatus) {
    if (data.status === "valid") {
      modelStatus.textContent = "Available";
      modelStatus.className = "badge bg-success";
    } else if (data.status === "no_credits") {
      modelStatus.textContent = "Credit Required";
      modelStatus.className = "badge bg-warning";
    } else {
      modelStatus.textContent = "Unavailable";
      modelStatus.className = "badge bg-secondary";
    }
  }
}

/**
 * Get user-friendly status text from status code
 */
function getStatusText(status) {
  switch (status) {
    case "valid":
      return "Operational";
    case "missing":
      return "Not Configured";
    case "invalid":
      return "Invalid Key";
    case "no_credits":
      return "Credit Issue";
    default:
      return "Unknown";
  }
}

/**
 * Get appropriate Bootstrap badge class for status
 */
function getStatusBadgeClass(status) {
  switch (status) {
    case "valid":
      return "bg-success";
    case "missing":
      return "bg-warning";
    case "invalid":
    case "no_credits":
      return "bg-danger";
    default:
      return "bg-secondary";
  }
}

/**
 * Generate HTML for status message
 */
function getStatusMessageHTML(data) {
  let html = "";

  switch (data.status) {
    case "valid":
      html = `
                <div class="alert alert-success">
                    <div class="d-flex align-items-center mb-2">
                        <span class="status-indicator valid"></span>
                        <strong>API Key Active and Operational</strong>
                    </div>
                    <p class="mb-0">Your Anthropic API key is valid and has sufficient credits. MCP insights are fully operational.</p>
                </div>
            `;
      break;

    case "missing":
      html = `
                <div class="alert alert-warning">
                    <div class="d-flex align-items-center mb-2">
                        <span class="status-indicator missing"></span>
                        <strong>API Key Not Configured</strong>
                    </div>
                    <p>You need to configure an Anthropic API key to use MCP insights.</p>
                    <p class="mb-0">Click the "Configure API Key" button below to set up your API key.</p>
                </div>
            `;
      break;

    case "invalid":
      html = `
                <div class="alert alert-danger">
                    <div class="d-flex align-items-center mb-2">
                        <span class="status-indicator invalid"></span>
                        <strong>API Key Invalid</strong>
                    </div>
                    <p>Your API key is invalid or has an incorrect format. Anthropic API keys should start with <code>sk-ant-</code>.</p>
                    <p class="mb-0">Please configure a valid API key to use MCP insights.</p>
                </div>
            `;
      break;

    case "no_credits":
      html = `
                <div class="alert alert-danger">
                    <div class="d-flex align-items-center mb-2">
                        <span class="status-indicator no_credits"></span>
                        <strong>Credit Balance Issue</strong>
                    </div>
                    <p>Your API key is valid, but has insufficient credits to access Claude 3.5 Sonnet.</p>
                    <p class="mb-0">Please add credits to your Anthropic account or configure a different API key.</p>
                    <div class="mt-3">
                        <a href="https://console.anthropic.com/settings/billing" 
                           class="btn btn-sm btn-outline-danger me-2" target="_blank">
                            <i class="bi bi-credit-card me-1"></i>Add Credits
                        </a>
                    </div>
                </div>
            `;
      break;

    default:
      html = `
                <div class="alert alert-secondary">
                    <div class="d-flex align-items-center mb-2">
                        <span class="status-indicator error"></span>
                        <strong>Status Unknown</strong>
                    </div>
                    <p class="mb-0">Unable to determine API key status. Please try again later.</p>
                </div>
            `;
  }

  return html;
}

/**
 * Update UI to show error state
 */
function updateStatusError() {
  // Update main status badge
  const statusBadge = document.getElementById("apiStatusBadge");
  if (statusBadge) {
    statusBadge.textContent = "Error";
    statusBadge.className = "badge bg-danger";
  }

  // Update status message
  const statusMessage = document.getElementById("apiStatusMessage");
  if (statusMessage) {
    statusMessage.innerHTML = `
            <div class="alert alert-danger">
                <div class="d-flex align-items-center mb-2">
                    <span class="status-indicator error"></span>
                    <strong>Connection Error</strong>
                </div>
                <p class="mb-0">Unable to check API status. Please try again later or refresh the page.</p>
            </div>
        `;
  }

  // Update diagnostics to unknown
  const diagnosticElements = [
    "configStatus",
    "creditStatus",
    "responseStatus",
    "modelStatus",
  ];
  diagnosticElements.forEach((id) => {
    const element = document.getElementById(id);
    if (element) {
      element.textContent = "Error";
      element.className = "badge bg-danger";
    }
  });
}
