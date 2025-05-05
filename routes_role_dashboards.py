"""
Role-based dashboard routes for the TerraLevy platform.

This module provides routes for role-specific dashboards, implementing
the multi-stage certification workflow as specified in the product requirements.

Roles:
- Clerk: Data management and initial entry
- Deputy: Review and verification
- Assessor: Final certification and approval
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required

# Create blueprint
role_dashboards_bp = Blueprint('role_dashboards', __name__, url_prefix='/role-dashboards')

# Configure logger
logger = logging.getLogger(__name__)


@role_dashboards_bp.route('/')
@login_required
def index():
    """
    Main role dashboards landing page.
    
    Redirects to the appropriate dashboard based on the user's role,
    or to the main dashboard if they have no specific role.
    """
    # Check user roles and redirect accordingly
    if current_user.has_role('assessor'):
        return redirect(url_for('role_dashboards.assessor_dashboard'))
    elif current_user.has_role('deputy'):
        return redirect(url_for('role_dashboards.deputy_dashboard'))
    elif current_user.has_role('clerk'):
        return redirect(url_for('role_dashboards.clerk_dashboard'))
    else:
        flash('You do not have any specialized roles assigned.', 'info')
        return redirect(url_for('home.index'))


@role_dashboards_bp.route('/clerk')
@login_required
def clerk_dashboard():
    """
    Clerk dashboard - focused on data management and initial data entry.
    
    This dashboard provides interfaces for:
    - Importing data from external sources
    - Validating imported data
    - Running data quality checks
    - Preparing data for deputy review
    """
    if not current_user.has_role('clerk') and not current_user.is_admin:
        flash('You do not have permission to access the Clerk dashboard.', 'warning')
        return redirect(url_for('home.index'))
    
    logger.info(f"User {current_user.username} accessed Clerk dashboard")
    return render_template('role_dashboards/clerk_dashboard.html')


@role_dashboards_bp.route('/deputy')
@login_required
def deputy_dashboard():
    """
    Deputy dashboard - focused on review and verification.
    
    This dashboard provides interfaces for:
    - Reviewing data prepared by clerks
    - Verifying statutory compliance
    - Checking for calculation errors
    - Flagging potential issues
    - Approving data for assessor review
    """
    if not current_user.has_role('deputy') and not current_user.is_admin:
        flash('You do not have permission to access the Deputy dashboard.', 'warning')
        return redirect(url_for('home.index'))
    
    logger.info(f"User {current_user.username} accessed Deputy dashboard")
    return render_template('role_dashboards/deputy_dashboard.html')


@role_dashboards_bp.route('/assessor')
@login_required
def assessor_dashboard():
    """
    Assessor dashboard - focused on final certification and approval.
    
    This dashboard provides interfaces for:
    - Reviewing deputy-verified data
    - Providing final certification
    - Generating official reports
    - Managing public-facing information
    """
    if not current_user.has_role('assessor') and not current_user.is_admin:
        flash('You do not have permission to access the Assessor dashboard.', 'warning')
        return redirect(url_for('home.index'))
    
    logger.info(f"User {current_user.username} accessed Assessor dashboard")
    return render_template('role_dashboards/assessor_dashboard.html')


def init_role_dashboards_routes(app):
    """
    Initialize role-based dashboard routes.
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(role_dashboards_bp)
    
    # Register a global context processor to make role information available in all templates
    @app.context_processor
    def inject_role_dashboard_info():
        return {'HAS_ROLE_DASHBOARDS': True}
    
    logger.info("Registered role-based dashboard routes")
    return True