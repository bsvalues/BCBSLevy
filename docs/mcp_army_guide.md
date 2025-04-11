# MCP Army System: Implementation Guide

## Overview

The MCP Army System extends the existing Model Content Protocol (MCP) framework with a collaborative agent architecture that enables agents to share experiences, learn from each other, and request assistance when needed. This guide provides information on the system's architecture, components, and how to use and extend it.

## Architecture

The MCP Army System is built around the following key components:

### 1. Experience Replay Buffer

A shared memory store where agents record their experiences, including:
- Actions taken
- Results obtained
- Errors encountered
- Assistance received

This buffer enables collaborative learning across agents, allowing successful patterns to be recognized and reused.

### 2. Agent Communication Bus

A standardized messaging system that facilitates inter-agent communication with:
- Structured message format
- Event-based publish/subscribe model
- Message history tracking
- Event type filtering

### 3. Agent Manager

Centralized coordination system responsible for:
- Agent registration and lifecycle management
- Task delegation and monitoring
- Performance tracking and evaluation
- Assistance request routing

### 4. MCP Integration Layer

Connects the Agent Army with the existing MCP framework by:
- Exposing Agent Army capabilities as MCP functions
- Routing MCP function calls to appropriate agents
- Standardizing data exchange between systems
- Providing fault tolerance and error handling

## Core Components

### Experience Replay Buffer (`utils/mcp_experience.py`)

```python
# Creating an experience
collaboration_manager.replay_buffer.add({
    "agentId": "levy_analysis",
    "eventType": "action",
    "payload": {
        "action": "analyze_tax_distribution",
        "parameters": {"district_id": 123}
    }
})

# Sampling experiences for training
experiences = collaboration_manager.replay_buffer.sample(batch_size=32)
```

### Agent Communication Bus (`utils/mcp_experience.py`)

```python
# Publishing a message
collaboration_manager.comms_bus.publish({
    "agentId": "levy_analysis",
    "eventType": "result",
    "payload": {
        "task_id": "abc123",
        "result": {"distribution": {...}}
    }
})

# Subscribing to events
def handle_error_event(message):
    print(f"Error from {message['agentId']}: {message['payload'].get('error')}")
    
collaboration_manager.comms_bus.subscribe("error", handle_error_event)
```

### Agent Manager (`utils/mcp_agent_manager.py`)

```python
# Initialize agent army
agent_manager.initialize_agent_army()

# Delegate task to agent
agent_manager.delegate_task("levy_analysis", {
    "task_type": "capability_execution",
    "capability": "analyze_tax_distribution",
    "parameters": {"district_id": 123}
})

# Request assistance
agent_manager.request_assistance(
    "workflow_coordinator",  # Helping agent
    "levy_analysis",         # Agent needing help
    "optimization"           # Type of assistance
)
```

## Web Dashboard

The MCP Army Dashboard provides a comprehensive interface for monitoring and managing the agent army:

- **Agent Status**: View all registered agents, their status, and performance metrics
- **Experience Replay**: Explore recorded experiences and analyze learning patterns
- **Collaboration Network**: Visualize agent interactions and assistance patterns
- **Training Control**: Trigger training cycles and monitor learning progress

Access the dashboard at: `/mcp-army/dashboard`

## API Endpoints

The MCP Army System exposes the following API endpoints:

- **GET /mcp-army/api/agents**: List all registered agents
- **GET /mcp-army/api/agents/{agent_id}**: Get details for a specific agent
- **POST /mcp-army/api/agents/{agent_id}/capabilities/{capability}**: Execute a capability on an agent
- **POST /mcp-army/api/agents/{agent_id}/assistance/{target_agent}**: Request assistance between agents
- **GET /mcp-army/api/experiences/stats**: Get statistics about the experience replay buffer
- **GET /mcp-army/api/agents/{agent_id}/experiences**: Get experiences for a specific agent
- **POST /mcp-army/api/training/start**: Start a collaborative training cycle

## How to Use

### 1. Agent Extensions

To create a new agent type:

1. Create a new class that extends `MCPAgent` in `utils/mcp_agents.py`
2. Register capabilities with `self.register_capability()`
3. Add the agent to the initialization in `utils/mcp_agent_manager.py`

Example:

```python
class ComplianceAgent(MCPAgent):
    """Agent for verifying tax compliance."""
    
    def __init__(self):
        """Initialize the Compliance Agent."""
        super().__init__(
            name="ComplianceAgent",
            description="Verifies tax compliance against regulatory requirements"
        )
        
        # Register capabilities
        self.register_capability("verify_compliance")
        self.register_capability("generate_compliance_report")
        
        # Claude service for AI capabilities
        self.claude = get_claude_service()
    
    def verify_district_compliance(self, district_id: int, year: int) -> Dict[str, Any]:
        """
        Verify compliance for a tax district.
        
        Args:
            district_id: ID of the tax district
            year: Tax year to verify
            
        Returns:
            Compliance verification results
        """
        # Implementation
        pass
```

### 2. Experience Recording

To record experiences in an agent:

```python
def my_agent_function(self, params):
    # Record action
    collaboration_manager.comms_bus.publish({
        "agentId": self.name,
        "eventType": "action",
        "payload": {
            "function": "my_agent_function",
            "parameters": params
        }
    })
    
    try:
        # Perform action
        result = self._perform_calculation(params)
        
        # Record success
        collaboration_manager.comms_bus.publish({
            "agentId": self.name,
            "eventType": "result",
            "payload": {
                "function": "my_agent_function",
                "result": result
            }
        })
        
        return result
        
    except Exception as e:
        # Record error
        collaboration_manager.comms_bus.publish({
            "agentId": self.name,
            "eventType": "error",
            "payload": {
                "function": "my_agent_function",
                "error": str(e)
            }
        })
        raise
```

### 3. Help Requests

To request help in an agent:

```python
def complex_analysis(self, data):
    try:
        # Try to perform analysis
        result = self._perform_analysis(data)
        return result
    except Exception as e:
        # Request help
        collaboration_manager.request_help(
            self.name,
            f"Failed to analyze data: {str(e)}",
            priority=0.8
        )
        
        # Return partial or fallback result
        return {"error": str(e), "partial_results": self._get_fallback_analysis(data)}
```

## Extending the System

### 1. New Agent Types

To implement a new agent type:

1. Create a new class in `utils/mcp_agents.py` extending `MCPAgent`
2. Add the agent to the initialization in `agent_manager.initialize_agent_army()`
3. Register the agent's functions with the MCP registry
4. Add UI components to the dashboard if needed

### 2. New Training Methods

To implement a new training approach:

1. Extend the `start_training_cycle` method in `MCPCollaborationManager`
2. Implement the training logic using sampled experiences
3. Add an API endpoint to trigger the training
4. Add UI components to visualize training results

### 3. Custom Workflows

To implement custom agent workflows:

1. Create functions in `workflow_coordinator_agent` that orchestrate multi-agent interactions
2. Register these functions with the MCP registry
3. Add API endpoints to trigger the workflows
4. Add UI components to visualize workflow execution

## Best Practices

1. **Structured Messages**: Follow the standard message format with `agentId`, `eventType`, and `payload`
2. **Error Handling**: Always catch and log errors, ensuring they're properly recorded in the experience buffer
3. **Performance Monitoring**: Regularly check agent performance metrics and look for opportunities to improve
4. **Training Frequency**: Run training cycles at appropriate intervals based on experience accumulation
5. **Documentation**: Document new agent capabilities, parameters, and expected responses
6. **Validation**: Always validate inputs and handle edge cases gracefully
7. **Testing**: Add comprehensive tests for new agent types and capabilities

## Troubleshooting

### MCP Army System Not Initializing

1. Check the application logs for specific error messages
2. Ensure the Anthropic API key is valid and functioning
3. Verify that all required modules are imported correctly
4. Check for any syntax errors in the agent implementations

### Agents Not Communicating

1. Verify that the communication bus is properly initialized
2. Check that events are being published with the correct format
3. Ensure subscribers are properly registered for relevant event types
4. Look for any exceptions during message processing

### Training Not Improving Performance

1. Check that experiences are being properly recorded
2. Verify that the sampling mechanism is selecting relevant experiences
3. Ensure the training logic is properly updating agent behavior
4. Consider adjusting the training parameters (batch size, learning rate, etc.)

## References

- MCP Core Documentation (`utils/mcp_core.py`)
- Agent Army Integration Guide (`utils/mcp_army_integration.py`)
- Experience Replay Buffer Documentation (`utils/mcp_experience.py`)
- Agent Manager Reference (`utils/mcp_agent_manager.py`)
- Dashboard User Guide (`templates/mcp_army/dashboard.html`)