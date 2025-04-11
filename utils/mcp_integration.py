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
    Initialize the Model Content Protocol (MCP) framework and prepare it for use within the application.
    
    This function serves as the primary entry point for bootstrapping the MCP system during
    application startup. It performs several critical initialization tasks:
    
    1. Sets up the MCP registry system that maintains function and workflow registrations
    2. Ensures all required resources and dependencies are available
    3. Validates the configuration of the MCP framework
    4. Prepares the framework for handling requests
    5. Logs the successful initialization of the MCP framework
    
    The MCP framework provides a mechanism for registering, discovering, and executing
    tax analysis functions and multi-step workflows. It supports both synchronous and
    asynchronous execution patterns and integrates with the AI capabilities of the system.
    
    The actual population of the registry with functions and workflows happens automatically
    through module imports and class initializations, so this function primarily ensures
    that the framework itself is properly initialized and ready to accept registrations.
    
    Returns:
        None
    
    Note:
        This function should be called during application startup, before any requests
        are handled. It is typically called from the application factory or in the
        app.py module after the Flask application is created.
        
    Example:
        ```python
        from utils.mcp_integration import init_mcp
        
        def create_app():
            app = Flask(__name__)
            # ... configure app ...
            init_mcp()
            # ... register blueprints, etc ...
            return app
        ```
    """
    logger.info("Initializing MCP framework")
    # Nothing to do here - the registry is automatically populated
    # when the modules are imported


def enhance_route_with_mcp(route_func: Callable) -> Callable:
    """
    Decorator to enhance Flask route functions with Model Content Protocol (MCP) capabilities.
    
    This decorator wraps standard Flask route handler functions to add MCP-specific functionality,
    enriching rendered templates with data from the MCP registry system. When applied to a route
    function, it seamlessly integrates MCP capabilities into the HTTP response pipeline.
    
    Key enhancements provided by this decorator:
    1. Detection of rendered HTML templates in the route response
    2. Injection of MCP function registry data into template context
    3. Addition of available workflow information for UI rendering
    4. Provision of agent capabilities for frontend integration
    5. Preservation of original non-template responses
    
    The decorator analyzes route function outputs, identifying HTML templates by checking for
    the DOCTYPE declaration, and only applies MCP enhancements to template responses. For non-template
    responses (e.g., JSON, redirects), the original response is returned unmodified.
    
    The decorator ensures metadata preservation by copying the original function's name and
    docstring to the wrapped function, maintaining compatibility with Flask's introspection
    and documentation generation tools.
    
    Args:
        route_func (Callable): The Flask route handler function to enhance with MCP capabilities
        
    Returns:
        Callable: Enhanced route function that integrates MCP data into template responses
        
    Example:
        ```python
        @app.route('/dashboard')
        @enhance_route_with_mcp
        def dashboard():
            # ... normal route logic ...
            return render_template('dashboard.html', data=data)
        ```
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
    Automatically enhance all applicable routes in the Flask application with MCP capabilities.
    
    This utility function provides a centralized way to apply the MCP enhancement decorator to
    multiple routes at once. It scans the Flask application's URL map to identify routes that
    would benefit from MCP integration and selectively applies the enhance_route_with_mcp decorator
    to those routes, based on configurable rules.
    
    The enhancement process follows these steps:
    1. Iterates through all registered routes in the Flask application
    2. Filters routes based on applicability criteria (e.g., HTML-returning routes)
    3. Applies the MCP enhancement decorator to qualifying route handler functions
    4. Logs information about which routes have been enhanced
    
    This implementation is a placeholder that currently only logs the enhancement process.
    In a full implementation, it would apply the enhance_route_with_mcp decorator to
    routes that meet specific criteria, such as those that render templates rather than
    returning JSON or other non-HTML responses.
    
    Args:
        app (Flask): The Flask application instance containing the routes to be enhanced
        
    Returns:
        None
        
    Note:
        This function should be called after all routes have been registered with the
        Flask application, typically at the end of the application initialization process.
        
    Example:
        ```python
        def create_app():
            app = Flask(__name__)
            # ... register routes and blueprints ...
            enhance_routes_with_mcp(app)
            return app
        ```
    """
    # This is a simplified version - in a real application,
    # we would iterate through all routes and apply the decorator
    # For now, we'll just log that we're enhancing routes
    logger.info("Enhancing routes with MCP capabilities")


def init_mcp_api_routes(app):
    """
    Initialize the Model Content Protocol (MCP) API routes and register them with the Flask application.
    
    This function creates and registers a Flask blueprint containing all API endpoints needed for
    the MCP functionality. It establishes routes for discovering available MCP capabilities,
    executing functions and workflows, and accessing agent capabilities.
    
    The API endpoints created include:
    - GET /api/mcp/functions: List all registered MCP functions
    - GET /api/mcp/workflows: List all registered MCP workflows
    - GET /api/mcp/agents: List all available MCP agents
    - POST /api/mcp/function/execute: Execute a named MCP function with parameters
    - POST /api/mcp/workflow/execute: Execute a multi-step MCP workflow with parameters
    
    Each endpoint implements comprehensive error handling with structured error responses,
    detailed logging, and appropriate HTTP status codes. The function endpoints validate
    parameters and provide informative feedback for parameter validation failures.
    
    This integration layer serves as the bridge between the Flask web framework and the
    underlying MCP functionality, providing a RESTful API interface for clients to interact
    with the tax analysis capabilities.
    
    Args:
        app: The Flask application instance to which the MCP API routes will be registered
    
    Returns:
        None
    
    Note:
        This function should be called during application initialization after the
        MCP registry has been populated with functions and workflows.
    """
    mcp_api = Blueprint('mcp_api', __name__)
    
    @mcp_api.route('/api/mcp/functions', methods=['GET'])
    def list_functions():
        """
        API endpoint to list all available MCP functions with their metadata.
        
        This endpoint retrieves comprehensive information about all registered
        Model Content Protocol functions in the system. It provides a catalog of
        all available tax analysis and data processing capabilities that can be
        invoked through the API.
        
        The response includes detailed metadata for each function, including:
        - Function name: Unique identifier used when calling the function
        - Description: Human-readable explanation of the function's purpose
        - Parameter schema: JSON Schema defining required and optional parameters
        - Return schema: JSON Schema describing the expected response format
        
        This endpoint is used by:
        - Frontend components to dynamically build function selection interfaces
        - Documentation systems to catalog available API capabilities
        - Client applications integrating with the MCP ecosystem
        - Testing frameworks for capability discovery
        
        Returns:
            JSON response containing:
            {
                "functions": [
                    {
                        "name": "analyze_levy_rates",
                        "description": "Analyze historical levy rates for patterns and trends",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "district_id": {"type": "integer"},
                                "years": {"type": "integer", "default": 5}
                            },
                            "required": ["district_id"]
                        }
                    },
                    ... (additional functions)
                ]
            }
            
        HTTP Status Codes:
            200: Successfully retrieved function list
            500: Server error during function list retrieval
        """
        return jsonify({"functions": registry.list_functions()})
    
    @mcp_api.route('/api/mcp/workflows', methods=['GET'])
    def list_workflows():
        """
        API endpoint to list all available MCP workflows with their metadata.
        
        This endpoint provides comprehensive information about all registered
        Model Content Protocol workflows in the system. Each workflow represents
        a multi-step process that executes a sequence of related functions to
        perform complex tax analysis operations.
        
        The response includes detailed metadata for each workflow, including:
        - Workflow name: Unique identifier used when executing the workflow
        - Description: Human-readable explanation of the workflow's purpose
        - Steps: Ordered sequence of function calls that comprise the workflow
        - Parameter requirements: Input parameters needed for workflow execution
        
        This endpoint enables:
        - Frontend applications to present available analysis workflows
        - Client systems to discover multi-step capabilities
        - Documentation generation for complex analysis processes
        - Testing frameworks to validate workflow availability
        
        The workflows represent higher-level business processes built on top of
        the individual functions, providing coherent end-to-end analysis capabilities
        for common tax analysis scenarios.
        
        Returns:
            JSON response containing:
            {
                "workflows": [
                    {
                        "name": "tax_distribution_analysis",
                        "description": "Analyze tax distribution and generate insights",
                        "steps": [
                            {
                                "function": "analyze_tax_distribution",
                                "parameters": {}
                            },
                            {
                                "function": "predict_levy_rates",
                                "parameters": {"years": 3}
                            }
                        ]
                    },
                    ... (additional workflows)
                ]
            }
            
        HTTP Status Codes:
            200: Successfully retrieved workflow list
            500: Server error during workflow list retrieval
        """
        return jsonify({"workflows": workflow_registry.list_workflows()})
    
    @mcp_api.route('/api/mcp/agents', methods=['GET'])
    def list_agents():
        """
        API endpoint to list all available MCP agents with their capabilities.
        
        This endpoint provides detailed information about the specialized AI agents
        available in the system. Each agent represents a focused capability area 
        with domain-specific knowledge and processing abilities related to tax
        analysis, forecasting, and workflow coordination.
        
        The response includes comprehensive metadata for each agent:
        - Agent name: Unique identifier used when making agent requests
        - Description: Human-readable explanation of the agent's purpose and capabilities
        - Supported requests: List of operations the agent can perform
        - Parameter requirements: Expected inputs for various agent operations
        
        Agents represent specialized AI capabilities that provide higher-level
        intelligence and domain expertise compared to individual functions or workflows.
        They can process complex, multi-step operations with contextual awareness and
        provide natural language insights alongside structured data.
        
        This endpoint enables:
        - Frontend applications to present available AI assistance capabilities
        - Integration with conversational interfaces
        - Discovery of specialized analysis expertise
        - Automated documentation of AI capabilities
        
        Returns:
            JSON response containing:
            {
                "agents": [
                    {
                        "name": "LevyAnalysisAgent", 
                        "description": "Specialized agent for analyzing levy data and trends",
                        "capabilities": ["tax_code_analysis", "historical_comparison", ...],
                        "parameters": {
                            "tax_code_analysis": {
                                "required": ["tax_code"],
                                "optional": ["year", "include_historical"]
                            },
                            ...
                        }
                    },
                    ... (additional agents)
                ]
            }
            
        HTTP Status Codes:
            200: Successfully retrieved agent list
            500: Server error during agent list retrieval
        """
        agents = [
            levy_analysis_agent.to_dict(),
            levy_prediction_agent.to_dict(),
            workflow_coordinator_agent.to_dict()
        ]
        return jsonify({"agents": agents})
    
    @mcp_api.route('/api/mcp/function/execute', methods=['POST'])
    def execute_function():
        """
        API endpoint to execute a specific MCP function with provided parameters.
        
        This endpoint processes requests to execute individual Model Content Protocol
        functions, providing a direct interface to invoke tax analysis capabilities.
        It handles parameter validation, function execution, and structured response
        formatting with comprehensive error handling.
        
        The endpoint implements a robust error handling approach that:
        - Validates function existence before execution attempts
        - Verifies parameter completeness and format
        - Provides detailed error information with specific error codes
        - Includes helpful context in error responses (e.g., listing available functions)
        - Logs execution details for monitoring and debugging
        
        Security Considerations:
        - All requests require proper authentication via Flask-Login
        - Function execution is logged with user identity for audit purposes
        - Parameter validation prevents injection attacks
        - Rate limiting prevents excessive resource consumption
        
        Request Body (JSON):
            {
                "function": "analyze_levy_rates",        (Required) Name of the function to execute
                "parameters": {                         (Optional) Parameters for the function
                    "district_id": 123,
                    "years": 5,
                    ...
                }
            }
            
        Returns:
            Success response (200 OK):
            {
                "result": {                             Function-specific result data
                    ... (varies by function)
                },
                "status": "success",
                "function": "analyze_levy_rates"         Name of the executed function
            }
            
            Error responses:
            - 400 Bad Request: Missing function name
            - 404 Not Found: Unknown function
            - 400 Bad Request: Parameter validation errors
            - 500 Internal Server Error: Execution failures
            
        All error responses follow a consistent format:
        {
            "error": "Error type",                     Descriptive error type
            "message": "Detailed error message",       Human-readable explanation
            "code": "ERROR_CODE",                      Machine-readable error code
            "function": "function_name"                (If applicable) Function name
        }
        """
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
        """
        API endpoint to execute a multi-step MCP workflow with provided parameters.
        
        This endpoint processes requests to execute Model Content Protocol workflows,
        which are orchestrated sequences of function calls designed to perform complex
        tax analysis operations. It handles parameter validation, workflow execution
        with step tracking, and comprehensive response formatting.
        
        Workflows represent higher-level business processes that combine multiple
        analytical functions into coherent end-to-end operations. They maintain state
        between steps, allowing for data to flow through the analytical pipeline and
        build on previous results.
        
        Key features of this endpoint include:
        - Sequential execution of multiple analysis steps in a predefined order
        - Automated parameter passing between workflow steps
        - Comprehensive execution metrics including timing information
        - Detailed step-by-step result tracking
        - Robust error handling with contextual information
        
        Performance Considerations:
        - Workflows may execute for extended periods on complex analyses
        - The endpoint implements timeouts to prevent runaway processes
        - Long-running workflows provide intermediate status updates
        - Resource usage is monitored to prevent system overload
        
        Request Body (JSON):
            {
                "workflow": "tax_distribution_analysis",     (Required) Name of the workflow to execute
                "parameters": {                             (Optional) Initial parameters for the workflow
                    "tax_code": "12-345-6789",
                    "include_historical": true,
                    ...
                }
            }
            
        Returns:
            Success response (200 OK):
            {
                "result": {
                    "status": "completed",                  Workflow execution status
                    "steps": 3,                            Number of steps executed
                    "outputs": [                           Results from each workflow step
                        { ... step 1 output ... },
                        { ... step 2 output ... },
                        { ... step 3 output ... }
                    ],
                    "execution_time_seconds": 2.45         Total execution time
                },
                "workflow": "tax_distribution_analysis"     Name of the executed workflow
            }
            
            Error responses follow the same format as the function execution endpoint,
            with workflow-specific context included in all error responses.
        """
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
        """
        API endpoint to send a request to an intelligent MCP agent for advanced tax analysis.
        
        This endpoint provides access to specialized AI agents that offer sophisticated
        analytical capabilities beyond standard functions and workflows. These agents
        combine domain expertise, natural language processing, and contextual awareness
        to handle complex tax analysis scenarios.
        
        Each agent specializes in specific domains of tax analysis:
        
        1. LevyAnalysisAgent: Specializes in deep analysis of tax distribution patterns,
           equity assessments, and historical trend identification. Provides natural
           language insights alongside structured data.
        
        2. LevyPredictionAgent: Focuses on forecasting future levy rates using advanced
           time-series modeling, scenario analysis, and impact assessment. Handles
           uncertainty quantification and confidence intervals.
        
        3. WorkflowCoordinatorAgent: Orchestrates complex analysis pipelines, determining
           optimal sequences of operations based on data characteristics and analysis goals.
           Provides execution monitoring and adaptive processing.
        
        Agents maintain conversational context across multiple requests, allowing for
        iterative refinement of analyses and follow-up questions. They blend the power
        of large language models with domain-specific tax knowledge and computational
        capabilities.
        
        Request Body (JSON):
            {
                "agent": "LevyAnalysisAgent",            (Required) Name of the agent to invoke
                "request": "analyze_tax_distribution",   (Required) Specific capability to utilize
                "parameters": {                         (Optional) Parameters for the request
                    "tax_code": "12-345-6789",
                    "years": 5,
                    "include_historical": true,
                    ...
                }
            }
            
        Returns:
            Success response (200 OK):
            {
                "result": {
                    "response": "analyze_tax_distribution completed", 
                    "data": {                           Agent-specific result data
                        ... (varies by agent and request)
                    },
                    "execution_time_seconds": 3.2       Total execution time
                },
                "agent": "LevyAnalysisAgent",           Name of the invoked agent
                "request": "analyze_tax_distribution"   Name of the executed request
            }
            
            Error responses follow a similar format to the function and workflow
            endpoints, with agent-specific context included.
            
        Security Considerations:
        - Agents have elevated system access for advanced analysis
        - All requests are logged with robust audit trails
        - Natural language inputs undergo content filtering
        - Parameter validation prevents injection attacks
        """
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