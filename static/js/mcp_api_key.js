/**
 * MCP API Key Management Script
 *
 * This script handles client-side functionality for API key management,
 * including saving and validating API keys for the MCP framework.
 */

document.addEventListener("DOMContentLoaded", () => {
  const apiKeyForm = document.getElementById("apiKeyForm");
  const apiKeyInput = document.getElementById("apiKey");
  const saveApiKeyBtn = document.getElementById("saveApiKey");
  const apiKeyResponseMessage = document.getElementById(
    "apiKeyResponseMessage",
  );

  if (!apiKeyForm || !apiKeyInput || !saveApiKeyBtn || !apiKeyResponseMessage) {
    // Some elements are missing, possibly on a different page
    return;
  }

  // Save API key button click handler
  saveApiKeyBtn.addEventListener("click", function () {
    const apiKey = apiKeyInput.value.trim();

    // Basic validation
    if (!apiKey) {
      showResponseMessage("error", "Please enter an API key.");
      return;
    }

    // Check for correct format
    if (!apiKey.startsWith("sk-ant-")) {
      showResponseMessage(
        "warning",
        'API key format seems invalid. Anthropic API keys typically start with "sk-ant-".',
      );
      return;
    }

    // Disable form controls during submission
    setFormLoading(true);

    // Send API key to server
    fetch("/api/mcp/save-api-key", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ api_key: apiKey }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          showResponseMessage(
            "success",
            "API key saved successfully! The page will refresh to apply changes.",
          );

          // Clear the input for security
          apiKeyInput.value = "";

          // Refresh the page after a short delay
          setTimeout(() => {
            window.location.reload();
          }, 2000);
        } else {
          showResponseMessage(
            "error",
            data.message || "Failed to save API key. Please try again.",
          );
        }
      })
      .catch((error) => {
        showResponseMessage(
          "error",
          "An error occurred while saving the API key. Please try again.",
        );
        console.error("Error saving API key:", error);
      })
      .finally(() => {
        setFormLoading(false);
      });
  });

  // Show response message with appropriate styling
  function showResponseMessage(type, message) {
    // Clear any existing message
    apiKeyResponseMessage.innerHTML = "";

    // Create new message
    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${type === "success" ? "success" : type === "warning" ? "warning" : "danger"} mt-3`;
    alertDiv.textContent = message;

    apiKeyResponseMessage.appendChild(alertDiv);
  }

  // Set loading state for form controls
  function setFormLoading(isLoading) {
    apiKeyInput.disabled = isLoading;
    saveApiKeyBtn.disabled = isLoading;

    if (isLoading) {
      // Add spinner to button
      saveApiKeyBtn.innerHTML =
        '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Saving...';
    } else {
      // Reset button text
      saveApiKeyBtn.innerHTML = "Save API Key";
    }
  }
});
