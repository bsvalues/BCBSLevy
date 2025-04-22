# Model Content Protocol (MCP) Framework

This document explains the Model Content Protocol (MCP) framework implemented in the SaaS Levy Calculation Application, which provides AI-powered insights and autonomous agent capabilities.

## Overview

The Model Content Protocol (MCP) is a framework for integrating large language models (LLMs) like Claude and specialized AI agents into the SaaS Levy Calculation Application. It provides a standardized way to:

1. Connect to AI services
2. Register and discover AI capabilities
3. Execute AI-powered functions and workflows
4. Coordinate multiple AI agents
5. Provide consistent interfaces for AI insights

## Key Components

### 1. Function Registry

The Function Registry is a central repository for all AI-powered functions available in the system. Each function is registered with:

- Name
- Description
- Parameter schema
- Return type
- Implementation details

Example functions include:

- `analyze_tax_distribution`
- `analyze_historical_trends`
- `predict_levy_rates`

### 2. AI Agents

The MCP framework includes specialized AI agents for different tasks:

#### Levy Analysis Agent

- Analyzes levy rates and assessed values across districts
- Identifies patterns and anomalies in tax data
- Provides insights on tax burden distribution

#### Levy Prediction Agent

- Predicts future levy rates based on historical data
- Forecasts assessed value changes
- Models impact of statutory changes

#### Workflow Coordinator Agent

- Coordinates complex multi-agent workflows
- Manages dependencies between tasks
- Handles error recovery and retries

### 3. Workflows

Workflows are predefined sequences of function calls and agent interactions designed to accomplish specific tasks. Key workflows include:

#### Tax Distribution Analysis Workflow

1. Collect tax code and property data
2. Calculate distribution metrics
3. Generate visualizations
4. Provide insights and recommendations

#### Levy Calculation Workflow

1. Gather levy amounts and assessed values
2. Calculate preliminary levy rates
3. Apply statutory limits
4. Generate compliance report
5. Provide optimization recommendations

#### Property Lookup Workflow

1. Retrieve property data
2. Calculate property tax
3. Analyze property in context of similar properties
4. Generate insights and recommendations

### 4. Claude Integration

The application integrates with Anthropic's Claude 3.5 Sonnet model to provide advanced natural language capabilities:

- Property data analysis
- Levy insights generation
- Complex pattern recognition
- Natural language explanations
- Recommendation generation

The Claude service is implemented in `utils/anthropic_utils.py` and provides methods for:

- Generating text responses
- Chat-based interactions
- Structured data analysis
- JSON-formatted insights

### 5. API Layer

The MCP framework exposes a RESTful API for interacting with AI capabilities:

- `/api/mcp/functions` - List available functions
- `/api/mcp/workflows` - List available workflows
- `/api/mcp/agents` - List available agents
- `/api/mcp/function/execute` - Execute a function
- `/api/mcp/workflow/execute` - Execute a workflow
- `/api/mcp/agent/request` - Send a request to an agent

## Integration Points

The MCP framework is integrated throughout the application:

1. **Levy Calculator**: Uses Claude to analyze levy rates and provide insights
2. **Property Lookup**: Uses Claude to analyze property data and provide comparisons
3. **MCP Insights Page**: Dedicated dashboard for AI capabilities and analytics
4. **API Endpoints**: Enables programmatic access to AI functions
5. **Template Partials**: Reusable UI components for displaying AI insights

## Implementation Details

### Core Files

- `utils/mcp_core.py` - Core MCP functionality and registry
- `utils/mcp_agents.py` - Agent implementations
- `utils/mcp_llm.py` - LLM interface abstractions
- `utils/anthropic_utils.py` - Claude-specific implementation
- `utils/mcp_integration.py` - Route enhancement and UI integration

### Data Flow

1. Client requests page or calls API endpoint
2. MCP-enhanced route handler processes request
3. Application logic determines required AI capabilities
4. MCP registry locates appropriate function or agent
5. Claude or other LLM processes the request
6. Results are formatted and returned to the client

### Error Handling

The MCP framework includes robust error handling:

- Graceful degradation when AI services are unavailable
- Fallback to non-AI alternatives when appropriate
- Clear error messages and logging
- Automatic retries for transient errors

## Future Enhancements

Planned enhancements to the MCP framework include:

1. **Multi-Modal Support**: Adding image and document understanding capabilities
2. **Agent Memory**: Persistent memory for agents across sessions
3. **Workflow Builder**: UI for creating custom AI workflows
4. **Fine-Tuned Models**: Domain-specific model fine-tuning for levy calculation
5. **Enhanced Coordination**: More sophisticated multi-agent collaboration

## Best Practices

When extending the MCP framework:

1. Register new functions in the appropriate registry
2. Implement agents as classes with clear responsibilities
3. Design workflows as sequences of atomic steps
4. Use consistent parameter and return types
5. Include appropriate error handling
6. Document all AI capabilities in code and UI
7. Test AI functions with a variety of inputs

## References

- [Anthropic Claude API Documentation](https://docs.anthropic.com/claude/reference/getting-started-with-claude)
- [Model Content Protocol Specification](#) (Internal document)
- [AI Agent Development Guidelines](#) (Internal document)
