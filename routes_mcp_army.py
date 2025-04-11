"""
Routes for the MCP Army system.

This module defines the routes for interacting with the MCP Army system
through the web interface.
"""

import logging
from typing import Dict, Any, List

from flask import Blueprint, render_template, request, jsonify, current_app

from utils.mcp_army_init import (
    get_agent_manager, get_collaboration_manager, 
    get_master_prompt_manager_instance, init_mcp_army
)

# Setup logging
logger = logging.getLogger(__name__)

# Define blueprint
mcp_army_bp = Blueprint('mcp_army', __name__, url_prefix='/mcp-army')

@mcp_army_bp.route('/dashboard')
def dashboard():
    """Render the MCP Army dashboard."""
    try:
        agent_manager = get_agent_manager()
        if not agent_manager:
            return render_template('mcp_army/error.html', 
                                 error="MCP Army system not initialized")
        
        agents = agent_manager.list_agents()
        return render_template('mcp_army/dashboard.html', 
                             agents=agents)
    except Exception as e:
        logger.error(f"Error rendering MCP Army dashboard: {str(e)}")
        return render_template('simple_404.html', 
                             error_code=500,
                             error_title="System Error",
                             error_message=f"Error loading MCP Army dashboard: {str(e)}")

@mcp_army_bp.route('/api/agents')
def list_agents():
    """API endpoint to list all registered agents."""
    try:
        agent_manager = get_agent_manager()
        if not agent_manager:
            return jsonify({"error": "MCP Army system not initialized"}), 503
        
        agents = agent_manager.list_agents()
        return jsonify({"agents": agents})
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        return jsonify({"error": str(e)}), 500

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
            
        return jsonify({"agent_id": agent_id, "status": status})
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
        
        stats = collaboration_manager.get_experience_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting experience stats: {str(e)}")
        return jsonify({"error": str(e)}), 500

@mcp_army_bp.route('/api/agents/<agent_id>/experiences')
def get_agent_experiences(agent_id):
    """API endpoint to get experiences for a specific agent."""
    try:
        collaboration_manager = get_collaboration_manager()
        if not collaboration_manager:
            return jsonify({"error": "MCP Army system not initialized"}), 503
        
        limit = request.args.get('limit', 10, type=int)
        experiences = collaboration_manager.get_agent_experiences(agent_id, limit)
        return jsonify({"agent_id": agent_id, "experiences": experiences})
    except Exception as e:
        logger.error(f"Error getting agent experiences: {str(e)}")
        return jsonify({"error": str(e)}), 500

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