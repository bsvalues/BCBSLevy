"""
Example routes to demonstrate the new TerraFusion UI components and workflows.

This module provides example implementations of the unified UI component system
to showcase best practices for creating consistent user experiences.
"""

from flask import Blueprint, render_template, current_app

# Create the examples blueprint
examples_bp = Blueprint('examples', __name__, url_prefix='/examples')

@examples_bp.route('/workflow')
def workflow_example():
    """
    Render the workflow example page that demonstrates the unified workflow system.
    """
    return render_template(
        'workflow-example.html', 
        active_page="Workflow Example",
        workflow_context="Demonstration",
        breadcrumbs=[
            ("Examples", "/examples"),
            ("Workflow Example", "/examples/workflow")
        ]
    )

@examples_bp.route('/components')
def components_example():
    """
    Render the components example page that showcases all available UI components.
    """
    return render_template(
        'components-example.html', 
        active_page="Components Gallery",
        breadcrumbs=[
            ("Examples", "/examples"),
            ("Components Gallery", "/examples/components")
        ]
    )

def init_example_routes(app):
    """
    Register example routes with the Flask app.
    """
    app.register_blueprint(examples_bp)
    app.logger.info('Example routes registered')