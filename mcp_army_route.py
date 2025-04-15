"""
Direct route module for MCP Army dashboard.

This module provides a direct route to the MCP Army dashboard,
bypassing any blueprint registration issues.
"""

import logging
from typing import Dict, Any, List

# Import Flask components 
from flask import Flask, render_template, request, jsonify, current_app, redirect

from utils.mcp_army_init import (
    get_agent_manager, get_collaboration_manager, 
    get_master_prompt_manager_instance, init_mcp_army
)

# Setup logging
logger = logging.getLogger(__name__)

# Define route
def mcp_army_dashboard_direct():
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
        from routes_mcp_army import generate_command_structure_diagram
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

def register_direct_routes(app):
    """Register the direct route for MCP Army dashboard."""
    try:
        # Register both URL patterns to ensure accessibility
        app.add_url_rule('/mcp-army-dashboard', 'mcp_army_dashboard_direct', mcp_army_dashboard_direct)
        app.add_url_rule('/mcp-army/dashboard', 'mcp_army_dashboard', mcp_army_dashboard_direct)
        app.add_url_rule('/agent-dashboard', 'agent_dashboard', lambda: redirect('/mcp-army/dashboard'))
        
        logger.info("Direct MCP Army dashboard routes registered")
        return True
    except Exception as e:
        logger.error(f"Error registering direct MCP Army dashboard route: {str(e)}")
        return False