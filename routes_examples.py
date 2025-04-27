"""
Example routes to demonstrate the unified UI components and workflows.

This module provides routes for example pages that showcase the unified
TerraFusion UI components, design patterns, and workflow implementations.
"""

from flask import Blueprint, render_template, current_app, url_for

# Create blueprint with a unique name
examples_bp = Blueprint('examples_ui', __name__, url_prefix='/examples')

@examples_bp.route('/workflow')
def workflow_example():
    """Show an example workflow using the unified UI components."""
    return render_template(
        'workflow-example.html',
        active_page='Example Workflow',
        workflow_context='Demo Workflow',
        breadcrumbs=[
            ('Examples', url_for('examples_ui.components')),
            ('Workflow Example', '#')
        ]
    )

@examples_bp.route('/components')
def components():
    """Show the components gallery with all UI component examples."""
    return render_template(
        'components-example.html',
        active_page='UI Components',
        breadcrumbs=[
            ('Examples', '#'),
            ('Components Gallery', '#')
        ]
    )

@examples_bp.route('/dashboard')
def dashboard_example():
    """Show an example dashboard using the unified UI components."""
    return render_template(
        'dashboard-example.html',
        active_page='Example Dashboard',
        breadcrumbs=[
            ('Examples', url_for('examples_ui.components')),
            ('Dashboard Example', '#')
        ]
    )

def init_example_routes(app):
    """Initialize example routes with the Flask application."""
    # Check if the blueprint is already registered to avoid duplicates
    if 'examples_ui' not in app.blueprints:
        app.register_blueprint(examples_bp)
        app.logger.info('Example routes initialized')
    else:
        app.logger.info('Example routes already initialized')