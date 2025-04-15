"""
Routes for the MCP Army system.

This module defines the routes for interacting with the MCP Army system
through the web interface.
"""

import logging
from typing import Dict, Any, List

from flask import Flask, Blueprint, render_template, request, jsonify, current_app

def generate_command_structure_diagram(command_structure, agent_relationships):
    """
    Generate a mermaid diagram representing the command structure.
    
    Args:
        command_structure: The command structure dictionary
        agent_relationships: Dictionary of agent relationship information
        
    Returns:
        Mermaid diagram string
    """
    mermaid = ["graph TD;", "    %% Command Structure Diagram"]
    
    # Define node styles
    mermaid.append("    classDef architect fill:#f9d71c,stroke:#333,stroke-width:2px;")
    mermaid.append("    classDef coordinator fill:#66b2ff,stroke:#333,stroke-width:2px;")
    mermaid.append("    classDef lead fill:#ff9966,stroke:#333,stroke-width:1px;")
    mermaid.append("    classDef specialist fill:#99cc99,stroke:#333,stroke-width:1px;")
    
    # Add nodes for each command level
    architect_id = command_structure.get('architect_prime')
    if architect_id:
        mermaid.append(f"    ARCHITECT[\"{architect_id}<br>Architect Prime\"]:::architect;")
    
    coordinator_id = command_structure.get('integration_coordinator')
    if coordinator_id:
        mermaid.append(f"    COORDINATOR[\"{coordinator_id}<br>Integration Coordinator\"]:::coordinator;")
    
    # Add component leads
    for component, lead_id in command_structure.get('component_leads', {}).items():
        mermaid.append(f"    LEAD_{lead_id}[\"{lead_id}<br>Component Lead: {component}\"]:::lead;")
    
    # Add specialist agents
    for domain, agents in command_structure.get('specialist_agents', {}).items():
        for agent_id in agents:
            mermaid.append(f"    AGENT_{agent_id}[\"{agent_id}<br>Specialist: {domain}\"]:::specialist;")
    
    # Add connections based on reporting relationships
    for agent_id, relationship in agent_relationships.items():
        reports_to = relationship.get('reports_to')
        if reports_to:
            node1 = f"AGENT_{agent_id}" if relationship.get('role') == 'specialist_agent' else f"LEAD_{agent_id}" if relationship.get('role') == 'component_lead' else "COORDINATOR" if relationship.get('role') == 'integration_coordinator' else "ARCHITECT"
            node2 = f"AGENT_{reports_to}" if agent_relationships.get(reports_to, {}).get('role') == 'specialist_agent' else f"LEAD_{reports_to}" if agent_relationships.get(reports_to, {}).get('role') == 'component_lead' else "COORDINATOR" if agent_relationships.get(reports_to, {}).get('role') == 'integration_coordinator' else "ARCHITECT"
            mermaid.append(f"    {node1} --> {node2};")
    
    # Add top-level connections if not already covered by relationships
    if architect_id and coordinator_id:
        mermaid.append(f"    COORDINATOR --> ARCHITECT;")
    
    for component, lead_id in command_structure.get('component_leads', {}).items():
        if agent_relationships.get(lead_id, {}).get('reports_to') is None and coordinator_id:
            mermaid.append(f"    LEAD_{lead_id} --> COORDINATOR;")
    
    for domain, agents in command_structure.get('specialist_agents', {}).items():
        for agent_id in agents:
            if agent_relationships.get(agent_id, {}).get('reports_to') is None:
                component = agent_relationships.get(agent_id, {}).get('component')
                lead_id = command_structure.get('component_leads', {}).get(component)
                if lead_id:
                    mermaid.append(f"    AGENT_{agent_id} --> LEAD_{lead_id};")
                elif coordinator_id:
                    mermaid.append(f"    AGENT_{agent_id} --> COORDINATOR;")
    
    return "\n".join(mermaid)

from utils.mcp_army_init import (
    get_agent_manager, get_collaboration_manager, 
    get_master_prompt_manager_instance, init_mcp_army
)

# Setup logging
logger = logging.getLogger(__name__)

# Define blueprint
mcp_army_bp = Blueprint('mcp_army', __name__, url_prefix='/mcp-army')

# Direct access route for dashboard
@mcp_army_bp.route('/direct-dashboard')
def mcp_army_dashboard_direct():
    """Direct access to the MCP Army dashboard."""
    return dashboard()

@mcp_army_bp.route('/dashboard')
def dashboard():
    """Render the MCP Army dashboard."""
    try:
        agent_manager = get_agent_manager()
        if not agent_manager:
            return render_template('mcp_army/error.html', 
                                 error="MCP Army system not initialized")
        
        agents = agent_manager.list_agents()
        
        # Get command structure for hierarchical display
        command_structure = agent_manager.command_structure
        agent_relationships = agent_manager.agent_relationships
        
        # Generate mermaid diagram for command structure
        mermaid_diagram = generate_command_structure_diagram(command_structure, agent_relationships)
        
        return render_template('mcp_army/dashboard.html', 
                             agents=agents,
                             command_structure=command_structure,
                             agent_relationships=agent_relationships,
                             mermaid_diagram=mermaid_diagram)
    except Exception as e:
        logger.error(f"Error rendering MCP Army dashboard: {str(e)}")
        return render_template('simple_404.html', 
                             error_code=500,
                             error_title="System Error",
                             error_message=f"Error loading MCP Army dashboard: {str(e)}")

@mcp_army_bp.route('/api/command-structure')
def get_command_structure():
    """API endpoint to get the current command structure."""
    try:
        agent_manager = get_agent_manager()
        if not agent_manager:
            return jsonify({"error": "MCP Army system not initialized"}), 503
        
        # Import utility for formatting command structure
        from utils.mcp_api_endpoints import format_command_structure
        
        # Format the command structure for API consumption
        formatted_structure = format_command_structure(
            agent_manager.command_structure, 
            agent_manager.agent_relationships
        )
        
        return jsonify(formatted_structure)
    except Exception as e:
        logger.error(f"Error getting command structure: {str(e)}")
        from utils.mcp_api_endpoints import handle_api_error
        return jsonify(handle_api_error(e, "Error retrieving command structure")), 500

@mcp_army_bp.route('/api/agents')
def list_agents():
    """API endpoint to list all registered agents."""
    try:
        agent_manager = get_agent_manager()
        if not agent_manager:
            return jsonify({"error": "MCP Army system not initialized"}), 503
        
        agents_raw = agent_manager.list_agents()
        
        # Import utility for formatting agent status
        from utils.mcp_api_endpoints import format_agent_status
        
        # Format each agent in the list
        formatted_agents = []
        for agent in agents_raw:
            agent_id = agent.get('id', 'unknown')
            # Get detailed status for each agent
            status = agent_manager.get_agent_status(agent_id) or {}
            # Format the agent status
            formatted_agent = format_agent_status(agent_id, status)
            formatted_agents.append(formatted_agent)
        
        return jsonify({"agents": formatted_agents})
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        from utils.mcp_api_endpoints import handle_api_error
        return jsonify(handle_api_error(e, "Error retrieving agent list")), 500

@mcp_army_bp.route('/api/agents/<agent_id>')
def get_agent_status(agent_id):
    """API endpoint to get the status of a specific agent."""
    try:
        agent_manager = get_agent_manager()
        if not agent_manager:
            return jsonify({"error": "MCP Army system not initialized"}), 503
        
        status = agent_manager.get_agent_status(agent_id)
        if not status:
            return jsonify({"error": f"Agent {agent_id} not found"}), 404
            
        # Import utility for formatting agent status
        from utils.mcp_api_endpoints import format_agent_status
        
        # Format the agent status for API consumption
        formatted_status = format_agent_status(agent_id, status)
        
        return jsonify(formatted_status)
    except Exception as e:
        logger.error(f"Error getting agent status: {str(e)}")
        return jsonify({"error": str(e)}), 500

@mcp_army_bp.route('/api/agents/<agent_id>/capabilities/<capability>', methods=['POST'])
def execute_capability(agent_id, capability):
    """API endpoint to execute a capability on a specific agent."""
    try:
        agent_manager = get_agent_manager()
        if not agent_manager:
            return jsonify({"error": "MCP Army system not initialized"}), 503
        
        parameters = request.json or {}
        result = agent_manager.execute_capability(agent_id, capability, parameters)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error executing capability: {str(e)}")
        return jsonify({"error": str(e)}), 500

@mcp_army_bp.route('/api/agents/<agent_id>/assistance/<target_agent>', methods=['POST'])
def request_assistance(agent_id, target_agent):
    """API endpoint to request one agent to assist another."""
    try:
        agent_manager = get_agent_manager()
        if not agent_manager:
            return jsonify({"error": "MCP Army system not initialized"}), 503
        
        assistance_type = request.json.get('assistance_type', 'general')
        result = agent_manager.request_assistance(agent_id, target_agent, assistance_type)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error requesting assistance: {str(e)}")
        return jsonify({"error": str(e)}), 500

@mcp_army_bp.route('/api/experiences/stats')
def get_experience_stats():
    """API endpoint to get statistics about the experience replay buffer."""
    try:
        collaboration_manager = get_collaboration_manager()
        if not collaboration_manager:
            return jsonify({"error": "MCP Army system not initialized"}), 503
        
        # Get stats from the collaboration manager
        stats = collaboration_manager.get_experience_stats()
        
        # Import utility for formatting experience stats
        from utils.mcp_api_endpoints import format_experience_stats
        
        # Format the experience stats for API consumption
        formatted_stats = format_experience_stats(stats)
        
        return jsonify(formatted_stats)
    except Exception as e:
        logger.error(f"Error getting experience stats: {str(e)}")
        from utils.mcp_api_endpoints import handle_api_error
        return jsonify(handle_api_error(e, "Error retrieving experience statistics")), 500

@mcp_army_bp.route('/api/agents/<agent_id>/experiences')
def get_agent_experiences(agent_id):
    """API endpoint to get experiences for a specific agent."""
    try:
        collaboration_manager = get_collaboration_manager()
        if not collaboration_manager:
            return jsonify({"error": "MCP Army system not initialized"}), 503
        
        limit = request.args.get('limit', 10, type=int)
        
        try:
            # Try to get experiences from the collaboration manager
            experiences = collaboration_manager.get_agent_experiences(agent_id, limit)
        except Exception as inner_e:
            logger.warning(f"Could not retrieve experiences from collaboration manager: {str(inner_e)}")
            # Import utility for generating demo experiences
            from utils.mcp_api_endpoints import generate_demo_experiences
            # Generate demo experiences
            experiences = generate_demo_experiences(agent_id, limit)
        
        return jsonify({"agent_id": agent_id, "experiences": experiences})
    except Exception as e:
        logger.error(f"Error getting agent experiences: {str(e)}")
        from utils.mcp_api_endpoints import handle_api_error
        return jsonify(handle_api_error(e, f"Error retrieving experiences for agent {agent_id}")), 500

@mcp_army_bp.route('/api/training/start', methods=['POST'])
def start_training():
    """API endpoint to start a training cycle."""
    try:
        collaboration_manager = get_collaboration_manager()
        if not collaboration_manager:
            return jsonify({"error": "MCP Army system not initialized"}), 503
        
        batch_size = request.json.get('batch_size', 32)
        result = collaboration_manager.start_training_cycle(batch_size)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error starting training: {str(e)}")
        return jsonify({"error": str(e)}), 500

@mcp_army_bp.route('/api/initialize', methods=['POST'])
def initialize_mcp_army():
    """API endpoint to initialize the MCP Army system."""
    try:
        # Check if already initialized
        agent_manager = get_agent_manager()
        if agent_manager:
            return jsonify({"status": "already_initialized"}), 200
        
        # Initialize the MCP Army system
        init_successful = init_mcp_army(current_app)
        
        if init_successful:
            return jsonify({"status": "initialized"}), 200
        else:
            return jsonify({"error": "Initialization failed"}), 500
    except Exception as e:
        logger.error(f"Error initializing MCP Army system: {str(e)}")
        return jsonify({"error": str(e)}), 500

@mcp_army_bp.route('/api/master-prompt')
def get_master_prompt():
    """API endpoint to get the current master prompt."""
    try:
        master_prompt_manager = get_master_prompt_manager_instance()
        if not master_prompt_manager:
            return jsonify({"error": "Master Prompt Manager not initialized"}), 503
        
        prompt = master_prompt_manager.get_current_prompt()
        return jsonify(prompt)
    except Exception as e:
        logger.error(f"Error getting master prompt: {str(e)}")
        return jsonify({"error": str(e)}), 500

@mcp_army_bp.route('/api/master-prompt/directives/<directive_name>')
def get_master_prompt_directive(directive_name):
    """API endpoint to get a specific directive from the master prompt."""
    try:
        master_prompt_manager = get_master_prompt_manager_instance()
        if not master_prompt_manager:
            return jsonify({"error": "Master Prompt Manager not initialized"}), 503
        
        directive = master_prompt_manager.get_directive(directive_name)
        if not directive:
            return jsonify({"error": f"Directive {directive_name} not found"}), 404
            
        return jsonify(directive)
    except Exception as e:
        logger.error(f"Error getting directive {directive_name}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@mcp_army_bp.route('/api/master-prompt', methods=['PUT'])
def update_master_prompt():
    """API endpoint to update the master prompt."""
    try:
        master_prompt_manager = get_master_prompt_manager_instance()
        if not master_prompt_manager:
            return jsonify({"error": "Master Prompt Manager not initialized"}), 503
        
        new_prompt = request.json
        if not new_prompt:
            return jsonify({"error": "No prompt data provided"}), 400
            
        success = master_prompt_manager.update_prompt(new_prompt)
        if not success:
            return jsonify({"error": "Failed to update master prompt"}), 500
            
        return jsonify({"status": "updated", "version": new_prompt.get("version", "unknown")})
    except Exception as e:
        logger.error(f"Error updating master prompt: {str(e)}")
        return jsonify({"error": str(e)}), 500

@mcp_army_bp.route('/api/master-prompt/broadcast', methods=['POST'])
def broadcast_master_prompt():
    """API endpoint to manually broadcast the master prompt to all agents."""
    try:
        master_prompt_manager = get_master_prompt_manager_instance()
        if not master_prompt_manager:
            return jsonify({"error": "Master Prompt Manager not initialized"}), 503
            
        master_prompt_manager.broadcast_prompt()
        return jsonify({"status": "broadcast_completed"})
    except Exception as e:
        logger.error(f"Error broadcasting master prompt: {str(e)}")
        return jsonify({"error": str(e)}), 500

@mcp_army_bp.route('/api/workflows/collaborative', methods=['POST'])
def execute_collaborative_workflow():
    """API endpoint to execute a collaborative workflow."""
    try:
        agent_manager = get_agent_manager()
        if not agent_manager:
            return jsonify({"error": "MCP Army system not initialized"}), 503
        
        workflow_name = request.json.get('workflow_name')
        parameters = request.json.get('parameters', {})
        
        # Find the workflow coordinator agent
        coordinator_id = None
        for agent_info in agent_manager.list_agents():
            if 'workflow_coordinator' in agent_info.get('id', ''):
                coordinator_id = agent_info.get('id')
                break
                
        if not coordinator_id:
            return jsonify({"error": "Workflow coordinator agent not found"}), 404
            
        # Execute the workflow
        result = agent_manager.execute_capability(
            coordinator_id,
            f"execute_workflow_{workflow_name}",
            parameters
        )
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error executing collaborative workflow: {str(e)}")
        return jsonify({"error": str(e)}), 500

def register_mcp_army_routes(app):
    """Register the MCP Army routes with the Flask application."""
    try:
        app.register_blueprint(mcp_army_bp)
        logger.info("MCP Army routes registered")
        return True
    except Exception as e:
        logger.error(f"Error registering MCP Army routes: {str(e)}")
        return False