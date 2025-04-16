"""
MCP Agent UI Routes for the LevyMaster application.

This module provides routes for MCP Agent UI features including
the agent registry, workflow designer, and agent playground.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for

# Create blueprints for the MCP UI routes
mcp_ui_bp = Blueprint('mcp_ui', __name__, url_prefix='/mcp')

@mcp_ui_bp.route('/agent-registry')
def agent_registry():
    """Render the Agent Registry page."""
    return render_template('mcp/agent_registry.html', page_title="Agent Registry")

@mcp_ui_bp.route('/workflow-designer')
def workflow_designer():
    """Render the Workflow Designer page."""
    return render_template('mcp/workflow_designer.html', page_title="Workflow Designer")

@mcp_ui_bp.route('/agent-playground')
def agent_playground():
    """Render the Agent Playground page."""
    return render_template('mcp/agent_playground.html', page_title="Agent Playground")

def register_mcp_ui_routes(app):
    """Register MCP UI routes with the app."""
    app.register_blueprint(mcp_ui_bp)
    app.logger.info("MCP UI routes registered")