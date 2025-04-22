/**
 * Levy Calculator JavaScript Module
 *
 * This module handles all the client-side functionality for the levy calculator,
 * including form submissions, API calls, and dynamic UI updates.
 */

document.addEventListener("DOMContentLoaded", function () {
  try {
    // Initialize the levy calculator functionality
    initLevyCalculator();

    // Load the saved scenarios if on levy calculator page
    if (document.getElementById("scenariosSection")) {
      loadSavedScenarios();
    }

    console.log("Levy Calculator JS loaded successfully");
  } catch (err) {
    console.error(
      "Error initializing levy calculator:",
      err.message,
      err.stack,
    );
  }
});

/**
 * Initialize the levy calculator functionality
 */
function initLevyCalculator() {
  // DOM elements
  const levyCalculatorForm = document.getElementById("levyCalculatorForm");
  const forecastForm = document.getElementById("forecastForm");
  const calculatorResultsSection = document.getElementById(
    "calculatorResultsSection",
  );
  const forecastResultsSection = document.getElementById(
    "forecastResultsSection",
  );
  const complianceIssuesSection = document.getElementById(
    "complianceIssuesSection",
  );
  const adjustedRateSection = document.getElementById("adjustedRateSection");
  const saveScenarioBtn = document.getElementById("saveScenarioBtn");
  const saveResultBtn = document.getElementById("saveResultBtn");
  const taxDistrictSelect = document.getElementById("taxDistrict");

  // Check if we're on the levy calculator page
  if (!levyCalculatorForm) return;

  // Initialize tooltips
  try {
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (typeof bootstrap !== "undefined" && bootstrap.Tooltip) {
      tooltips.forEach((tooltip) => new bootstrap.Tooltip(tooltip));
    } else {
      console.warn("Bootstrap tooltip functionality not available");
    }
  } catch (err) {
    console.error("Error initializing tooltips:", err.message);
  }

  // Initialize modals if they exist
  let saveScenarioModal = null;
  let deleteScenarioModal = null;

  try {
    if (typeof bootstrap !== "undefined" && bootstrap.Modal) {
      saveScenarioModal = document.getElementById("saveScenarioModal")
        ? new bootstrap.Modal(document.getElementById("saveScenarioModal"))
        : null;
      deleteScenarioModal = document.getElementById("deleteScenarioModal")
        ? new bootstrap.Modal(document.getElementById("deleteScenarioModal"))
        : null;
    } else {
      console.warn("Bootstrap modal functionality not available");
    }
  } catch (err) {
    console.error("Error initializing modals:", err.message);
  }

  // State
  let currentDistrict = null;
  let currentCalculation = null;
  let currentScenarioId = null;

  // Event listeners
  if (levyCalculatorForm) {
    levyCalculatorForm.addEventListener("submit", handleLevyCalculation);
  }

  if (forecastForm) {
    forecastForm.addEventListener("submit", handleForecastCalculation);
  }

  if (saveScenarioBtn) {
    saveScenarioBtn.addEventListener("click", openSaveScenarioModal);
  }

  if (saveResultBtn) {
    saveResultBtn.addEventListener("click", openSaveScenarioModal);
  }

  if (taxDistrictSelect) {
    taxDistrictSelect.addEventListener("change", handleDistrictChange);
  }

  // Check for URL params to load a scenario
  const urlParams = new URLSearchParams(window.location.search);
  const scenarioId = urlParams.get("scenario");
  if (scenarioId) {
    loadScenario(scenarioId);
  }

  /**
   * Handle levy calculation form submission
   * @param {Event} e - Form submission event
   */
  function handleLevyCalculation(e) {
    e.preventDefault();

    // Show loading state
    document.getElementById("calculateBtn").innerHTML =
      '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Calculating...';
    document.getElementById("calculateBtn").disabled = true;

    const formData = new FormData(levyCalculatorForm);

    fetch("/levy-calculator/calculate", {
      method: "POST",
      body: formData,
      headers: {
        "X-CSRFToken": document
          .querySelector('meta[name="csrf-token"]')
          .getAttribute("content"),
      },
    })
      .then((response) => response.json())
      .then((data) => {
        // Reset button state
        document.getElementById("calculateBtn").innerHTML =
          '<i class="bi bi-calculator me-1"></i>Calculate Levy Rate';
        document.getElementById("calculateBtn").disabled = false;

        if (data.status === "success") {
          displayCalculationResults(data.result);
        } else {
          // Show error message
          alert("Error: " + data.message);
        }
      })
      .catch((error) => {
        console.error("Error calculating levy:", error);
        document.getElementById("calculateBtn").innerHTML =
          '<i class="bi bi-calculator me-1"></i>Calculate Levy Rate';
        document.getElementById("calculateBtn").disabled = false;
        alert(
          "An error occurred while calculating the levy rate. Please try again.",
        );
      });
  }

  /**
   * Handle forecast calculation form submission
   * @param {Event} e - Form submission event
   */
  function handleForecastCalculation(e) {
    e.preventDefault();

    if (!currentCalculation) {
      alert("Please calculate a levy rate first.");
      return;
    }

    // Get forecast form data
    const assessedValueChange =
      parseFloat(document.getElementById("assessedValueChange").value) || 0;
    const newConstructionValue =
      parseFloat(document.getElementById("newConstructionValue").value) || 0;
    const annexationValue =
      parseFloat(document.getElementById("annexationValue").value) || 0;

    // Calculate forecast
    const currentAssessedValue = currentCalculation.assessed_value;
    const currentLevyAmount = currentCalculation.levy_amount;
    const currentLevyRate = currentCalculation.levy_rate;

    // Calculate new assessed value with growth and additions
    const valueChangeMultiplier = 1 + assessedValueChange / 100;
    const newAssessedValue =
      currentAssessedValue * valueChangeMultiplier +
      newConstructionValue +
      annexationValue;

    // Calculate new levy rate with the same levy amount
    const newLevyRate = (currentLevyAmount / newAssessedValue) * 1000;

    // Calculate maximum allowable levy increase (typically 1% plus new construction)
    const baseIncrease = currentLevyAmount * 0.01; // 1% increase allowed by law
    const newConstructionAllowance =
      (newConstructionValue / currentAssessedValue) * currentLevyAmount;
    const annexationAllowance =
      (annexationValue / currentAssessedValue) * currentLevyAmount;
    const maxAllowableIncrease =
      baseIncrease + newConstructionAllowance + annexationAllowance;
    const maxLevyAmount = currentLevyAmount + maxAllowableIncrease;

    // Calculate new levy rate with maximum allowable levy
    const maxLevyRate = (maxLevyAmount / newAssessedValue) * 1000;

    // Display results
    displayForecastResults({
      current_year: currentCalculation.year,
      next_year: currentCalculation.year + 1,
      current_assessed_value: currentAssessedValue,
      new_assessed_value: newAssessedValue,
      current_levy_amount: currentLevyAmount,
      current_levy_rate: currentLevyRate,
      new_levy_rate: newLevyRate,
      max_allowable_increase: maxAllowableIncrease,
      max_levy_amount: maxLevyAmount,
      max_levy_rate: maxLevyRate,
      base_increase: baseIncrease,
      new_construction_allowance: newConstructionAllowance,
      annexation_allowance: annexationAllowance,
    });
  }

  /**
   * Display levy calculation results
   * @param {Object} result - Calculation result data
   */
  function displayCalculationResults(result) {
    // Store current calculation
    currentCalculation = result;

    // Update result section elements
    document.getElementById("resultDistrict").textContent =
      result.district_name;
    document.getElementById("resultYear").textContent = result.year;
    document.getElementById("resultAssessedValue").textContent = formatCurrency(
      result.assessed_value,
    );
    document.getElementById("resultStatutoryLimit").textContent =
      result.statutory_limit
        ? formatRate(result.statutory_limit)
        : "Not specified";
    document.getElementById("resultLevyAmount").textContent = formatCurrency(
      result.levy_amount,
    );
    document.getElementById("resultLevyRate").textContent = formatRate(
      result.levy_rate,
    );

    // Update calculation method display
    document.getElementById("formulaAssessedValue").textContent =
      formatCurrency(result.assessed_value);
    document.getElementById("formulaLevyAmount").textContent = formatCurrency(
      result.levy_amount,
    );
    document.getElementById("formulaAssessedValueFinal").textContent =
      formatCurrency(result.assessed_value);
    document.getElementById("formulaLevyAmountFinal").textContent =
      formatCurrency(result.levy_amount);
    document.getElementById("formulaLevyRate").textContent = formatRate(
      result.levy_rate,
    );

    // Handle compliance issues
    if (result.compliance_issues && result.compliance_issues.length > 0) {
      const issuesList = document.getElementById("complianceIssuesList");
      issuesList.innerHTML = "";

      result.compliance_issues.forEach((issue) => {
        const li = document.createElement("li");
        li.textContent = issue.message;
        issuesList.appendChild(li);
      });

      complianceIssuesSection.classList.remove("d-none");

      // Update result status badge
      document.getElementById("resultStatus").textContent = "Warning";
      document.getElementById("resultStatus").className =
        "badge bg-warning px-3 py-2";
    } else {
      complianceIssuesSection.classList.add("d-none");

      // Update result status badge
      document.getElementById("resultStatus").textContent = "Valid";
      document.getElementById("resultStatus").className =
        "badge bg-success px-3 py-2";
    }

    // Handle adjusted rate (if over statutory limit)
    if (result.adjustment_data) {
      document.getElementById("adjustedLevyRate").textContent = formatRate(
        result.adjustment_data.adjusted_rate,
      );
      document.getElementById("originalLevyRate").textContent = formatRate(
        result.adjustment_data.original_rate,
      );
      document.getElementById("adjustedLevyAmount").textContent =
        formatCurrency(result.adjustment_data.adjusted_amount);
      document.getElementById("levyReduction").textContent = formatCurrency(
        result.adjustment_data.difference,
      );

      adjustedRateSection.classList.remove("d-none");
    } else {
      adjustedRateSection.classList.add("d-none");
    }

    // Show results section
    calculatorResultsSection.style.display = "block";
  }

  /**
   * Display forecast results
   * @param {Object} forecast - Forecast data
   */
  function displayForecastResults(forecast) {
    // Update forecast display elements
    document.getElementById("forecastAssessedValue").textContent =
      formatCurrency(forecast.new_assessed_value);
    document.getElementById("forecastLevyRate").textContent = formatRate(
      forecast.new_levy_rate,
    );
    document.getElementById("forecastMaxIncrease").textContent = formatCurrency(
      forecast.max_allowable_increase,
    );
    document.getElementById("forecastMaxLevyAmount").textContent =
      formatCurrency(forecast.max_levy_amount);
    document.getElementById("forecastMaxLevyRate").textContent = formatRate(
      forecast.max_levy_rate,
    );
    document.getElementById("forecastBaseIncrease").textContent =
      formatCurrency(forecast.base_increase);
    document.getElementById("forecastNewConstructionAllowance").textContent =
      formatCurrency(forecast.new_construction_allowance);

    // Show forecast results section
    forecastResultsSection.classList.remove("d-none");
  }

  /**
   * Handle tax district change
   */
  function handleDistrictChange() {
    const districtId = taxDistrictSelect.value;

    if (!districtId) return;

    // Fetch district details
    fetch(`/levy-calculator/district/${districtId}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          currentDistrict = data.district;

          // Pre-fill levy amount if there's a recent rate
          if (data.levy_rates && data.levy_rates.length > 0) {
            const latestRate = data.levy_rates[0];
            document.getElementById("levyAmount").value =
              latestRate.levy_amount;
          }
        }
      })
      .catch((error) => {
        console.error("Error fetching district details:", error);
      });
  }

  /**
   * Open save scenario modal
   */
  function openSaveScenarioModal() {
    if (!currentCalculation) {
      alert("Please calculate a levy rate first.");
      return;
    }

    // Pre-fill modal form with current calculation data
    document.getElementById("scenarioDistrict").textContent =
      currentCalculation.district_name;
    document.getElementById("scenarioYear").textContent =
      currentCalculation.year;
    document.getElementById("scenarioLevyAmount").textContent = formatCurrency(
      currentCalculation.levy_amount,
    );
    document.getElementById("scenarioLevyRate").textContent = formatRate(
      currentCalculation.levy_rate,
    );

    // Set form values for submission
    document.getElementById("saveDistrictId").value =
      currentCalculation.district_id;
    document.getElementById("saveBaseYear").value = currentCalculation.year;
    document.getElementById("saveTargetYear").value = currentCalculation.year;
    document.getElementById("saveLevyAmount").value =
      currentCalculation.levy_amount;

    if (currentScenarioId) {
      document.getElementById("saveScenarioId").value = currentScenarioId;
      document.getElementById("saveScenarioModalLabel").textContent =
        "Update Scenario";
      document.getElementById("saveScenarioSubmitBtn").textContent = "Update";
    } else {
      document.getElementById("saveScenarioId").value = "";
      document.getElementById("saveScenarioModalLabel").textContent =
        "Save Scenario";
      document.getElementById("saveScenarioSubmitBtn").textContent = "Save";
    }

    // Show the modal
    if (saveScenarioModal) {
      saveScenarioModal.show();
    }
  }

  /**
   * Load a specific scenario
   * @param {number} scenarioId - The scenario ID to load
   */
  function loadScenario(scenarioId) {
    fetch(`/levy-calculator/scenario/${scenarioId}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          const scenario = data.scenario;
          currentScenarioId = scenario.id;

          // Set form values
          if (taxDistrictSelect) {
            taxDistrictSelect.value = scenario.district_id;
            // Trigger change event
            const event = new Event("change");
            taxDistrictSelect.dispatchEvent(event);
          }

          document.getElementById("taxYear").value = scenario.base_year;
          document.getElementById("levyAmount").value = scenario.levy_amount;

          // Set forecast values
          document.getElementById("assessedValueChange").value =
            scenario.assessed_value_change;
          document.getElementById("newConstructionValue").value =
            scenario.new_construction_value;
          document.getElementById("annexationValue").value =
            scenario.annexation_value;

          // Submit form to get results
          setTimeout(() => {
            levyCalculatorForm.dispatchEvent(new Event("submit"));
          }, 500);
        }
      })
      .catch((error) => {
        console.error("Error loading scenario:", error);
        alert("Error loading scenario. Please try again.");
      });
  }

  /**
   * Format a number as currency
   * @param {number} value - The value to format
   * @returns {string} Formatted currency string
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
   * Format a number as a rate
   * @param {number} value - The value to format
   * @returns {string} Formatted rate string
   */
  function formatRate(value) {
    return new Intl.NumberFormat("en-US", {
      minimumFractionDigits: 4,
      maximumFractionDigits: 4,
    }).format(value);
  }
}
