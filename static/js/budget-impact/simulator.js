/**
 * Budget Impact Simulator JavaScript
 * 
 * This script handles the budget impact simulation functionality, including:
 * - Standard simulations
 * - AI-powered analysis with Claude integration
 * - Multi-year projections
 * - Sensitivity analysis
 */

document.addEventListener('DOMContentLoaded', function() {
  // Log initialization for debugging
  console.log("Budget Impact Simulator JS initializing...");
  
  // Helper function to safely add event listeners
  function addSafeEventListener(element, event, handler) {
    if (element) {
      element.addEventListener(event, handler);
    } else {
      console.warn(`Element not found for ${event} event.`);
    }
  }
  
  // UI Elements - with null checks
  const yearSelect = document.getElementById('yearSelect');
  const runSimulationBtn = document.getElementById('runSimulation');
  const exportResultsBtn = document.getElementById('exportResults');
  const taxRateSlider = document.getElementById('taxRateSlider');
  const taxRateValue = document.getElementById('taxRateValue');
  const assessedValueSlider = document.getElementById('assessedValueSlider');
  const assessedValueValue = document.getElementById('assessedValueValue');
  const applyToAllDistricts = document.getElementById('applyToAllDistricts');
  const districtTypeApplyContainer = document.getElementById('districtTypeApplyContainer');
  const districtTypeFilters = document.querySelectorAll('.district-type-filter');
  const districtItems = document.querySelectorAll('.district-item');
  const districtCheckboxes = document.querySelectorAll('.district-checkbox');
  const districtTypeApplyCheckboxes = document.querySelectorAll('.district-type-apply');
  
  // Simulation type controls
  const standardSimulation = document.getElementById('standardSimulation');
  const aiSimulation = document.getElementById('aiSimulation');
  const multiYearSimulation = document.getElementById('multiYearSimulation');
  const sensitivityAnalysis = document.getElementById('sensitivityAnalysis');
  
  // Containers
  const simulationSummaryContainer = document.getElementById('simulationSummaryContainer');
  const districtImpactTableBody = document.getElementById('districtImpactTableBody');
  const aiInsightsContainer = document.getElementById('aiInsightsContainer');
  const multiYearProjectionsContainer = document.getElementById('multiYearProjectionsContainer');
  const sensitivityAnalysisContainer = document.getElementById('sensitivityAnalysisContainer');
  
  // Charts
  let levyAmountChart;
  let levyRateChart;
  let multiYearChart;
  let rateSensitivityChart;
  let valueSensitivityChart;
  
  // Only add events if we're on the budget impact page
  if (!document.querySelector('.budget-impact-page')) {
    console.log("Not on budget impact page, skipping event listeners");
    return; // Exit early if not on the right page
  }
  
  // Event listeners (with null checks)
  if (yearSelect) {
    yearSelect.addEventListener('change', function() {
      window.location.href = `/budget-impact/?year=${this.value}`;
    });
  }
  
  if (taxRateSlider && taxRateValue) {
    taxRateSlider.addEventListener('input', function() {
      taxRateValue.textContent = `${this.value}%`;
    });
  }
  
  if (assessedValueSlider && assessedValueValue) {
    assessedValueSlider.addEventListener('input', function() {
      assessedValueValue.textContent = `${this.value}%`;
    });
  }
  
  if (applyToAllDistricts && districtTypeApplyContainer) {
    applyToAllDistricts.addEventListener('change', function() {
      districtTypeApplyContainer.style.display = this.checked ? 'none' : 'block';
    });
  }
  
  // Filter districts by type
  districtTypeFilters.forEach(filter => {
    if (filter) {
      filter.addEventListener('change', filterDistricts);
    }
  });
  
  // Handle simulation type changes
  if (aiSimulation && multiYearSimulation && sensitivityAnalysis) {
    aiSimulation.addEventListener('change', function() {
      if (this.checked) {
        // Enable additional options
        multiYearSimulation.disabled = false;
        sensitivityAnalysis.disabled = false;
      }
    });
  }
  
  if (standardSimulation && multiYearSimulation && sensitivityAnalysis) {
    standardSimulation.addEventListener('change', function() {
      if (this.checked) {
        // Disable additional options
        multiYearSimulation.checked = false;
        multiYearSimulation.disabled = true;
        sensitivityAnalysis.checked = false;
        sensitivityAnalysis.disabled = true;
      }
    });
  }
  
  if (multiYearSimulation && aiSimulation && standardSimulation) {
    multiYearSimulation.addEventListener('change', function() {
      if (this.checked && !aiSimulation.checked) {
        aiSimulation.checked = true;
        standardSimulation.checked = false;
      }
    });
  }
  
  if (sensitivityAnalysis && aiSimulation && standardSimulation) {
    sensitivityAnalysis.addEventListener('change', function() {
      if (this.checked && !aiSimulation.checked) {
        aiSimulation.checked = true;
        standardSimulation.checked = false;
      }
    });
  }
  
  // Run simulation button (with null check)
  if (runSimulationBtn) {
    runSimulationBtn.addEventListener('click', function() {
      const selectedDistricts = getSelectedDistricts();
      if (selectedDistricts.length === 0) {
        alert('Please select at least one district for simulation.');
        return;
      }
      
      // Show loading state
      runSimulationBtn.disabled = true;
      runSimulationBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Running...';
      
      // Clear previous results
      resetResults();
      
      // Get simulation parameters
      const params = getSimulationParameters();
      
      // Run appropriate simulation type
      if (aiSimulation && aiSimulation.checked) {
        runAISimulation(params);
      } else {
        runStandardSimulation(params);
      }
    });
  }
  
  // Export results button (with null check)
  if (exportResultsBtn) {
    exportResultsBtn.addEventListener('click', exportResults);
  }
  
  // Initialize charts
  initializeCharts();
  
  /**
   * Filters districts based on selected district types
   */
  function filterDistricts() {
    const selectedTypes = Array.from(districtTypeFilters)
      .filter(cb => cb.checked)
      .map(cb => cb.value);
    
    districtItems.forEach(item => {
      const districtType = item.dataset.districtType;
      if (selectedTypes.length === 0 || selectedTypes.includes(districtType)) {
        item.style.display = 'block';
      } else {
        item.style.display = 'none';
        // Uncheck if hidden
        const checkbox = item.querySelector('.district-checkbox');
        if (checkbox) {
          checkbox.checked = false;
        }
      }
    });
  }
  
  /**
   * Gets the list of selected district IDs
   */
  function getSelectedDistricts() {
    return Array.from(districtCheckboxes)
      .filter(cb => cb.checked)
      .map(cb => parseInt(cb.value));
  }
  
  /**
   * Gets the district type filters to apply changes to
   */
  function getDistrictTypeFilters() {
    if (applyToAllDistricts.checked) {
      return [];
    }
    
    return Array.from(districtTypeApplyCheckboxes)
      .filter(cb => cb.checked)
      .map(cb => cb.value);
  }
  
  /**
   * Gets all simulation parameters
   */
  function getSimulationParameters() {
    const year = parseInt(yearSelect.value);
    const rateChangePercent = parseFloat(taxRateSlider.value);
    const assessedValueChangePercent = parseFloat(assessedValueSlider.value);
    const districtIds = getSelectedDistricts();
    const districtTypeFilters = getDistrictTypeFilters();
    const useAI = aiSimulation.checked;
    const multiYear = multiYearSimulation.checked;
    const sensitivityAnalysisEnabled = sensitivityAnalysis.checked;
    
    // First selected district or null for system-wide
    const districtId = districtIds.length === 1 ? districtIds[0] : null;
    
    return {
      year,
      district_id: districtId,
      district_ids: districtIds,
      scenario_parameters: {
        rate_change_percent: rateChangePercent,
        assessed_value_change_percent: assessedValueChangePercent,
        district_type_filters: districtTypeFilters,
        inflation_rate: 2.0, // Default values
        population_growth_rate: 1.0,
        economic_growth_factor: 1.5
      },
      multi_year: multiYear,
      sensitivity_analysis: sensitivityAnalysisEnabled
    };
  }
  
  /**
   * Run standard simulation via API
   */
  function runStandardSimulation(params) {
    // Show loading state
    runSimulationBtn.disabled = true;
    runSimulationBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
    
    // Clear any previous error messages
    clearErrorMessages();
    
    // Call the standard simulation API
    fetch('/budget-impact/api/simulation', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        year: params.year,
        district_ids: params.district_ids,
        scenario: params.scenario_parameters
      })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      // Check for success property in response
      if (data.success === false) {
        // Show error toast
        showErrorToast('Simulation Error', data.error || 'An error occurred during simulation');
        console.error('Simulation API returned error:', data.error);
        return;
      }
      
      // Handle the new API response format with success property
      if (data.success === true) {
        displaySimulationResults(data);
      } else {
        // Handle legacy API response format without success property
        displaySimulationResults(data);
      }
      
      runSimulationBtn.disabled = false;
      runSimulationBtn.innerHTML = 'Run Simulation';
      exportResultsBtn.disabled = false;
    })
    .catch(error => {
      console.error('Error running simulation:', error);
      showErrorToast('Simulation Failed', error.message || 'Please check the console for details');
      runSimulationBtn.disabled = false;
      runSimulationBtn.innerHTML = 'Run Simulation';
    });
  }
  
  /**
   * Run AI-powered simulation via API
   */
  function runAISimulation(params) {
    // Show loading state
    runSimulationBtn.disabled = true;
    runSimulationBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing AI Analysis...';
    
    // Clear any previous error messages
    clearErrorMessages();
    
    // Show appropriate containers based on options
    if (params.multi_year) {
      multiYearProjectionsContainer.style.display = 'block';
    }
    
    if (params.sensitivity_analysis) {
      sensitivityAnalysisContainer.style.display = 'block';
    }
    
    // Always show AI insights for AI simulation
    aiInsightsContainer.style.display = 'block';
    
    // Call the AI simulation API
    fetch('/budget-impact/api/ai-simulation', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      // Check if the API returned an error
      if (!data.success) {
        // Show error toast with more details
        showErrorToast('AI Simulation Error', data.error || 'Unknown error occurred with AI simulation');
        console.error('AI simulation API returned error:', data.error);
        
        // If we have a fallback standard simulation in response, display it
        if (data.baseline && data.simulation && data.impact) {
          console.log('Using fallback standard simulation data');
          displaySimulationResults(data);
          showInfoToast('Using Standard Simulation', 'AI simulation failed, showing standard results instead');
        }
        
        runSimulationBtn.disabled = false;
        runSimulationBtn.innerHTML = 'Run Simulation';
        return;
      }
      
      // Process successful response
      const results = data.simulation_results;
      
      if (!results) {
        showErrorToast('Simulation Error', 'No simulation results returned');
        console.error('No simulation results returned from AI API');
        runSimulationBtn.disabled = false;
        runSimulationBtn.innerHTML = 'Run Simulation';
        return;
      }
      
      // Display results
      displayAISimulationResults(results);
      
      // If we have optimization recommendations from the top-level API response or from the AI insights
      if (data.optimization_recommendations) {
        enableOptimizationRecommendations(data.optimization_recommendations);
      } else if (results.ai_insights && results.ai_insights.optimization_recommendations) {
        enableOptimizationRecommendations(results.ai_insights.optimization_recommendations);
      }
      
      // Show success toast
      showSuccessToast('AI Simulation Complete', 'The AI simulation was successfully processed');
      
      // Re-enable buttons
      runSimulationBtn.disabled = false;
      runSimulationBtn.innerHTML = 'Run Simulation';
      exportResultsBtn.disabled = false;
    })
    .catch(error => {
      console.error('Error running AI simulation:', error);
      showErrorToast('AI Simulation Failed', error.message || 'Please check the console for details');
      
      // Reset UI
      runSimulationBtn.disabled = false;
      runSimulationBtn.innerHTML = 'Run Simulation';
      aiInsightsContainer.innerHTML = '<div class="alert alert-danger">AI simulation failed. Please try again or use standard simulation.</div>';
    });
  }
  
  /**
   * Display standard simulation results
   */
  function displaySimulationResults(data) {
    const { baseline, simulation, impact } = data;
    
    // Display summary
    displaySummary(baseline, simulation);
    
    // Update charts
    updateCharts(baseline, simulation);
    
    // Update metrics
    updateMetrics(baseline, simulation);
    
    // Update district impact table
    updateDistrictImpactTable(baseline, simulation, impact);
  }
  
  /**
   * Display AI simulation results
   */
  function displayAISimulationResults(results) {
    const multiYear = results.multi_year || false;
    
    if (multiYear) {
      // Multi-year results
      const baseline = results.baseline;
      const projections = results.projections;
      
      // Display first year projection as simulation
      const simulation = projections[0];
      
      // Display summary
      displaySummary(baseline, simulation);
      
      // Update charts
      updateCharts(baseline, simulation);
      
      // Update metrics
      updateMetrics(baseline, simulation);
      
      // Update multi-year projections
      updateMultiYearProjections(baseline, projections);
    } else {
      // Single-year results
      const baseline = results.baseline;
      const simulation = results.simulation;
      
      // Display summary
      displaySummary(baseline, simulation);
      
      // Update charts
      updateCharts(baseline, simulation);
      
      // Update metrics
      updateMetrics(baseline, simulation);
    }
    
    // Check for district impacts
    if (simulation.district_impacts) {
      updateDistrictImpactTable(baseline, simulation, simulation.district_impacts);
    }
    
    // Display AI insights
    if (results.ai_insights) {
      displayAIInsights(results.ai_insights);
    }
    
    // Display sensitivity analysis if available
    if (results.sensitivity_analysis) {
      displaySensitivityAnalysis(results.sensitivity_analysis);
    }
  }
  
  /**
   * Display summary information
   */
  function displaySummary(baseline, simulation) {
    let summaryHtml = '<div class="card">';
    summaryHtml += '<div class="card-body">';
    
    // Summary content
    summaryHtml += `<p><strong>Total Levy:</strong> $${formatNumber(baseline.total_levy_amount)} → $${formatNumber(simulation.total_levy_amount)}</p>`;
    
    const levyAmountChange = simulation.total_levy_amount - baseline.total_levy_amount;
    const levyAmountPercent = (levyAmountChange / baseline.total_levy_amount) * 100;
    
    const changeClass = levyAmountChange > 0 ? 'impact-increase' : (levyAmountChange < 0 ? 'impact-decrease' : 'impact-neutral');
    
    summaryHtml += `<p><strong>Change:</strong> <span class="${changeClass}">$${formatNumber(levyAmountChange)} (${formatNumber(levyAmountPercent)}%)</span></p>`;
    
    if (baseline.avg_levy_rate && simulation.avg_levy_rate) {
      summaryHtml += `<p><strong>Avg Rate:</strong> ${formatNumber(baseline.avg_levy_rate)} → ${formatNumber(simulation.avg_levy_rate)}</p>`;
    }
    
    summaryHtml += '</div></div>';
    
    simulationSummaryContainer.innerHTML = summaryHtml;
  }
  
  /**
   * Update the visualization charts
   */
  function updateCharts(baseline, simulation) {
    // Update levy amount chart
    if (levyAmountChart) {
      const districtNames = [];
      const baselineLevyAmounts = [];
      const simulatedLevyAmounts = [];
      
      // Check if we have district data
      if (baseline.districts) {
        // System-wide data with multiple districts
        baseline.districts.forEach((district, i) => {
          const simDistrict = simulation.districts[i];
          districtNames.push(district.name || `District ${district.id}`);
          baselineLevyAmounts.push(district.total_levy_amount);
          simulatedLevyAmounts.push(simDistrict.total_levy_amount);
        });
      } else if (baseline.district_name) {
        // Single district data
        districtNames.push(baseline.district_name);
        baselineLevyAmounts.push(baseline.total_levy_amount);
        simulatedLevyAmounts.push(simulation.total_levy_amount);
      } else {
        // No district data, use total
        districtNames.push('Total');
        baselineLevyAmounts.push(baseline.total_levy_amount);
        simulatedLevyAmounts.push(simulation.total_levy_amount);
      }
      
      levyAmountChart.data.labels = districtNames;
      levyAmountChart.data.datasets[0].data = baselineLevyAmounts;
      levyAmountChart.data.datasets[1].data = simulatedLevyAmounts;
      levyAmountChart.update();
    }
    
    // Update levy rate chart
    if (levyRateChart) {
      const districtNames = [];
      const baselineRates = [];
      const simulatedRates = [];
      
      // Check if we have district data
      if (baseline.districts) {
        // System-wide data with multiple districts
        baseline.districts.forEach((district, i) => {
          const simDistrict = simulation.districts[i];
          districtNames.push(district.name || `District ${district.id}`);
          baselineRates.push(district.avg_levy_rate);
          simulatedRates.push(simDistrict.avg_levy_rate);
        });
      } else if (baseline.district_name) {
        // Single district data
        districtNames.push(baseline.district_name);
        baselineRates.push(baseline.avg_levy_rate);
        simulatedRates.push(simulation.avg_levy_rate);
      } else {
        // No district data, use average
        districtNames.push('Average');
        baselineRates.push(baseline.avg_levy_rate);
        simulatedRates.push(simulation.avg_levy_rate);
      }
      
      levyRateChart.data.labels = districtNames;
      levyRateChart.data.datasets[0].data = baselineRates;
      levyRateChart.data.datasets[1].data = simulatedRates;
      levyRateChart.update();
    }
  }
  
  /**
   * Update metrics display
   */
  function updateMetrics(baseline, simulation) {
    // Update baseline total levy
    document.getElementById('baselineTotalLevy').textContent = '$' + formatNumber(baseline.total_levy_amount);
    
    // Update simulated total levy
    document.getElementById('simulatedTotalLevy').textContent = '$' + formatNumber(simulation.total_levy_amount);
    
    // Calculate change and percentage
    const levyChange = simulation.total_levy_amount - baseline.total_levy_amount;
    const levyChangePercent = (levyChange / baseline.total_levy_amount) * 100;
    
    // Update levy change
    const levyChangeElement = document.getElementById('simulatedTotalLevyChange');
    levyChangeElement.textContent = formatNumber(levyChangePercent) + '% change';
    levyChangeElement.className = 'metric-change ' + (levyChange > 0 ? 'impact-positive' : (levyChange < 0 ? 'impact-negative' : 'impact-neutral'));
    
    // Check if we have property tax data
    if (baseline.avg_tax_per_property !== undefined) {
      document.getElementById('avgTaxPerProperty').textContent = '$' + formatNumber(simulation.avg_tax_per_property);
      
      const taxPerPropertyChange = simulation.avg_tax_per_property - baseline.avg_tax_per_property;
      const taxPerPropertyChangePercent = (taxPerPropertyChange / baseline.avg_tax_per_property) * 100;
      
      const taxPerPropertyChangeElement = document.getElementById('avgTaxPerPropertyChange');
      taxPerPropertyChangeElement.textContent = formatNumber(taxPerPropertyChangePercent) + '% change';
      taxPerPropertyChangeElement.className = 'metric-change ' + (taxPerPropertyChange > 0 ? 'impact-positive' : (taxPerPropertyChange < 0 ? 'impact-negative' : 'impact-neutral'));
    }
    
    // Check if we have levy rate data
    if (baseline.avg_levy_rate !== undefined) {
      document.getElementById('avgLevyRate').textContent = formatNumber(simulation.avg_levy_rate);
      
      const rateChange = simulation.avg_levy_rate - baseline.avg_levy_rate;
      const rateChangePercent = (rateChange / baseline.avg_levy_rate) * 100;
      
      const rateChangeElement = document.getElementById('avgLevyRateChange');
      rateChangeElement.textContent = formatNumber(rateChangePercent) + '% change';
      rateChangeElement.className = 'metric-change ' + (rateChange > 0 ? 'impact-positive' : (rateChange < 0 ? 'impact-negative' : 'impact-neutral'));
    }
  }
  
  /**
   * Update district impact table
   */
  function updateDistrictImpactTable(baseline, simulation, impact) {
    let tableHtml = '';
    
    // Handle system-wide data with multiple districts
    if (baseline.districts) {
      baseline.districts.forEach(district => {
        const districtId = district.id;
        const districtImpact = impact[districtId];
        
        if (districtImpact) {
          const baselineLevy = districtImpact.levy_amount.baseline;
          const simulatedLevy = districtImpact.levy_amount.simulation;
          const levyChange = districtImpact.levy_amount.change;
          const levyChangePercent = districtImpact.levy_amount.percent;
          
          const changeClass = levyChange > 0 ? 'text-success' : (levyChange < 0 ? 'text-danger' : 'text-muted');
          
          tableHtml += `<tr>
            <td>${district.name || `District ${district.id}`}</td>
            <td>${district.district_type || 'N/A'}</td>
            <td>$${formatNumber(baselineLevy)}</td>
            <td>$${formatNumber(simulatedLevy)}</td>
            <td class="${changeClass}">$${formatNumber(levyChange)}</td>
            <td class="${changeClass}">${formatNumber(levyChangePercent)}%</td>
          </tr>`;
        }
      });
    } else if (simulation.impact) {
      // Single district with impact data directly in simulation
      const districtName = baseline.district_name || `District ${baseline.id}`;
      const districtType = baseline.district_type || 'N/A';
      const baselineLevy = baseline.total_levy_amount;
      const simulatedLevy = simulation.total_levy_amount;
      const levyChange = simulation.impact.levy_amount_change;
      const levyChangePercent = simulation.impact.levy_amount_percent;
      
      const changeClass = levyChange > 0 ? 'text-success' : (levyChange < 0 ? 'text-danger' : 'text-muted');
      
      tableHtml += `<tr>
        <td>${districtName}</td>
        <td>${districtType}</td>
        <td>$${formatNumber(baselineLevy)}</td>
        <td>$${formatNumber(simulatedLevy)}</td>
        <td class="${changeClass}">$${formatNumber(levyChange)}</td>
        <td class="${changeClass}">${formatNumber(levyChangePercent)}%</td>
      </tr>`;
    }
    
    if (tableHtml) {
      districtImpactTableBody.innerHTML = tableHtml;
    } else {
      districtImpactTableBody.innerHTML = '<tr><td colspan="6" class="text-center">No district impact data available</td></tr>';
    }
  }
  
  /**
   * Update multi-year projections display
   */
  function updateMultiYearProjections(baseline, projections) {
    if (!projections || projections.length === 0) {
      return;
    }
    
    // Update multi-year chart
    if (multiYearChart) {
      const years = projections.map(p => p.year);
      const levyAmounts = projections.map(p => p.total_levy_amount);
      const levyRates = projections.map(p => p.avg_levy_rate);
      
      multiYearChart.data.labels = years;
      multiYearChart.data.datasets[0].data = levyAmounts;
      multiYearChart.data.datasets[1].data = levyRates.map(rate => rate * 100); // Scale rates for visibility
      multiYearChart.update();
    }
    
    // Update multi-year table
    let tableHtml = '';
    projections.forEach(projection => {
      const year = projection.year;
      const levyAmount = projection.total_levy_amount;
      const levyRate = projection.avg_levy_rate;
      const assessedValue = projection.total_assessed_value;
      const taxPerProperty = projection.avg_tax_per_property;
      
      const baselineLevy = baseline.total_levy_amount;
      const levyChangePercent = ((levyAmount - baselineLevy) / baselineLevy) * 100;
      
      const changeClass = levyChangePercent > 0 ? 'text-success' : (levyChangePercent < 0 ? 'text-danger' : 'text-muted');
      
      tableHtml += `<tr>
        <td>${year}</td>
        <td>$${formatNumber(levyAmount)}</td>
        <td>${formatNumber(levyRate)}</td>
        <td>$${formatNumber(assessedValue)}</td>
        <td>$${formatNumber(taxPerProperty)}</td>
        <td class="${changeClass}">${formatNumber(levyChangePercent)}%</td>
      </tr>`;
    });
    
    if (tableHtml) {
      document.getElementById('multiYearTableBody').innerHTML = tableHtml;
    }
  }
  
  /**
   * Display sensitivity analysis
   */
  function displaySensitivityAnalysis(sensitivityScenarios) {
    if (!sensitivityScenarios || sensitivityScenarios.length === 0) {
      return;
    }
    
    // Separate rate and value scenarios
    const rateScenarios = sensitivityScenarios.filter(s => s.parameter === 'rate_change_percent');
    const valueScenarios = sensitivityScenarios.filter(s => s.parameter === 'assessed_value_change_percent');
    
    // Update sensitivity charts
    if (rateSensitivityChart && rateScenarios.length > 0) {
      const values = rateScenarios.map(s => s.value);
      const impacts = rateScenarios.map(s => s.result.total_levy_amount);
      
      rateSensitivityChart.data.labels = values.map(v => v + '%');
      rateSensitivityChart.data.datasets[0].data = impacts;
      rateSensitivityChart.update();
    }
    
    if (valueSensitivityChart && valueScenarios.length > 0) {
      const values = valueScenarios.map(s => s.value);
      const impacts = valueScenarios.map(s => s.result.total_levy_amount);
      
      valueSensitivityChart.data.labels = values.map(v => v + '%');
      valueSensitivityChart.data.datasets[0].data = impacts;
      valueSensitivityChart.update();
    }
    
    // Update sensitivity table
    let tableHtml = '';
    sensitivityScenarios.forEach(scenario => {
      const parameter = scenario.parameter === 'rate_change_percent' ? 'Tax Rate Change' : 'Assessed Value Change';
      const value = scenario.value;
      const levyAmount = scenario.result.total_levy_amount;
      const levyChange = scenario.result.change;
      const levyChangePercent = scenario.result.percent;
      
      const changeClass = levyChange > 0 ? 'text-success' : (levyChange < 0 ? 'text-danger' : 'text-muted');
      
      tableHtml += `<tr>
        <td>${parameter}</td>
        <td>${value}%</td>
        <td>$${formatNumber(levyAmount)}</td>
        <td class="${changeClass}">$${formatNumber(levyChange)}</td>
        <td class="${changeClass}">${formatNumber(levyChangePercent)}%</td>
      </tr>`;
    });
    
    if (tableHtml) {
      document.getElementById('sensitivityTableBody').innerHTML = tableHtml;
    }
  }
  
  /**
   * Display AI insights
   */
  // Apply recommended optimal scenario values to sliders
  function applyOptimalScenario(rateChange, valueChange) {
    // Ensure parameters are valid numbers
    if (typeof rateChange !== 'number' || isNaN(rateChange)) {
      console.error('Invalid rate change value:', rateChange);
      return;
    }
    
    if (typeof valueChange !== 'number' || isNaN(valueChange)) {
      console.error('Invalid value change value:', valueChange);
      return;
    }
    
    // Update tax rate slider
    if (taxRateSlider) {
      // Clamp to slider min/max
      const min = parseFloat(taxRateSlider.min);
      const max = parseFloat(taxRateSlider.max);
      const clampedRate = Math.min(Math.max(rateChange, min), max);
      
      taxRateSlider.value = clampedRate;
      taxRateValue.textContent = `${clampedRate}%`;
    }
    
    // Update assessed value slider
    if (assessedValueSlider) {
      // Clamp to slider min/max
      const min = parseFloat(assessedValueSlider.min);
      const max = parseFloat(assessedValueSlider.max);
      const clampedValue = Math.min(Math.max(valueChange, min), max);
      
      assessedValueSlider.value = clampedValue;
      assessedValueValue.textContent = `${clampedValue}%`;
    }
    
    // Show notification
    const toast = new bootstrap.Toast(document.getElementById('optimalAppliedToast'));
    toast.show();
  }
  
  // Make function available to the window scope for the button onclick
  window.applyOptimalScenario = applyOptimalScenario;
  
  function displayAIInsights(insights) {
    // Display executive summary
    if (insights.executive_summary) {
      document.getElementById('executiveSummary').innerHTML = insights.executive_summary;
    }
    
    // Display key insights
    if (insights.key_insights && insights.key_insights.length > 0) {
      let insightsHtml = '<div class="list-group">';
      
      insights.key_insights.forEach(insight => {
        const badgeClass = getBadgeClassForSignificance(insight.significance);
        insightsHtml += `
          <div class="list-group-item">
            <div class="d-flex justify-content-between align-items-center">
              <h6 class="mb-1">${insight.area.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h6>
              <span class="badge ${badgeClass}">${insight.significance}</span>
            </div>
            <p class="mb-1">${insight.insight}</p>
          </div>
        `;
      });
      
      insightsHtml += '</div>';
      document.getElementById('keyInsights').innerHTML = insightsHtml;
    }
    
    // Display stakeholder impacts
    if (insights.stakeholder_impacts && insights.stakeholder_impacts.length > 0) {
      let impactsHtml = '<div class="table-responsive"><table class="table table-hover">';
      impactsHtml += '<thead><tr><th>Stakeholder</th><th>Impact</th><th>Scale</th></tr></thead><tbody>';
      
      insights.stakeholder_impacts.forEach(impact => {
        const badgeClass = getBadgeClassForMagnitude(impact.magnitude);
        const scaleClass = getBadgeClassForScale(impact.scale);
        
        impactsHtml += `<tr>
          <td>${impact.stakeholder.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</td>
          <td><span class="badge ${badgeClass} me-2">${impact.magnitude}</span>${impact.impact}</td>
          <td><span class="badge ${scaleClass}">${impact.scale}</span></td>
        </tr>`;
      });
      
      impactsHtml += '</tbody></table></div>';
      document.getElementById('stakeholderImpacts').innerHTML = impactsHtml;
    }
    
    // Display recommendations
    if (insights.recommendations && insights.recommendations.length > 0) {
      let recsHtml = '<div class="list-group">';
      
      insights.recommendations.forEach(rec => {
        const badgeClass = getBadgeClassForPriority(rec.priority);
        recsHtml += `
          <div class="list-group-item">
            <div class="d-flex justify-content-between align-items-center">
              <h6 class="mb-1">${rec.title}</h6>
              <span class="badge ${badgeClass}">${rec.priority}</span>
            </div>
            <p class="mb-1">${rec.description}</p>
          </div>
        `;
      });
      
      recsHtml += '</div>';
      document.getElementById('recommendations').innerHTML = recsHtml;
    }
    
    // Display implementation considerations
    if (insights.implementation_considerations && insights.implementation_considerations.length > 0) {
      let consHtml = '<ul class="list-group">';
      
      insights.implementation_considerations.forEach(consideration => {
        consHtml += `<li class="list-group-item">${consideration}</li>`;
      });
      
      consHtml += '</ul>';
      document.getElementById('implementationConsiderations').innerHTML = consHtml;
    }
    
    // Display historical context
    if (insights.historical_context) {
      document.getElementById('historicalContext').innerHTML = insights.historical_context;
    }
    
    // Display multi-year assessment if available
    if (insights.multi_year_assessment) {
      document.getElementById('multiYearAssessmentContainer').style.display = 'block';
      document.getElementById('multiYearAssessment').innerHTML = insights.multi_year_assessment;
    }
    
    // Display optimal scenario
    if (insights.optimal_scenario) {
      const optimal = insights.optimal_scenario;
      let optimalHtml = '<div class="card">';
      optimalHtml += '<div class="card-body">';
      optimalHtml += `<h6 class="card-title">Recommended Optimal Scenario</h6>`;
      optimalHtml += `<p><strong>Rate Change:</strong> ${formatNumber(optimal.rate_change)}%</p>`;
      optimalHtml += `<p><strong>Value Change:</strong> ${formatNumber(optimal.value_change)}%</p>`;
      optimalHtml += `<p class="card-text">${optimal.justification}</p>`;
      optimalHtml += '<div class="mt-2">';
      optimalHtml += `<button class="btn btn-sm btn-primary" onclick="applyOptimalScenario(${optimal.rate_change}, ${optimal.value_change})">Apply Optimal Values</button>`;
      optimalHtml += '</div>';
      optimalHtml += '</div></div>';
      
      document.getElementById('optimalScenario').innerHTML = optimalHtml;
    }
  }
  
  /**
   * Initialize chart objects
   */
  function initializeCharts() {
    // Levy Amount Chart
    const levyAmountCtx = document.getElementById('levyAmountChart').getContext('2d');
    levyAmountChart = new Chart(levyAmountCtx, {
      type: 'bar',
      data: {
        labels: [],
        datasets: [
          {
            label: 'Baseline',
            data: [],
            backgroundColor: 'rgba(54, 162, 235, 0.5)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
          },
          {
            label: 'Simulation',
            data: [],
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return '$' + value.toLocaleString();
              }
            }
          }
        },
        plugins: {
          title: {
            display: false,
            text: 'Levy Amounts Comparison'
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return context.dataset.label + ': $' + context.raw.toLocaleString();
              }
            }
          }
        }
      }
    });
    
    // Levy Rate Chart
    const levyRateCtx = document.getElementById('levyRateChart').getContext('2d');
    levyRateChart = new Chart(levyRateCtx, {
      type: 'bar',
      data: {
        labels: [],
        datasets: [
          {
            label: 'Baseline',
            data: [],
            backgroundColor: 'rgba(54, 162, 235, 0.5)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
          },
          {
            label: 'Simulation',
            data: [],
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true
          }
        },
        plugins: {
          title: {
            display: false,
            text: 'Levy Rates Comparison'
          }
        }
      }
    });
    
    // Multi-Year Chart
    const multiYearCtx = document.getElementById('multiYearChart').getContext('2d');
    multiYearChart = new Chart(multiYearCtx, {
      type: 'line',
      data: {
        labels: [],
        datasets: [
          {
            label: 'Total Levy Amount',
            data: [],
            backgroundColor: 'rgba(54, 162, 235, 0.1)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            yAxisID: 'y'
          },
          {
            label: 'Avg Levy Rate (x100)',
            data: [],
            backgroundColor: 'rgba(255, 99, 132, 0.1)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            position: 'left',
            title: {
              display: true,
              text: 'Total Levy Amount ($)'
            },
            ticks: {
              callback: function(value) {
                return '$' + value.toLocaleString();
              }
            }
          },
          y1: {
            beginAtZero: true,
            position: 'right',
            title: {
              display: true,
              text: 'Avg Levy Rate (x100)'
            },
            grid: {
              drawOnChartArea: false
            }
          }
        },
        plugins: {
          title: {
            display: false,
            text: 'Multi-Year Projections'
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                if (context.dataset.yAxisID === 'y') {
                  return context.dataset.label + ': $' + context.raw.toLocaleString();
                } else {
                  return context.dataset.label + ': ' + (context.raw / 100).toFixed(4);
                }
              }
            }
          }
        }
      }
    });
    
    // Rate Sensitivity Chart
    const rateSensitivityCtx = document.getElementById('rateSensitivityChart').getContext('2d');
    rateSensitivityChart = new Chart(rateSensitivityCtx, {
      type: 'line',
      data: {
        labels: [],
        datasets: [
          {
            label: 'Total Levy Amount',
            data: [],
            backgroundColor: 'rgba(75, 192, 192, 0.1)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return '$' + value.toLocaleString();
              }
            }
          }
        },
        plugins: {
          title: {
            display: false,
            text: 'Rate Change Sensitivity'
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return context.dataset.label + ': $' + context.raw.toLocaleString();
              }
            }
          }
        }
      }
    });
    
    // Value Sensitivity Chart
    const valueSensitivityCtx = document.getElementById('valueSensitivityChart').getContext('2d');
    valueSensitivityChart = new Chart(valueSensitivityCtx, {
      type: 'line',
      data: {
        labels: [],
        datasets: [
          {
            label: 'Total Levy Amount',
            data: [],
            backgroundColor: 'rgba(153, 102, 255, 0.1)',
            borderColor: 'rgba(153, 102, 255, 1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return '$' + value.toLocaleString();
              }
            }
          }
        },
        plugins: {
          title: {
            display: false,
            text: 'Assessed Value Change Sensitivity'
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return context.dataset.label + ': $' + context.raw.toLocaleString();
              }
            }
          }
        }
      }
    });
  }
  
  /**
   * Reset all result containers
   */
  function resetResults() {
    simulationSummaryContainer.innerHTML = '<div class="loader-container"><div class="loader"></div></div>';
    districtImpactTableBody.innerHTML = '<tr><td colspan="6" class="text-center">Loading...</td></tr>';
    
    // Reset AI insights
    aiInsightsContainer.style.display = 'none';
    document.getElementById('executiveSummary').innerHTML = '<div class="loader-container"><p class="text-muted">Run AI simulation to see insights</p></div>';
    document.getElementById('keyInsights').innerHTML = '<div class="loader-container"><p class="text-muted">Run AI simulation to see insights</p></div>';
    document.getElementById('stakeholderImpacts').innerHTML = '<div class="loader-container"><p class="text-muted">Run AI simulation to see insights</p></div>';
    document.getElementById('recommendations').innerHTML = '<div class="loader-container"><p class="text-muted">Run AI simulation to see insights</p></div>';
    document.getElementById('implementationConsiderations').innerHTML = '<div class="loader-container"><p class="text-muted">Run AI simulation to see insights</p></div>';
    document.getElementById('historicalContext').innerHTML = '<div class="loader-container"><p class="text-muted">Run AI simulation to see insights</p></div>';
    document.getElementById('multiYearAssessment').innerHTML = '<div class="loader-container"><p class="text-muted">Run AI simulation to see insights</p></div>';
    document.getElementById('optimalScenario').innerHTML = '<div class="loader-container"><p class="text-muted">Run AI simulation to see insights</p></div>';
    
    // Reset multi-year projections
    multiYearProjectionsContainer.style.display = 'none';
    document.getElementById('multiYearTableBody').innerHTML = '<tr><td colspan="6" class="text-center">Run multi-year simulation to see results</td></tr>';
    
    // Reset sensitivity analysis
    sensitivityAnalysisContainer.style.display = 'none';
    document.getElementById('sensitivityTableBody').innerHTML = '<tr><td colspan="5" class="text-center">Run sensitivity analysis to see results</td></tr>';
  }
  
  /**
   * Export simulation results
   */
  function exportResults() {
    alert('Export functionality not yet implemented');
  }
  
  /**
   * Get badge class for significance level
   */
  function getBadgeClassForSignificance(significance) {
    switch (significance.toLowerCase()) {
      case 'high':
        return 'bg-danger';
      case 'medium':
        return 'bg-warning text-dark';
      case 'low':
        return 'bg-info text-dark';
      default:
        return 'bg-secondary';
    }
  }
  
  /**
   * Get badge class for magnitude
   */
  function getBadgeClassForMagnitude(magnitude) {
    switch (magnitude.toLowerCase()) {
      case 'positive':
        return 'bg-success';
      case 'negative':
        return 'bg-danger';
      case 'mixed':
        return 'bg-warning text-dark';
      case 'neutral':
        return 'bg-secondary';
      default:
        return 'bg-secondary';
    }
  }
  
  /**
   * Get badge class for scale
   */
  function getBadgeClassForScale(scale) {
    switch (scale.toLowerCase()) {
      case 'high':
        return 'bg-danger';
      case 'medium':
        return 'bg-warning text-dark';
      case 'low':
        return 'bg-info text-dark';
      default:
        return 'bg-secondary';
    }
  }
  
  /**
   * Get badge class for priority
   */
  function getBadgeClassForPriority(priority) {
    switch (priority.toLowerCase()) {
      case 'high':
        return 'bg-danger';
      case 'medium':
        return 'bg-warning text-dark';
      case 'low':
        return 'bg-info text-dark';
      default:
        return 'bg-secondary';
    }
  }
  
  /**
   * Format number to 2 decimal places with commas
   */
  function formatNumber(value) {
    if (value === null || value === undefined) {
      return '0.00';
    }
    return parseFloat(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
});

/**
 * Apply optimal scenario values (called from AI recommendations)
 */
function applyOptimalScenario(rateChange, valueChange) {
  const taxRateSlider = document.getElementById('taxRateSlider');
  const taxRateValue = document.getElementById('taxRateValue');
  const assessedValueSlider = document.getElementById('assessedValueSlider');
  const assessedValueValue = document.getElementById('assessedValueValue');
  
  // Set rate change
  taxRateSlider.value = rateChange;
  taxRateValue.textContent = `${rateChange}%`;
  
  // Set value change
  assessedValueSlider.value = valueChange;
  assessedValueValue.textContent = `${valueChange}%`;
  
  // Notify user with toast
  showSuccessToast('Values Applied', 'Optimal scenario values have been applied! Click "Run Simulation" to see results.');
}

/**
 * Clear all error messages in the UI
 */
function clearErrorMessages() {
  // Remove any existing alert messages
  const existingAlerts = document.querySelectorAll('.alert');
  existingAlerts.forEach(alert => {
    if (alert.parentNode) {
      alert.parentNode.removeChild(alert);
    }
  });
  
  // Hide any existing toasts
  const existingToasts = document.querySelectorAll('.toast');
  existingToasts.forEach(toast => {
    const bsToast = bootstrap.Toast.getInstance(toast);
    if (bsToast) {
      bsToast.hide();
    }
  });
}

/**
 * Show an error toast notification
 * 
 * @param {string} title - The toast title
 * @param {string} message - The toast message
 */
function showErrorToast(title, message) {
  // Create toast container if it doesn't exist
  let toastContainer = document.getElementById('toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(toastContainer);
  }
  
  // Create toast element
  const toastId = 'error-toast-' + new Date().getTime();
  const toastHtml = `
    <div id="${toastId}" class="toast align-items-center text-white bg-danger border-0" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          <strong>${title}</strong>: ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;
  
  toastContainer.insertAdjacentHTML('beforeend', toastHtml);
  
  // Show the toast
  const toastElement = document.getElementById(toastId);
  const toast = new bootstrap.Toast(toastElement, { delay: 5000 });
  toast.show();
  
  // Log the error
  console.error(`${title}: ${message}`);
}

/**
 * Show an info toast notification
 * 
 * @param {string} title - The toast title
 * @param {string} message - The toast message
 */
function showInfoToast(title, message) {
  // Create toast container if it doesn't exist
  let toastContainer = document.getElementById('toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(toastContainer);
  }
  
  // Create toast element
  const toastId = 'info-toast-' + new Date().getTime();
  const toastHtml = `
    <div id="${toastId}" class="toast align-items-center text-dark bg-info border-0" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          <strong>${title}</strong>: ${message}
        </div>
        <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;
  
  toastContainer.insertAdjacentHTML('beforeend', toastHtml);
  
  // Show the toast
  const toastElement = document.getElementById(toastId);
  const toast = new bootstrap.Toast(toastElement, { delay: 4000 });
  toast.show();
}

/**
 * Enable and display optimization recommendations
 * 
 * @param {Object} recommendations - The optimization recommendations from the AI
 */
function enableOptimizationRecommendations(recommendations) {
  // Get the recommendations container
  const container = document.getElementById('recommendations');
  if (!container) return;
  
  // Clear loading indicator
  container.innerHTML = '';
  
  // Extract explanation if available
  let explanation = 'The AI has analyzed your scenario and recommends parameter adjustments to optimize your budget impact.';
  if (recommendations.explanation) {
    explanation = recommendations.explanation;
  }
  
  // Create recommendations content
  let content = `
    <div class="alert alert-info mb-3">
      <i class="bi bi-lightbulb-fill me-2"></i>
      <strong>AI-Recommended Optimal Scenario</strong>
    </div>
    <div class="card border-primary mb-3">
      <div class="card-header bg-primary text-white">
        <i class="bi bi-graph-up-arrow me-2"></i>Optimization Recommendations
      </div>
      <div class="card-body">
        <p>${explanation}</p>
        <div class="table-responsive">
          <table class="table table-sm table-striped mb-3">
            <thead class="table-light">
              <tr>
                <th>Parameter</th>
                <th class="text-end">Recommended Value</th>
              </tr>
            </thead>
            <tbody>
  `;
  
  // Check if we have the two key parameters that map to our sliders
  if (recommendations.tax_rate_adjustment !== undefined) {
    content += `
      <tr>
        <td>Tax Rate Adjustment</td>
        <td class="text-end fw-bold">${recommendations.tax_rate_adjustment.toFixed(2)}%</td>
      </tr>
    `;
  }
  
  if (recommendations.property_value_growth !== undefined) {
    content += `
      <tr>
        <td>Property Value Growth</td>
        <td class="text-end fw-bold">${recommendations.property_value_growth.toFixed(2)}%</td>
      </tr>
    `;
  }
  
  // Add all other recommendations
  for (const [key, value] of Object.entries(recommendations)) {
    // Skip the ones we've already added and the explanation
    if (key === 'tax_rate_adjustment' || key === 'property_value_growth' || key === 'explanation') {
      continue;
    }
    
    const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    const formattedValue = typeof value === 'number' ? value.toFixed(2) : value;
    
    content += `
      <tr>
        <td>${formattedKey}</td>
        <td class="text-end">${formattedValue}</td>
      </tr>
    `;
  }
  
  // Add apply button
  content += `
            </tbody>
          </table>
        </div>
        <button id="applyOptimalScenario" class="btn btn-primary">
          <i class="bi bi-magic me-2"></i>Apply Optimal Values to Sliders
        </button>
        <small class="text-muted d-block mt-2">
          Clicking this button will update the tax rate and property value sliders with the AI's recommended values.
        </small>
      </div>
    </div>
  `;
  
  // Insert content
  container.innerHTML = content;
  
  // Add event listener to the apply button
  document.getElementById('applyOptimalScenario').addEventListener('click', () => {
    applyOptimizationRecommendations(recommendations);
  });
}

/**
 * Apply the AI optimization recommendations to the input controls
 * 
 * @param {Object} recommendations - The optimization recommendations
 */
function applyOptimizationRecommendations(recommendations) {
  // The optimization recommendation fields to actual slider mappings
  // Since we currently only have two sliders: taxRateSlider and assessedValueSlider
  
  // First, get the tax_rate_adjustment recommendation, with fallback to a default
  let taxRateAdjustment = 0;
  if (recommendations.tax_rate_adjustment !== undefined) {
    taxRateAdjustment = recommendations.tax_rate_adjustment;
  }
  
  // Then, get the property_value_growth recommendation, with fallback to a default
  let propertyValueGrowth = 0; 
  if (recommendations.property_value_growth !== undefined) {
    propertyValueGrowth = recommendations.property_value_growth;
  }
  
  // Apply to the actual sliders we have in the UI
  const taxRateSlider = document.getElementById('taxRateSlider');
  if (taxRateSlider) {
    // Ensure the value is within the slider's range
    taxRateSlider.value = Math.max(
      parseFloat(taxRateSlider.min),
      Math.min(parseFloat(taxRateSlider.max), taxRateAdjustment)
    );
    // Trigger input event to update the display
    const event = new Event('input', { bubbles: true });
    taxRateSlider.dispatchEvent(event);
  }
  
  const assessedValueSlider = document.getElementById('assessedValueSlider');
  if (assessedValueSlider) {
    // Ensure the value is within the slider's range
    assessedValueSlider.value = Math.max(
      parseFloat(assessedValueSlider.min),
      Math.min(parseFloat(assessedValueSlider.max), propertyValueGrowth)
    );
    // Trigger input event to update the display
    const event = new Event('input', { bubbles: true });
    assessedValueSlider.dispatchEvent(event);
  }
  
  // Show the toast notification
  const optimalAppliedToast = new bootstrap.Toast(document.getElementById('optimalAppliedToast'));
  optimalAppliedToast.show();
  
  // Also show a success toast
  showSuccessToast('Optimal Scenario Applied', 'The AI-recommended values have been applied to the sliders. Run the simulation again to see the optimized results.');
}

/**
 * Show a success toast notification
 * 
 * @param {string} title - The toast title
 * @param {string} message - The toast message
 */
function showSuccessToast(title, message) {
  // Create toast container if it doesn't exist
  let toastContainer = document.getElementById('toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(toastContainer);
  }
  
  // Create toast element
  const toastId = 'success-toast-' + new Date().getTime();
  const toastHtml = `
    <div id="${toastId}" class="toast align-items-center text-white bg-success border-0" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          <strong>${title}</strong>: ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;
  
  toastContainer.insertAdjacentHTML('beforeend', toastHtml);
  
  // Show the toast
  const toastElement = document.getElementById(toastId);
  const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
  toast.show();
}