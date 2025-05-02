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
  
  // Additional data for tooltips and hover effects
  const tooltipData = taxCodeData.map((tc) => ({
    districtName: tc.district_name || 'Unknown',
    levyRate: tc.levy_rate || 0,
    assessedValue: tc.total_assessed_value || 0,
    levyAmount: tc.levy_amount || 0
  }));

  // Create levy rates chart
  createLevyRatesChart(labels, levyRates, tooltipData);

  // Create assessed values chart
  createAssessedValuesChart(labels, assessedValues, tooltipData);

  // Create levy amounts chart
  createLevyAmountsChart(labels, levyAmounts, tooltipData);
}

function createLevyRatesChart(labels, levyRates, tooltipData = []) {
  const ctx = document.getElementById("levyRatesChart");
  if (!ctx) return;

  // Generate hover colors (slightly brighter)
  const baseColor = "rgba(54, 162, 235, 0.6)";
  const hoverColor = "rgba(54, 162, 235, 0.85)";
  const backgroundColors = Array(labels.length).fill(baseColor);
  const hoverBackgroundColors = Array(labels.length).fill(hoverColor);

  // Custom tooltip formatting
  const tooltipFormatter = (context) => {
    const index = context.dataIndex;
    let tooltipContent = '';
    
    if (tooltipData && tooltipData[index]) {
      const data = tooltipData[index];
      tooltipContent = [
        `District: ${data.districtName || 'Unknown'}`,
        `Tax Code: ${labels[index]}`,
        `Levy Rate: ${levyRates[index].toFixed(6)} per $1,000`,
        `Assessed Value: ${formatCurrency(data.assessedValue)}`,
        `Levy Amount: ${formatCurrency(data.levyAmount)}`
      ];
      return tooltipContent;
    }
    
    return `${labels[index]}: ${levyRates[index].toFixed(6)}`;
  };
  
  // Create chart with enhanced interactivity
  const chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Levy Rate (per $1,000)",
          data: levyRates,
          backgroundColor: backgroundColors,
          borderColor: "rgba(54, 162, 235, 1)",
          borderWidth: 1,
          hoverBackgroundColor: hoverBackgroundColors,
          hoverBorderColor: "rgba(54, 162, 235, 1.0)",
          hoverBorderWidth: 2,
          borderRadius: 4,
          // Add subtle animations
          barPercentage: 0.8,
          categoryPercentage: 0.8,
        },
      ],
    },
    options: {
      responsive: true,
      animation: {
        duration: 1000,
        easing: 'easeOutQuart'
      },
      onHover: (event, chartElements) => {
        // Change cursor to pointer when hovering over bars
        event.native.target.style.cursor = chartElements.length ? 'pointer' : 'default';
        
        // Highlight the corresponding data row if implemented
        if (chartElements.length && typeof highlightTableRow === 'function') {
          const index = chartElements[0].index;
          highlightTableRow(index);
        }
      },
      plugins: {
        legend: {
          position: "top",
          labels: {
            font: {
              family: "'Inter', 'Helvetica', 'Arial', sans-serif",
              weight: '500'
            },
            padding: 15,
            usePointStyle: true,
            pointStyle: 'rect'
          },
          onHover: (event) => {
            event.native.target.style.cursor = 'pointer';
          }
        },
        title: {
          display: true,
          text: "Levy Rates by Tax Code",
          font: {
            size: 16,
            family: "'Inter', 'Helvetica', 'Arial', sans-serif",
            weight: '600'
          },
          padding: {
            top: 10,
            bottom: 20
          }
        },
        tooltip: {
          enabled: true,
          backgroundColor: 'rgba(0, 21, 41, 0.9)',
          titleFont: {
            size: 14,
            family: "'Inter', 'Helvetica', 'Arial', sans-serif",
            weight: '600'
          },
          bodyFont: {
            size: 13,
            family: "'Inter', 'Helvetica', 'Arial', sans-serif"
          },
          padding: 12,
          cornerRadius: 8,
          displayColors: false,
          callbacks: {
            title: (context) => context[0].label,
            label: tooltipFormatter,
            labelTextColor: () => '#ffffff'
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Rate per $1,000",
            font: {
              weight: '500'
            }
          },
          grid: {
            drawBorder: false,
            color: 'rgba(0, 0, 0, 0.05)'
          },
          ticks: {
            callback: (value) => value.toFixed(4)
          }
        },
        x: {
          grid: {
            display: false,
            drawBorder: false
          },
          ticks: {
            maxRotation: 45,
            minRotation: 45
          }
        }
      }
    },
  });
  
  // Store chart instance in global space for potential interactions
  if (!window.terrafusionCharts) {
    window.terrafusionCharts = {};
  }
  window.terrafusionCharts.levyRatesChart = chart;
  
  // Add click interactions
  ctx.onclick = (evt) => {
    const points = chart.getElementsAtEventForMode(evt, 'nearest', { intersect: true }, true);
    if (points.length) {
      const firstPoint = points[0];
      const label = chart.data.labels[firstPoint.index];
      const value = chart.data.datasets[firstPoint.datasetIndex].data[firstPoint.index];
      console.log(`Clicked on Tax Code: ${label} with rate: ${value}`);
      
      // Flash effect on clicked bar
      const dataset = chart.data.datasets[firstPoint.datasetIndex];
      const originalColor = dataset.backgroundColor[firstPoint.index];
      dataset.backgroundColor[firstPoint.index] = 'rgba(255, 193, 7, 0.8)';
      chart.update();
      
      // Restore original color after 300ms
      setTimeout(() => {
        dataset.backgroundColor[firstPoint.index] = originalColor;
        chart.update();
      }, 300);
    }
  };
}

function createAssessedValuesChart(labels, assessedValues, tooltipData = []) {
  const ctx = document.getElementById("assessedValuesChart");
  if (!ctx) return;

  // Format large numbers for display
  const formattedValues = assessedValues.map((value) => value / 1000000); // Convert to millions

  // Generate hover colors (slightly brighter)
  const baseColor = "rgba(75, 192, 192, 0.6)";
  const hoverColor = "rgba(75, 192, 192, 0.85)";
  const backgroundColors = Array(labels.length).fill(baseColor);
  const hoverBackgroundColors = Array(labels.length).fill(hoverColor);
  
  // Custom tooltip formatting
  const tooltipFormatter = (context) => {
    const index = context.dataIndex;
    let tooltipContent = '';
    
    if (tooltipData && tooltipData[index]) {
      const data = tooltipData[index];
      tooltipContent = [
        `District: ${data.districtName || 'Unknown'}`,
        `Tax Code: ${labels[index]}`,
        `Assessed Value: ${formatCurrency(data.assessedValue)}`,
        `Levy Rate: ${data.levyRate.toFixed(6)} per $1,000`,
        `Levy Amount: ${formatCurrency(data.levyAmount)}`
      ];
      return tooltipContent;
    }
    
    return `${labels[index]}: ${formatCurrency(assessedValues[index])}`;
  };

  const chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Total Assessed Value (millions)",
          data: formattedValues,
          backgroundColor: backgroundColors,
          borderColor: "rgba(75, 192, 192, 1)",
          borderWidth: 1,
          hoverBackgroundColor: hoverBackgroundColors,
          hoverBorderColor: "rgba(75, 192, 192, 1)",
          hoverBorderWidth: 2,
          borderRadius: 4,
          // Add subtle animations
          barPercentage: 0.8,
          categoryPercentage: 0.8,
        },
      ],
    },
    options: {
      responsive: true,
      animation: {
        duration: 1000,
        easing: 'easeOutQuart'
      },
      onHover: (event, chartElements) => {
        // Change cursor to pointer when hovering over bars
        event.native.target.style.cursor = chartElements.length ? 'pointer' : 'default';
        
        // Highlight the corresponding data row if implemented
        if (chartElements.length && typeof highlightTableRow === 'function') {
          const index = chartElements[0].index;
          highlightTableRow(index);
        }
      },
      plugins: {
        legend: {
          position: "top",
          labels: {
            font: {
              family: "'Inter', 'Helvetica', 'Arial', sans-serif",
              weight: '500'
            },
            padding: 15,
            usePointStyle: true,
            pointStyle: 'rect'
          },
          onHover: (event) => {
            event.native.target.style.cursor = 'pointer';
          }
        },
        title: {
          display: true,
          text: "Total Assessed Value by Tax Code",
          font: {
            size: 16,
            family: "'Inter', 'Helvetica', 'Arial', sans-serif",
            weight: '600'
          },
          padding: {
            top: 10,
            bottom: 20
          }
        },
        tooltip: {
          enabled: true,
          backgroundColor: 'rgba(0, 21, 41, 0.9)',
          titleFont: {
            size: 14,
            family: "'Inter', 'Helvetica', 'Arial', sans-serif",
            weight: '600'
          },
          bodyFont: {
            size: 13,
            family: "'Inter', 'Helvetica', 'Arial', sans-serif"
          },
          padding: 12,
          cornerRadius: 8,
          displayColors: false,
          callbacks: {
            title: (context) => context[0].label,
            label: tooltipFormatter,
            labelTextColor: () => '#ffffff'
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Value ($ millions)",
            font: {
              weight: '500'
            }
          },
          grid: {
            drawBorder: false,
            color: 'rgba(0, 0, 0, 0.05)'
          },
          ticks: {
            callback: (value) => `$${value}M`
          }
        },
        x: {
          grid: {
            display: false,
            drawBorder: false
          },
          ticks: {
            maxRotation: 45,
            minRotation: 45
          }
        }
      }
    },
  });
  
  // Store chart instance in global space for potential interactions
  if (!window.terrafusionCharts) {
    window.terrafusionCharts = {};
  }
  window.terrafusionCharts.assessedValuesChart = chart;
  
  // Add click interactions
  ctx.onclick = (evt) => {
    const points = chart.getElementsAtEventForMode(evt, 'nearest', { intersect: true }, true);
    if (points.length) {
      const firstPoint = points[0];
      const label = chart.data.labels[firstPoint.index];
      const value = chart.data.datasets[firstPoint.datasetIndex].data[firstPoint.index];
      console.log(`Clicked on Tax Code: ${label} with value: $${value}M`);
      
      // Flash effect on clicked bar
      const dataset = chart.data.datasets[firstPoint.datasetIndex];
      const originalColor = dataset.backgroundColor[firstPoint.index];
      dataset.backgroundColor[firstPoint.index] = 'rgba(46, 204, 113, 0.8)'; // Green highlight
      chart.update();
      
      // Restore original color after 300ms
      setTimeout(() => {
        dataset.backgroundColor[firstPoint.index] = originalColor;
        chart.update();
      }, 300);
    }
  };
}

function createLevyAmountsChart(labels, levyAmounts, tooltipData = []) {
  const ctx = document.getElementById("levyAmountsChart");
  if (!ctx) return;

  // Format large numbers for display
  const formattedValues = levyAmounts.map((value) => value / 1000); // Convert to thousands

  // Generate hover colors (slightly brighter)
  const baseColors = [
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
  ];
  
  const borderColors = [
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
  ];
  
  // Generate hover colors with higher opacity
  const hoverColors = baseColors.map(color => {
    return color.replace('0.6', '0.8');
  });
  
  // Custom tooltip formatting
  const tooltipFormatter = (context) => {
    const index = context.dataIndex;
    let tooltipContent = '';
    
    if (tooltipData && tooltipData[index]) {
      const data = tooltipData[index];
      tooltipContent = [
        `District: ${data.districtName || 'Unknown'}`,
        `Tax Code: ${labels[index]}`,
        `Levy Amount: ${formatCurrency(data.levyAmount)}`,
        `Levy Rate: ${data.levyRate.toFixed(6)} per $1,000`,
        `Assessed Value: ${formatCurrency(data.assessedValue)}`
      ];
      return tooltipContent;
    }
    
    return `${labels[index]}: ${formatCurrency(levyAmounts[index])}`;
  };

  const chart = new Chart(ctx, {
    type: "pie",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Levy Amount (thousands)",
          data: formattedValues,
          backgroundColor: baseColors,
          borderColor: borderColors,
          borderWidth: 1,
          hoverBackgroundColor: hoverColors,
          hoverBorderColor: borderColors,
          hoverBorderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      animation: {
        animateRotate: true,
        animateScale: true,
        duration: 1000,
        easing: 'easeOutQuart'
      },
      plugins: {
        legend: {
          position: "right",
          labels: {
            font: {
              family: "'Inter', 'Helvetica', 'Arial', sans-serif",
              weight: '500'
            },
            padding: 15,
            usePointStyle: true,
            pointStyle: 'circle'
          },
          onHover: (event) => {
            event.native.target.style.cursor = 'pointer';
          }
        },
        title: {
          display: true,
          text: "Levy Amounts by Tax Code",
          font: {
            size: 16,
            family: "'Inter', 'Helvetica', 'Arial', sans-serif",
            weight: '600'
          },
          padding: {
            top: 10,
            bottom: 20
          }
        },
        tooltip: {
          enabled: true,
          backgroundColor: 'rgba(0, 21, 41, 0.9)',
          titleFont: {
            size: 14,
            family: "'Inter', 'Helvetica', 'Arial', sans-serif",
            weight: '600'
          },
          bodyFont: {
            size: 13,
            family: "'Inter', 'Helvetica', 'Arial', sans-serif"
          },
          padding: 12,
          cornerRadius: 8,
          displayColors: true,
          callbacks: {
            title: (context) => context[0].label,
            label: tooltipFormatter,
            labelTextColor: () => '#ffffff'
          }
        }
      },
      // Add hover interaction
      onHover: (event, chartElements) => {
        event.native.target.style.cursor = chartElements.length ? 'pointer' : 'default';
        
        // Add subtle animation when hovering
        if (chartElements.length) {
          const index = chartElements[0].index;
          // Could add more interactive effects here
        }
      }
    },
  });
  
  // Store chart instance in global space for potential interactions
  if (!window.terrafusionCharts) {
    window.terrafusionCharts = {};
  }
  window.terrafusionCharts.levyAmountsChart = chart;
  
  // Add click interactions
  ctx.onclick = (evt) => {
    const points = chart.getElementsAtEventForMode(evt, 'nearest', { intersect: true }, true);
    if (points.length) {
      const firstPoint = points[0];
      const label = chart.data.labels[firstPoint.index];
      const value = chart.data.datasets[firstPoint.datasetIndex].data[firstPoint.index];
      console.log(`Clicked on Tax Code: ${label} with amount: ${value * 1000}`);
      
      // Trigger a slight explosion effect by temporarily adjusting the offset
      const originalOffset = 0;
      chart.getDatasetMeta(0).data[firstPoint.index].offset = 10;
      chart.update();
      
      // Restore original offset after a short delay
      setTimeout(() => {
        chart.getDatasetMeta(0).data[firstPoint.index].offset = originalOffset;
        chart.update();
      }, 300);
    }
  };
}

// Utility function to format currency
function formatCurrency(value) {
  if (value === null || value === undefined) return '$0.00';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
}

/**
 * Highlights the corresponding table row when hovering over chart elements
 * @param {number} index The index of the data point in the chart
 * @param {string} tableSelector CSS selector for the data table (default: '.data-table')
 */
function highlightTableRow(index, tableSelector = '.data-table') {
  const table = document.querySelector(tableSelector);
  if (!table) return;
  
  // Remove any existing highlights
  const highlightedRows = table.querySelectorAll('tr.highlight-row');
  highlightedRows.forEach(row => row.classList.remove('highlight-row'));
  
  // Find the corresponding table row (skip header row)
  const rows = table.querySelectorAll('tbody tr');
  if (index >= 0 && index < rows.length) {
    // Add highlight class
    rows[index].classList.add('highlight-row');
    
    // Scroll row into view if needed
    rows[index].scrollIntoView({
      behavior: 'smooth',
      block: 'center'
    });
  }
}

/**
 * Registers click handlers for table rows to highlight corresponding chart elements
 * @param {string} tableSelector CSS selector for the data table (default: '.data-table')
 */
function setupTableRowHighlighting(tableSelector = '.data-table') {
  const table = document.querySelector(tableSelector);
  if (!table) return;
  
  const rows = table.querySelectorAll('tbody tr');
  rows.forEach((row, index) => {
    row.addEventListener('click', () => {
      // Remove existing highlights
      table.querySelectorAll('tr.highlight-row').forEach(r => 
        r.classList.remove('highlight-row')
      );
      
      // Add highlight to clicked row
      row.classList.add('highlight-row');
      
      // Highlight corresponding chart elements if charts exist
      if (window.terrafusionCharts) {
        // Highlight bar in levy rates chart
        if (window.terrafusionCharts.levyRatesChart) {
          const chart = window.terrafusionCharts.levyRatesChart;
          const dataset = chart.data.datasets[0];
          
          // Reset all colors
          const baseColor = "rgba(54, 162, 235, 0.6)";
          dataset.backgroundColor = Array(dataset.data.length).fill(baseColor);
          
          // Highlight selected bar
          if (index < dataset.data.length) {
            dataset.backgroundColor[index] = 'rgba(255, 193, 7, 0.8)'; // Amber highlight
          }
          
          chart.update();
        }
        
        // Highlight bar in assessed values chart
        if (window.terrafusionCharts.assessedValuesChart) {
          const chart = window.terrafusionCharts.assessedValuesChart;
          const dataset = chart.data.datasets[0];
          
          // Reset all colors
          const baseColor = "rgba(75, 192, 192, 0.6)";
          dataset.backgroundColor = Array(dataset.data.length).fill(baseColor);
          
          // Highlight selected bar
          if (index < dataset.data.length) {
            dataset.backgroundColor[index] = 'rgba(46, 204, 113, 0.8)'; // Green highlight
          }
          
          chart.update();
        }
        
        // Highlight pie slice in levy amounts chart
        if (window.terrafusionCharts.levyAmountsChart) {
          const chart = window.terrafusionCharts.levyAmountsChart;
          
          // Apply slight offset to selected slice
          chart.getDatasetMeta(0).data.forEach((dataPoint, i) => {
            dataPoint.offset = (i === index) ? 10 : 0;
          });
          
          chart.update();
        }
      }
    });
    
    // Add hover effect to table rows
    row.addEventListener('mouseenter', () => {
      if (!row.classList.contains('highlight-row')) {
        row.classList.add('hover-row');
      }
    });
    
    row.addEventListener('mouseleave', () => {
      row.classList.remove('hover-row');
    });
  });
}

// Add necessary CSS for highlighting
document.addEventListener('DOMContentLoaded', function() {
  // Add style for highlighted rows if not already present
  if (!document.getElementById('chart-highlight-styles')) {
    const style = document.createElement('style');
    style.id = 'chart-highlight-styles';
    style.textContent = `
      .highlight-row {
        background-color: rgba(255, 252, 232, 0.7) !important;
        box-shadow: 0 0 8px rgba(0, 0, 0, 0.1);
        transition: background-color 0.3s ease;
      }
      .hover-row {
        background-color: rgba(240, 244, 245, 0.5);
        transition: background-color 0.3s ease;
      }
      .data-table tbody tr {
        cursor: pointer;
        transition: all 0.2s ease-in-out;
      }
      .data-table tbody tr:hover {
        transform: translateY(-2px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }
    `;
    document.head.appendChild(style);
  }
});
