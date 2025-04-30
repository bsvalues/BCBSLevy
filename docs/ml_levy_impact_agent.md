# ML Levy Impact Agent

## Overview

The ML Levy Impact Agent is a specialized agent in the MCP framework that uses machine learning to predict the impact of levy changes on taxpayers and jurisdictions. It provides insights into how property values, mill rates, levy limits, and other factors affect tax outcomes.

## Features

- **ML-powered impact prediction**: Forecasts tax impacts based on multiple input parameters
- **Confidence scoring**: Provides confidence levels for predictions
- **Impact factor analysis**: Identifies key factors influencing the prediction
- **Human-readable explanations**: Generates natural language explanations of the results
- **AI-enhanced insights**: Uses Claude to provide deeper context and implications

## Architecture

The MLLevyImpactAgent is built on top of the MCPAgent base class and follows the MCP framework's agent design patterns. It integrates with:

- The MCP registry for function registration
- The WorkflowCoordinatorAgent for orchestration
- The Claude service for AI-enhanced explanations

## Usage

### Through the MCP API

To use the agent through the MCP framework's API:

```python
from utils.mcp_core import registry

# Run a levy impact analysis
result = registry.execute_function(
    "analyze_levy_impact",
    {
        "district_id": "SD001",
        "mill_rate": 1.5,
        "property_value": 250000,
        "levy_limit": 5000000,
        "prior_year_levy": 4800000,
        "district_type": "school",
        "year": 2025,
        "new_construction_value": 10000000
    }
)
```

### Using the CLI Tool

For direct interaction outside of the full application, use the CLI tool:

```bash
python utils/levy_impact_cli.py --input levy_impact_sample.json --explain
```

Or with direct parameters:

```bash
python utils/levy_impact_cli.py \
    --mill-rate 1.5 \
    --property-value 250000 \
    --levy-limit 5000000 \
    --prior-year-levy 4800000 \
    --district-type school \
    --year 2025 \
    --new-construction-value 10000000 \
    --explain
```

### Through the WorkflowCoordinatorAgent

For more complex scenarios, use the WorkflowCoordinatorAgent to orchestrate the analysis:

```python
from utils.mcp_agents import WorkflowCoordinatorAgent

coordinator = WorkflowCoordinatorAgent()
result = coordinator.analyze_levy_impact({
    "district_id": "SD001",
    "mill_rate": 1.5,
    "property_value": 250000,
    "levy_limit": 5000000,
    "prior_year_levy": 4800000,
    "district_type": "school",
    "year": 2025,
    "new_construction_value": 10000000
})
```

## Input Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `mill_rate` | float | Current mill rate (tax rate per $1,000 of assessed value) | Yes |
| `property_value` | float | Assessed property value | Yes |
| `levy_limit` | float | Maximum levy amount allowed by law | Yes |
| `prior_year_levy` | float | Previous year's levy amount | Yes |
| `district_type` | string | Type of taxing district (e.g., "school", "fire", "city") | Yes |
| `year` | int | Target year for the prediction | Yes |
| `new_construction_value` | float | Value of new construction in the district | No |
| `district_id` | string | Identifier for the district (required for workflow) | Workflow only |

## Output Format

The agent returns a structured JSON response with the following fields:

```json
{
  "estimated_impact": {
    "tax_per_property": 375.0,
    "total_levy": 4848000.0,
    "levy_rate_change": 1.0
  },
  "confidence": 0.85,
  "impact_factors": [
    "New construction adds capacity",
    "Near levy limit threshold"
  ],
  "explanations": [
    "Estimated impact calculated based on property value of $250,000.00 at a mill rate of 1.5000.",
    "Property would contribute approximately $375.00 to the levy.",
    "Total estimated levy of $4,848,000.00 compared to prior year levy of $4,800,000.00."
  ],
  "status": "success"
}
```

## Demo Script

A demonstration script is available to showcase the agent's capabilities:

```bash
python demonstration_scripts/run_levy_impact_demo.py
```

This script loads sample data, runs a prediction, and displays the results with explanations.

## Extending the Model

The current implementation uses a simplified calculation model to simulate ML predictions. To integrate a real machine learning model:

1. Modify the `_initialize_model` method to load your trained model
2. Update the `predict_levy_impact` method to use the model for inference
3. Add any necessary preprocessing and postprocessing steps

Example for a TensorFlow model:

```python
def _initialize_model(self):
    """Load the pre-trained levy impact prediction model."""
    import tensorflow as tf
    
    model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'levy_impact_model')
    self.model = tf.keras.models.load_model(model_path)
    self.model_initialized = True
    logger.info("Levy impact prediction model initialized successfully")
```

## Integration with the MCP Framework

The MLLevyImpactAgent is registered with the MCP framework through the `mcp_agent_manager.py` file. It's initialized with the other agents during the MCP Army initialization process and becomes part of the agent hierarchy.

The agent's capabilities are exposed through the MCP registry, allowing them to be invoked via the API or used in workflows orchestrated by the WorkflowCoordinatorAgent.

## Testing

Unit tests for the agent are available in `tests/test_ml_levy_impact_agent.py`. These tests verify:

- Basic agent initialization
- Prediction functionality with various parameter combinations
- Error handling for missing parameters
- Explanation generation

Run the tests with:

```bash
python -m unittest tests/test_ml_levy_impact_agent.py
```