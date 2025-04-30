
// TerraFusion Grafana Dashboard Configuration
const levyDashboard = {
  title: 'TerraFusion Metrics',
  panels: [
    {
      title: 'Agent Performance',
      type: 'graph',
      targets: [
        { expr: 'rate(mcp_agent_operations_total[5m])' },
        { expr: 'rate(mcp_agent_errors_total[5m])' }
      ]
    },
    {
      title: 'API Response Times',
      type: 'heatmap',
      targets: [{ expr: 'rate(api_request_duration_seconds_bucket[5m])' }]
    },
    {
      title: 'Database Query Performance',
      type: 'timeseries',
      targets: [{ expr: 'rate(database_query_duration_seconds[5m])' }]
    }
  ]
};

// Export dashboard configuration
window.levyDashboard = levyDashboard;
