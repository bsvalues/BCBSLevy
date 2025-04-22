// Charts.js - Client-side JavaScript for data visualization

function initializeCharts(taxCodeData) {
  if (!taxCodeData || taxCodeData.length === 0) {
    console.log("No tax code data available for charts");
    return;
  }

  // Prepare data for charts
  const labels = taxCodeData.map((tc) => tc.code);
  const levyRates = taxCodeData.map((tc) => tc.levy_rate || 0);
  const assessedValues = taxCodeData.map((tc) => tc.total_assessed_value || 0);
  const levyAmounts = taxCodeData.map((tc) => tc.levy_amount || 0);

  // Create levy rates chart
  createLevyRatesChart(labels, levyRates);

  // Create assessed values chart
  createAssessedValuesChart(labels, assessedValues);

  // Create levy amounts chart
  createLevyAmountsChart(labels, levyAmounts);
}

function createLevyRatesChart(labels, levyRates) {
  const ctx = document.getElementById("levyRatesChart");
  if (!ctx) return;

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Levy Rate (per $1,000)",
          data: levyRates,
          backgroundColor: "rgba(54, 162, 235, 0.6)",
          borderColor: "rgba(54, 162, 235, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "top",
        },
        title: {
          display: true,
          text: "Levy Rates by Tax Code",
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Rate per $1,000",
          },
        },
      },
    },
  });
}

function createAssessedValuesChart(labels, assessedValues) {
  const ctx = document.getElementById("assessedValuesChart");
  if (!ctx) return;

  // Format large numbers for display
  const formattedValues = assessedValues.map((value) => value / 1000000); // Convert to millions

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Total Assessed Value (millions)",
          data: formattedValues,
          backgroundColor: "rgba(75, 192, 192, 0.6)",
          borderColor: "rgba(75, 192, 192, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "top",
        },
        title: {
          display: true,
          text: "Total Assessed Value by Tax Code",
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Value ($ millions)",
          },
        },
      },
    },
  });
}

function createLevyAmountsChart(labels, levyAmounts) {
  const ctx = document.getElementById("levyAmountsChart");
  if (!ctx) return;

  // Format large numbers for display
  const formattedValues = levyAmounts.map((value) => value / 1000); // Convert to thousands

  new Chart(ctx, {
    type: "pie",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Levy Amount (thousands)",
          data: formattedValues,
          backgroundColor: [
            "rgba(255, 99, 132, 0.6)",
            "rgba(54, 162, 235, 0.6)",
            "rgba(255, 206, 86, 0.6)",
            "rgba(75, 192, 192, 0.6)",
            "rgba(153, 102, 255, 0.6)",
            "rgba(255, 159, 64, 0.6)",
            "rgba(199, 199, 199, 0.6)",
            "rgba(83, 102, 255, 0.6)",
            "rgba(40, 159, 64, 0.6)",
            "rgba(210, 199, 199, 0.6)",
          ],
          borderColor: [
            "rgba(255, 99, 132, 1)",
            "rgba(54, 162, 235, 1)",
            "rgba(255, 206, 86, 1)",
            "rgba(75, 192, 192, 1)",
            "rgba(153, 102, 255, 1)",
            "rgba(255, 159, 64, 1)",
            "rgba(199, 199, 199, 1)",
            "rgba(83, 102, 255, 1)",
            "rgba(40, 159, 64, 1)",
            "rgba(210, 199, 199, 1)",
          ],
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "right",
        },
        title: {
          display: true,
          text: "Levy Amounts by Tax Code",
        },
      },
    },
  });
}
