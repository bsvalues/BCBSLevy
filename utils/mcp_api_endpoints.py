"""
MCP API Endpoints utility module.

This module provides utility functions for the MCP Army API endpoints,
including helper functions for formatting responses and handling errors.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

# Setup logging
logger = logging.getLogger(__name__)

def format_agent_status(agent_id: str, status_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format agent status response for API consumption.
    
    Args:
        agent_id: The agent ID
        status_dict: The raw status dictionary from the agent manager
        
    Returns:
        Formatted agent status dictionary
    """
    # Ensure we have default values for expected fields
    performance = status_dict.get('performance', {})
    if not performance:
        performance = {
            'overall': 0.75,  # Default to 75% performance
            'task_success_rate': 0.8,
            'response_time': 500,  # ms
            'error_rate': 0.05
        }
    
    # Get agent role and domain if available
    role = status_dict.get('role', 'agent')
    domain = status_dict.get('domain', 'general')
    
    # Get agent capabilities
    capabilities = status_dict.get('capabilities', [])
    if not capabilities:
        # Provide default capabilities based on agent type
        if "coordinator" in agent_id:
            capabilities = [
                "execute_workflow_levy_compliance_audit",
                "execute_workflow_cross_district_analysis",
                "execute_workflow_historical_trend_forecasting",
                "execute_workflow_regulatory_compliance_check"
            ]
        elif "analysis" in agent_id:
            capabilities = [
                "analyze_levy_data",
                "validate_levy_calculations",
                "generate_compliance_report",
                "identify_optimization_opportunities"
            ]
        elif "prediction" in agent_id:
            capabilities = [
                "forecast_future_trends",
                "analyze_historical_patterns",
                "calculate_confidence_intervals",
                "generate_scenario_projections"
            ]
        else:
            capabilities = [
                "coordinate_agents",
                "integrate_information",
                "manage_workflows",
                "handle_assistance_requests"
            ]
    
    # Format the status response
    formatted_status = {
        "agent_id": agent_id,
        "status": {
            "status": status_dict.get('status', 'active'),
            "last_updated": status_dict.get('last_updated', datetime.now().isoformat()),
            "performance": performance,
            "message": status_dict.get('message', '')
        },
        "type": status_dict.get('type', 'agent'),
        "role": role,
        "domain": domain,
        "component": status_dict.get('component', 'default'),
        "capabilities": capabilities,
        "metadata": status_dict.get('metadata', {})
    }
    
    return formatted_status


def format_experience_stats(stats_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format experience statistics for API consumption.
    
    Args:
        stats_dict: The raw statistics dictionary from the collaboration manager
        
    Returns:
        Formatted experience statistics dictionary
    """
    # If no stats are provided, return a default set of statistics
    if not stats_dict:
        return {
            "total_experiences": 0,
            "utilization": 0.0,
            "most_recent": datetime.now().isoformat(),
            "by_agent": {},
            "by_event_type": {}
        }
    
    # Format the statistics
    formatted_stats = {
        "total_experiences": stats_dict.get('total_experiences', 0),
        "utilization": stats_dict.get('utilization', 0.0),
        "most_recent": stats_dict.get('most_recent', datetime.now().isoformat()),
        "by_agent": stats_dict.get('by_agent', {}),
        "by_event_type": stats_dict.get('by_event_type', {})
    }
    
    return formatted_stats


def format_command_structure(
    command_structure: Dict[str, Any], 
    agent_relationships: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Format command structure for API consumption.
    
    Args:
        command_structure: The raw command structure from the agent manager
        agent_relationships: The raw agent relationships from the agent manager
        
    Returns:
        Formatted command structure dictionary
    """
    if not command_structure:
        # Return a default command structure
        return {
            "command_structure": {
                "architect_prime": "workflow_coordinator",
                "integration_coordinator": "MCP",
                "component_leads": {
                    "levy": "levy_analysis"
                },
                "specialist_agents": {
                    "prediction": ["levy_prediction"]
                }
            },
            "agent_relationships": {}
        }
    
    # Format the command structure
    formatted_structure = {
        "command_structure": command_structure,
        "agent_relationships": agent_relationships
    }
    
    return formatted_structure


def handle_api_error(error: Exception, default_message: str = "An error occurred") -> Dict[str, Any]:
    """
    Handle API errors consistently.
    
    Args:
        error: The exception that occurred
        default_message: Default error message if none is provided
        
    Returns:
        Error response dictionary
    """
    logger.error(f"API Error: {str(error)}")
    
    # Extract error message
    error_message = str(error) if str(error) else default_message
    
    # Create error response
    error_response = {
        "error": error_message,
        "timestamp": datetime.now().isoformat()
    }
    
    return error_response


def generate_demo_experiences(agent_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Generate demo experience data for an agent.
    
    Args:
        agent_id: The agent ID to generate experiences for
        limit: Maximum number of experiences to generate
        
    Returns:
        List of experience dictionaries
    """
    # Different event types based on agent role
    event_types = ["task_completion", "collaboration", "learning", "error_recovery"]
    
    # Generate sample experiences
    experiences = []
    now = datetime.now()
    
    for i in range(min(limit, 10)):
        event_type = event_types[i % len(event_types)]
        timestamp = now.replace(minute=now.minute - i).isoformat()
        
        experience = {
            "id": f"exp_{agent_id}_{i}",
            "agentId": agent_id,
            "eventType": event_type,
            "timestamp": timestamp,
            "details": {
                "context": f"Sample {event_type} context",
                "outcome": "success" if i % 5 != 0 else "failure"
            }
        }
        
        experiences.append(experience)
    
    return experiences