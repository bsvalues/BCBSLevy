/**
 * Functions to fetch and process real Benton County data for the demo
 */

/**
 * Fetch real data from the API
 * @param {string} endpoint - API endpoint to fetch data from
 * @param {Object} params - Parameters to include in the request
 * @param {string} targetId - ID of the element to update with the response
 * @param {string} fallbackHTML - HTML to use if the API call fails
 * @param {number} duration - Duration of the animation
 * @param {Function} callback - Optional callback to run after completing
 */
function fetchRealData(endpoint, params, targetId, fallbackHTML, duration, callback) {
    // Show loading indicator
    showDemoHUD('Fetching real Benton County data...');
    
    // Build URL with parameters
    let url = endpoint;
    if (params && Object.keys(params).length > 0) {
        const queryParams = new URLSearchParams();
        for (const key in params) {
            queryParams.append(key, params[key]);
        }
        url += '?' + queryParams.toString();
    }
    
    // Make API request
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('API response not ok');
            }
            return response.json();
        })
        .then(data => {
            // Process the data
            console.log('Successfully fetched real data:', data);
            
            // Update the target element with real data
            updateTargetWithRealData(targetId, data, duration, callback);
        })
        .catch(error => {
            console.warn('Error fetching real data:', error);
            
            // Fall back to using the provided HTML
            if (targetId === 'response-container') {
                simulateActivity(targetId, fallbackHTML, duration, callback);
            } else {
                console.error('Unknown target for fallback data:', targetId);
            }
        });
}

/**
 * Update a target element with real data
 * @param {string} targetId - ID of the element to update
 * @param {Object} data - Real data from the API
 * @param {number} duration - Duration of the animation
 * @param {Function} callback - Optional callback to run after completing
 */
function updateTargetWithRealData(targetId, data, duration, callback) {
    // Handle different target types
    switch(targetId) {
        case 'response-container':
            updateResponseContainer(data, duration, callback);
            break;
            
        default:
            console.error('Unknown target for real data:', targetId);
            break;
    }
}

/**
 * Update the response container with real data
 * @param {Object} data - Real data from the API
 * @param {number} duration - Duration of the animation
 * @param {Function} callback - Optional callback to run after completing
 */
function updateResponseContainer(data, duration, callback) {
    // Find or create response container
    let container = document.querySelector('.response-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'response-container mt-4';
        
        // Try to find the query container to append after
        const queryContainer = document.querySelector('.query-container');
        if (queryContainer) {
            queryContainer.parentNode.insertBefore(container, queryContainer.nextSibling);
        } else {
            // Fallback to main content
            const mainContent = document.querySelector('.container');
            if (mainContent) {
                mainContent.appendChild(container);
            } else {
                // Last resort - add to body
                document.body.appendChild(container);
            }
        }
    }
    
    // Generate HTML from data
    let html = '';
    
    // Check data type (forecast or analysis)
    if (data.forecast) {
        // Forecast data format
        html = generateForecastHTML(data);
    } else if (data.analysis) {
        // Analysis data format
        html = generateAnalysisHTML(data);
    } else {
        // Unknown data format
        console.error('Unknown data format:', data);
        html = `<div class="alert alert-warning">Unrecognized data format</div>`;
    }
    
    // Update container with animation
    container.innerHTML = html;
    container.style.opacity = '0';
    container.style.transform = 'translateY(20px)';
    container.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    
    setTimeout(function() {
        container.style.opacity = '1';
        container.style.transform = 'translateY(0)';
        
        // Run callback if provided
        if (typeof callback === 'function') {
            setTimeout(callback, 500);
        }
    }, 100);
}

/**
 * Generate HTML for forecast data
 * @param {Object} data - Forecast data
 * @returns {string} HTML for the forecast
 */
function generateForecastHTML(data) {
    const forecast = data.forecast;
    const years = forecast.years;
    const rates = forecast.rates;
    const levies = forecast.levies;
    const confidence = forecast.confidence_levels || ["High", "High", "Medium"];
    
    // Format data into an HTML table
    let tableRows = '';
    for (let i = 0; i < years.length; i++) {
        const confidenceClass = confidence[i].toLowerCase() === 'high' ? 'bg-success' : 'bg-warning';
        
        tableRows += `
            <tr>
                <td>${years[i]}</td>
                <td>$${rates[i].toFixed(2)}</td>
                <td>$${(levies[i]).toLocaleString()}</td>
                <td><span class="badge ${confidenceClass}">${confidence[i]}</span></td>
            </tr>
        `;
    }
    
    return `
        <div class="card mb-3 border-primary">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Benton County School District - Levy Rate Forecast</h5>
            </div>
            <div class="card-body">
                <div class="forecast-chart-container" style="height: 250px; position: relative;">
                    <canvas id="forecastChart"></canvas>
                </div>
                <table class="table table-sm mt-3">
                    <thead>
                        <tr>
                            <th>Year</th>
                            <th>Projected Rate</th>
                            <th>Projected Levy</th>
                            <th>Confidence</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${tableRows}
                    </tbody>
                </table>
                <div class="alert alert-info mt-3">
                    <strong>Analysis:</strong> ${data.analysis_summary || "Based on Benton County historical data, we project steady increases in levy rates over the forecast period."}
                </div>
            </div>
        </div>
    `;
}

/**
 * Generate HTML for analysis data
 * @param {Object} data - Analysis data
 * @returns {string} HTML for the analysis
 */
function generateAnalysisHTML(data) {
    const analysis = data.analysis;
    const district = analysis.district_name || "Benton County School District";
    const currentValue = analysis.current_assessed_value;
    const newConstruction = analysis.new_construction_value;
    const newConstructionPct = analysis.new_construction_percentage;
    const priorYearLevy = analysis.prior_year_levy;
    const maxRate = analysis.statutory_max_rate;
    
    // Generate scenarios table
    let scenariosRows = '';
    if (analysis.scenarios) {
        analysis.scenarios.forEach(scenario => {
            const cssClass = scenario.recommended ? 'table-success' : '';
            
            scenariosRows += `
                <tr class="${cssClass}">
                    <td>${scenario.name}</td>
                    <td>$${scenario.rate.toFixed(2)}</td>
                    <td>$${(scenario.levy_amount).toLocaleString()}</td>
                    <td>${scenario.percent_change > 0 ? '+' : ''}${scenario.percent_change.toFixed(1)}%</td>
                </tr>
            `;
        });
    }
    
    return `
        <div class="card mb-3 border-success">
            <div class="card-header bg-success text-white">
                <h5 class="mb-0">Levy Analysis Result</h5>
            </div>
            <div class="card-body">
                <h6>${district} - Levy Rate Analysis</h6>
                <p>Based on the parameters provided:</p>
                <ul>
                    <li>Current assessed value: $${currentValue.toLocaleString()}</li>
                    <li>New construction value: $${newConstruction.toLocaleString()} (${newConstructionPct}%)</li>
                    <li>Prior year levy amount: $${priorYearLevy.toLocaleString()}</li>
                    <li>Statutory maximum rate: $${maxRate.toFixed(2)} per $1,000</li>
                </ul>
                <h6 class="mt-3">Calculation Results:</h6>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Scenario</th>
                                <th>Calculated Rate</th>
                                <th>Levy Amount</th>
                                <th>% Change</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${scenariosRows}
                        </tbody>
                    </table>
                </div>
                <div class="alert alert-info mt-3">
                    <strong>Recommendation:</strong> ${analysis.recommendation || "Based on Benton County's historical patterns, the optimal levy rate balances revenue needs with taxpayer impact."}
                </div>
            </div>
        </div>
    `;
}