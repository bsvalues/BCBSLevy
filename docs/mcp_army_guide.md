# MCP Army System Technical Documentation

## Overview

The MCP Army is an advanced collaborative AI agent framework built on top of the existing Model Content Protocol (MCP) architecture. It enables multiple specialized AI agents to work together, share experiences, and collectively improve the system's capabilities over time.

This technical documentation provides a comprehensive guide to the MCP Army architecture, components, communication protocols, and integration paths.

## Architecture

The MCP Army system follows a modular architecture composed of these key components:

```
┌──────────────────────────────────────────────────────────────┐
│                       Flask Application                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────┐              ┌─────────────────────────┐ │
│  │                │              │                         │ │
│  │   MCP Army     │◄────────────►│  Original MCP System    │ │
│  │                │              │                         │ │
│  └────────┬───────┘              └─────────────────────────┘ │
│           │                                                  │
│           ▼                                                  │
│  ┌────────────────┐    ┌─────────────────┐    ┌───────────────┐  │
│  │                │    │                 │    │               │  │
│  │ Agent Manager  │◄──►│ Agent Types     │◄──►│ Experience    │  │
│  │                │    │                 │    │ Replay Buffer │  │
│  └────────────────┘    └─────────────────┘    └───────────────┘  │
│           │                   ▲                   ▲           │
│           ▼                   │                   │           │
│  ┌────────────────┐           │                   │           │
│  │                │           │                   │           │
│  │ Communication  │◄──────────┘                   │           │
│  │ Bus            │                               │           │
│  │                │◄──────────────────────────────┘           │
│  └────────────────┘                                           │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                       Database Layer                          │
└──────────────────────────────────────────────────────────────┘
```

### Key Components

1. **Agent Manager**
   - Central orchestration system for agent registration and monitoring
   - Handles task delegation and performance tracking
   - Coordinates collaborative workflows between agents

2. **Agent Types**
   - **LevyAnalysisAgent**: Specializes in tax distribution and levy rate analysis
   - **LevyPredictionAgent**: Focuses on forecasting and predictive modeling
   - **WorkflowCoordinatorAgent**: Orchestrates multi-agent complex workflows
   - Additional specialized agents as needed

3. **Communication Bus**
   - Message-based communication system for agent interaction
   - Event publishing and subscription mechanism
   - Standardized message format per protocol specification

4. **Experience Replay Buffer**
   - Central repository for agent experiences and learning
   - Enables knowledge sharing between agents
   - Supports prioritized replay for focused learning

5. **MCP Integration Layer**
   - Connects the Army architecture to the existing MCP system
   - Provides function registration and capability mapping
   - Ensures backward compatibility with existing MCP implementations

## Communication Protocol

The MCP Army uses a standardized message-based communication protocol defined in `utils/mcp_army_protocol.py`. All agent interactions follow this protocol to ensure consistency and reliability.

### Message Format

```json
{
  "messageId": "unique_uuid_for_this_message",
  "correlationId": "uuid_to_track_a_specific_task_or_workflow",
  "sourceAgentId": "agent_sending_message",
  "targetAgentId": "intended_recipient_or_topic",
  "timestamp": "ISO_8601_date_time_utc",
  "eventType": "COMMAND | EVENT | QUERY | RESPONSE | ERROR | STATUS_UPDATE | ASSISTANCE_REQUESTED",
  "payload": {
    // Event-specific data structure
  },
  "metadata": {
    "priority": "low | medium | high",
    "ttl": "seconds_to_live"
  }
}
```

### Event Types

- **COMMAND**: Direct instruction to an agent
- **EVENT**: Notification of something that happened
- **QUERY**: Request for information
- **RESPONSE**: Reply to a query or command
- **ERROR**: Error notification
- **STATUS_UPDATE**: Agent reporting its status
- **ASSISTANCE_REQUESTED**: Agent requesting help

## Experience Replay System

The Experience Replay Buffer allows agents to share and learn from each other's experiences. This collaborative learning mechanism is a core feature of the MCP Army design.

### Experience Format

```json
{
  "experienceId": "unique_uuid",
  "agentId": "agent_logging_experience",
  "timestamp": "ISO_8601_date_time_utc",
  "state": { /* Representation of state before action */ },
  "action": { /* Representation of action taken */ },
  "result": { /* Outcome of the action */ },
  "nextState": { /* Representation of state after action */ },
  "rewardSignal": "optional_numeric_reward_if_using_RL",
  "metadata": { "priority": "calculated_or_assigned_priority" }
}
```

### Priority Calculation

The system uses a prioritized experience replay mechanism, where experiences are prioritized based on:

1. Error events (highest priority)
2. Novel or unusual situations
3. Significant state changes
4. Recency (more recent experiences have higher priority)

### Training Process

The training process is triggered:
- On reaching a buffer size threshold (configurable)
- At regular time intervals (default: hourly)
- Manually via the MCP Army dashboard

## Agent Types

### LevyAnalysisAgent

**Purpose**: Specializes in analyzing tax distributions and levy rates

**Capabilities**:
- `analyze_levy_rates`: Analyze historical levy rates for patterns and anomalies
- `analyze_tax_distribution`: Evaluate tax burden distribution across districts
- `compare_assessed_values`: Compare property assessments across similar properties

### LevyPredictionAgent

**Purpose**: Focuses on forecasting and predictive modeling

**Capabilities**:
- `predict_levy_rates`: Forecast future levy rates based on historical data
- `predict_levy_rates_with_scenario`: Forecast rates under specific conditions
- `calculate_budget_impact`: Estimate budget impact of levy rate changes

### WorkflowCoordinatorAgent

**Purpose**: Orchestrates multi-agent workflows for complex tasks

**Capabilities**:
- `execute_workflow_levy_compliance_audit`: Coordinated levy compliance check
- `execute_workflow_cross_district_analysis`: Analysis across multiple districts
- `execute_workflow_historical_trend_forecasting`: Historical trend analysis
- `execute_workflow_regulatory_compliance_check`: Regulatory compliance verification

## Integrating with MCP Army

### Adding a New Agent

1. Create a new agent class derived from `MCPAgent`
2. Implement required capabilities and interfaces
3. Register with the AgentManager via configuration

Example:

```python
from utils.mcp_agents import MCPAgent

class ComplianceAuditAgent(MCPAgent):
    def __init__(self):
        super().__init__()
        self.capabilities = {
            'audit_compliance': self.audit_compliance,
            'verify_regulatory_requirements': self.verify_regulatory_requirements
        }
    
    def audit_compliance(self, parameters):
        # Implementation
        pass
    
    def verify_regulatory_requirements(self, parameters):
        # Implementation
        pass
```

### Executing Agent Capabilities

```python
from utils.mcp_army_init import get_agent_manager

# Get the agent manager
agent_manager = get_agent_manager()

# Execute a capability
result = agent_manager.execute_capability(
    'levy_analysis',
    'analyze_tax_distribution',
    {
        'district_id': 123,
        'year': 2025
    }
)
```

### Creating a Collaborative Workflow

1. Define a workflow in the WorkflowCoordinatorAgent
2. Register the workflow with a unique name
3. Implement the workflow execution logic

Example:

```python
def execute_workflow_compliance_audit(self, parameters):
    """Execute a compliance audit workflow."""
    district_id = parameters.get('district_id')
    year = parameters.get('year')
    
    # Step 1: Get district details
    district = self.execute_capability(
        'levy_analysis',
        'get_district_details',
        {'district_id': district_id}
    )
    
    # Step 2: Analyze historical rates
    historical_analysis = self.execute_capability(
        'levy_analysis',
        'analyze_levy_rates',
        {'district_id': district_id, 'year': year}
    )
    
    # Step 3: Predict future rates
    predictions = self.execute_capability(
        'levy_prediction',
        'predict_levy_rates',
        {'district_id': district_id, 'base_year': year}
    )
    
    # Compile results
    return {
        'district': district,
        'historical_analysis': historical_analysis,
        'predictions': predictions,
        'workflow_completed': True
    }
```

## Monitoring and Dashboard

The MCP Army Dashboard provides real-time visualization and control of the agent system. Key features include:

1. **Agent Status Monitoring**
   - Current status of all agents
   - Performance metrics and error rates
   - Activity logs

2. **Experience Replay Metrics**
   - Total experiences collected
   - Experience distribution by agent
   - Training cycle statistics

3. **Workflow Execution**
   - Execute collaborative workflows
   - Monitor workflow progress
   - View workflow results

4. **Assistance Requests**
   - View and manage agent assistance requests
   - Manually trigger agent assistance
   - Monitor help resolution status

## Error Handling

The MCP Army system implements a robust error handling strategy:

1. **Error Classification**
   - API/External Service Errors: Issues with external services
   - Agent Internal Errors: Issues within agent logic
   - Communication Errors: Issues with message delivery
   - Configuration Errors: Issues with system configuration

2. **Recovery Mechanisms**
   - Automatic retry for transient errors
   - Agent fallback for critical failures
   - Graceful degradation when components fail
   - Comprehensive error logging for post-mortem analysis

3. **Help Request System**
   - Automatic assistance requests when performance degrades
   - Manual assistance requests through the dashboard
   - Agent collaboration to resolve issues

## Security Considerations

The MCP Army implementation includes several security measures:

1. **Message Validation**
   - Strict validation of all inter-agent messages
   - Input sanitization to prevent injection attacks
   - Message source verification

2. **Access Control**
   - Role-based access to agent capabilities
   - Authentication for dashboard access
   - Audit logging of all agent actions

3. **Data Protection**
   - Sensitive data masking in experiences and logs
   - Secure handling of API credentials
   - Compliance with data protection regulations

## Performance Optimization

The system is designed for optimal performance:

1. **Resource Management**
   - Dynamic agent allocation based on workload
   - Resource throttling for busy agents
   - Performance monitoring and automatic optimization

2. **Caching**
   - Experience caching for frequent patterns
   - Result caching for common queries
   - Configuration caching for optimal startup

3. **Asynchronous Processing**
   - Non-blocking message processing
   - Background training cycles
   - Parallel workflow execution where possible

## Conclusion

The MCP Army system provides a powerful, extensible framework for collaborative AI agents. By following this documentation, developers can leverage the system's capabilities, extend it with new agent types, and create sophisticated multi-agent workflows for the Levy Calculation System.