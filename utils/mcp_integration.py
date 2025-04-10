"""
Model Content Protocol (MCP) integration with Flask routes.

This module provides functionality for integrating MCP capabilities into the Flask application,
including route enhancement and API endpoints.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Callable, Optional

from flask import Blueprint, request, jsonify, current_app, render_template

from utils.mcp_core import registry, workflow_registry
from utils.mcp_agents import (
    levy_analysis_agent,
    levy_prediction_agent,
    workflow_coordinator_agent
)

logger = logging.getLogger(__name__)


def init_mcp():
    """
    Initialize the MCP framework.
    
    This function should be called during application startup.
    """
    logger.info("Initializing MCP framework")
    # Nothing to do here - the registry is automatically populated
    # when the modules are imported


def enhance_route_with_mcp(route_func: Callable) -> Callable:
    """
    Decorator to enhance a route with MCP capabilities.
    
    Args:
        route_func: The route function to enhance
        
    Returns:
        Enhanced route function
    """
    def enhanced_route(*args, **kwargs):
        # Execute the original route function
        result = route_func(*args, **kwargs)
        
        # If the result is a rendered template, add MCP capabilities
        if isinstance(result, str) and "<!DOCTYPE html>" in result:
            # Extract MCP data for the template
            # This is a simplified example - in a real application,
            # this would extract relevant data from the request/context
            mcp_data = {
                "available_functions": registry.list_functions(),
                "available_workflows": workflow_registry.list_workflows(),
                "available_agents": [
                    levy_analysis_agent.to_dict(),
                    levy_prediction_agent.to_dict(),
                    workflow_coordinator_agent.to_dict()
                ]
            }
            
            # This is a placeholder - in a real application, we would
            # inject the MCP data into the template context
            # For now, we'll just return the original result
            return result
        
        return result
    
    # Preserve the original function's metadata
    enhanced_route.__name__ = route_func.__name__
    enhanced_route.__doc__ = route_func.__doc__
    
    return enhanced_route


def enhance_routes_with_mcp(app):
    """
    Enhance all routes in the application with MCP capabilities.
    
    Args:
        app: Flask application
    """
    # This is a simplified version - in a real application,
    # we would iterate through all routes and apply the decorator
    # For now, we'll just log that we're enhancing routes
    logger.info("Enhancing routes with MCP capabilities")


def init_mcp_api_routes(app):
    """
    Initialize MCP API routes.
    
    Args:
        app: Flask application
    """
    mcp_api = Blueprint('mcp_api', __name__)
    
    @mcp_api.route('/api/mcp/functions', methods=['GET'])
    def list_functions():
        """API endpoint to list available MCP functions."""
        return jsonify({"functions": registry.list_functions()})
    
    @mcp_api.route('/api/mcp/workflows', methods=['GET'])
    def list_workflows():
        """API endpoint to list available MCP workflows."""
        return jsonify({"workflows": workflow_registry.list_workflows()})
    
    @mcp_api.route('/api/mcp/agents', methods=['GET'])
    def list_agents():
        """API endpoint to list available MCP agents."""
        agents = [
            levy_analysis_agent.to_dict(),
            levy_prediction_agent.to_dict(),
            workflow_coordinator_agent.to_dict()
        ]
        return jsonify({"agents": agents})
    
    @mcp_api.route('/api/mcp/function/execute', methods=['POST'])
    def execute_function():
        """API endpoint to execute an MCP function."""
        data = request.json
        if not data or 'function' not in data:
            logger.warning("Invalid MCP function request: missing function name")
            return jsonify({
                "error": "Invalid request", 
                "message": "Missing function name",
                "code": "MISSING_FUNCTION_NAME"
            }), 400
        
        function_name = data['function']
        parameters = data.get('parameters', {})
        
        # Check if function exists in registry
        if not registry.has_function(function_name):
            logger.warning(f"Attempt to execute unknown function: {function_name}")
            return jsonify({
                "error": "Unknown function", 
                "message": f"Function '{function_name}' is not registered",
                "code": "UNKNOWN_FUNCTION",
                "available_functions": registry.list_functions()
            }), 404
        
        try:
            logger.info(f"Executing MCP function: {function_name} with params: {parameters}")
            result = registry.execute_function(function_name, parameters)
            return jsonify({
                "result": result, 
                "status": "success",
                "function": function_name
            })
        except ValueError as e:
            # Parameter validation errors
            logger.error(f"Parameter validation error in function {function_name}: {str(e)}")
            return jsonify({
                "error": "Parameter validation failed", 
                "message": str(e),
                "code": "INVALID_PARAMETERS",
                "function": function_name
            }), 400
        except KeyError as e:
            # Missing required parameter
            logger.error(f"Missing required parameter in function {function_name}: {str(e)}")
            return jsonify({
                "error": "Missing required parameter", 
                "message": f"Missing required parameter: {str(e)}",
                "code": "MISSING_PARAMETER",
                "function": function_name
            }), 400
        except Exception as e:
            # General execution errors
            logger.error(f"Error executing function {function_name}: {str(e)}")
            return jsonify({
                "error": "Function execution failed", 
                "message": str(e),
                "code": "EXECUTION_ERROR",
                "function": function_name
            }), 500
    
    @mcp_api.route('/api/mcp/workflow/execute', methods=['POST'])
    def execute_workflow():
        """API endpoint to execute an MCP workflow."""
        data = request.json
        if not data or 'workflow' not in data:
            logger.warning("Invalid MCP workflow request: missing workflow name")
            return jsonify({
                "error": "Invalid request", 
                "message": "Missing workflow name",
                "code": "MISSING_WORKFLOW_NAME"
            }), 400
        
        workflow_name = data['workflow']
        parameters = data.get('parameters', {})
        
        # Check if workflow exists in registry
        if not workflow_registry.has_workflow(workflow_name):
            logger.warning(f"Attempt to execute unknown workflow: {workflow_name}")
            return jsonify({
                "error": "Unknown workflow", 
                "message": f"Workflow '{workflow_name}' is not registered",
                "code": "UNKNOWN_WORKFLOW",
                "available_workflows": workflow_registry.list_workflows()
            }), 404
            
        try:
            logger.info(f"Executing MCP workflow: {workflow_name} with params: {parameters}")
            start_time = datetime.now()
            results = workflow_registry.execute_workflow(workflow_name, parameters)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Workflow {workflow_name} completed in {execution_time:.2f}s with {len(results)} steps")
            return jsonify({
                "result": {
                    "status": "completed", 
                    "steps": len(results), 
                    "outputs": results,
                    "execution_time_seconds": round(execution_time, 2)
                },
                "workflow": workflow_name
            })
        except ValueError as e:
            # Parameter validation errors
            logger.error(f"Parameter validation error in workflow {workflow_name}: {str(e)}")
            return jsonify({
                "error": "Parameter validation failed", 
                "message": str(e),
                "code": "INVALID_PARAMETERS",
                "workflow": workflow_name
            }), 400 
        except KeyError as e:
            # Missing required parameter
            logger.error(f"Missing required parameter in workflow {workflow_name}: {str(e)}")
            return jsonify({
                "error": "Missing required parameter", 
                "message": f"Missing required parameter: {str(e)}",
                "code": "MISSING_PARAMETER",
                "workflow": workflow_name
            }), 400
        except Exception as e:
            # General execution errors
            logger.error(f"Error executing workflow {workflow_name}: {str(e)}")
            return jsonify({
                "error": "Workflow execution failed", 
                "message": str(e),
                "code": "EXECUTION_ERROR",
                "workflow": workflow_name
            }), 500
    
    @mcp_api.route('/api/mcp/agent/request', methods=['POST'])
    def agent_request():
        """API endpoint to send a request to an MCP agent."""
        data = request.json
        if not data or 'agent' not in data:
            logger.warning("Invalid MCP agent request: missing agent name")
            return jsonify({
                "error": "Invalid request", 
                "message": "Missing agent name",
                "code": "MISSING_AGENT_NAME"
            }), 400
            
        if 'request' not in data:
            logger.warning("Invalid MCP agent request: missing request name")
            return jsonify({
                "error": "Invalid request", 
                "message": "Missing request name",
                "code": "MISSING_REQUEST_NAME"
            }), 400
        
        agent_name = data['agent']
        request_name = data['request']
        parameters = data.get('parameters', {})
        
        # Get the appropriate agent
        available_agents = {
            "LevyAnalysisAgent": levy_analysis_agent,
            "LevyPredictionAgent": levy_prediction_agent,
            "WorkflowCoordinatorAgent": workflow_coordinator_agent
        }
        
        if agent_name not in available_agents:
            logger.warning(f"Attempt to access unknown agent: {agent_name}")
            return jsonify({
                "error": "Unknown agent", 
                "message": f"Agent '{agent_name}' is not registered",
                "code": "UNKNOWN_AGENT",
                "available_agents": list(available_agents.keys())
            }), 404
            
        agent = available_agents[agent_name]
            
        try:
            logger.info(f"Executing agent request: {agent_name}/{request_name} with params: {parameters}")
            start_time = datetime.now()
            result = agent.handle_request(request_name, parameters)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Agent request {agent_name}/{request_name} completed in {execution_time:.2f}s")
            return jsonify({
                "result": {
                    "response": f"{request_name} completed", 
                    "data": result,
                    "execution_time_seconds": round(execution_time, 2)
                },
                "agent": agent_name,
                "request": request_name
            })
        except ValueError as e:
            # Parameter validation errors
            logger.error(f"Parameter validation error in agent request {agent_name}/{request_name}: {str(e)}")
            return jsonify({
                "error": "Parameter validation failed", 
                "message": str(e),
                "code": "INVALID_PARAMETERS",
                "agent": agent_name,
                "request": request_name
            }), 400
        except KeyError as e:
            # Missing required parameter
            logger.error(f"Missing required parameter in agent request {agent_name}/{request_name}: {str(e)}")
            return jsonify({
                "error": "Missing required parameter", 
                "message": f"Missing required parameter: {str(e)}",
                "code": "MISSING_PARAMETER",
                "agent": agent_name,
                "request": request_name
            }), 400
        except Exception as e:
            # General execution errors
            logger.error(f"Error executing agent request {agent_name}/{request_name}: {str(e)}")
            return jsonify({
                "error": "Agent request failed", 
                "message": str(e),
                "code": "EXECUTION_ERROR",
                "agent": agent_name,
                "request": request_name
            }), 500
    
    app.register_blueprint(mcp_api)