"""
Role-based dashboard routes for the TerraLevy platform.

This module defines routes for role-specific dashboards (clerk, deputy, assessor)
as part of the multi-stage certification workflow described in the product requirements.
"""

import logging
from functools import wraps
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user

from app import db
from models import User, UserRole, TaxDistrict, TaxCode

# Configure logger
logger = logging.getLogger(__name__)

# Create blueprint
role_dashboards_bp = Blueprint('role_dashboards', __name__, url_prefix='/role-dashboards')

# Role-based access control decorators
def clerk_required(f):
    """Decorator that checks if the current user has the clerk role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('You need to be logged in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.has_role('clerk') and not current_user.is_admin:
            flash('You need clerk permissions to access this page.', 'warning')
            return redirect(url_for('home.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def deputy_required(f):
    """Decorator that checks if the current user has the deputy role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('You need to be logged in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.has_role('deputy') and not current_user.is_admin:
            flash('You need deputy permissions to access this page.', 'warning')
            return redirect(url_for('home.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def assessor_required(f):
    """Decorator that checks if the current user has the assessor role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('You need to be logged in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.has_role('assessor') and not current_user.is_admin:
            flash('You need assessor permissions to access this page.', 'warning')
            return redirect(url_for('home.index'))
        
        return f(*args, **kwargs)
    return decorated_function

# Dashboard routes
@role_dashboards_bp.route('/clerk')
@login_required
@clerk_required
def clerk_dashboard():
    """
    Clerk dashboard route.
    
    This dashboard focuses on data entry, import, and initial validation.
    """
    try:
        district_count = TaxDistrict.query.count()
        tax_code_count = TaxCode.query.count()
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {str(e)}")
        district_count = 0
        tax_code_count = 0
    
    return render_template(
        'role_dashboards/clerk_dashboard.html',
        district_count=district_count,
        tax_code_count=tax_code_count
    )

@role_dashboards_bp.route('/deputy')
@login_required
@deputy_required
def deputy_dashboard():
    """
    Deputy dashboard route.
    
    This dashboard focuses on data review, verification, and compliance checking.
    """
    try:
        district_count = TaxDistrict.query.count()
        tax_code_count = TaxCode.query.count()
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {str(e)}")
        district_count = 0
        tax_code_count = 0
    
    return render_template(
        'role_dashboards/deputy_dashboard.html',
        district_count=district_count,
        tax_code_count=tax_code_count
    )

@role_dashboards_bp.route('/assessor')
@login_required
@assessor_required
def assessor_dashboard():
    """
    Assessor dashboard route.
    
    This dashboard focuses on final certification, report generation, and public communication.
    """
    try:
        district_count = TaxDistrict.query.count()
        tax_code_count = TaxCode.query.count()
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {str(e)}")
        district_count = 0
        tax_code_count = 0
    
    return render_template(
        'role_dashboards/assessor_dashboard.html',
        district_count=district_count,
        tax_code_count=tax_code_count
    )

def init_role_dashboards_routes(app):
    """
    Initialize role-based dashboard routes.
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(role_dashboards_bp)
    
    # Add context processor to make role permissions available in all templates
    @app.context_processor
    def inject_role_permissions():
        """Make role permissions available in all templates."""
        if current_user.is_authenticated:
            has_role_dashboards = (
                current_user.is_admin or
                current_user.has_role('clerk') or
                current_user.has_role('deputy') or
                current_user.has_role('assessor')
            )
        else:
            has_role_dashboards = False
        
        return {
            'HAS_ROLE_DASHBOARDS': has_role_dashboards,
            'HAS_CLERK_ROLE': current_user.is_authenticated and (current_user.has_role('clerk') or current_user.is_admin),
            'HAS_DEPUTY_ROLE': current_user.is_authenticated and (current_user.has_role('deputy') or current_user.is_admin),
            'HAS_ASSESSOR_ROLE': current_user.is_authenticated and (current_user.has_role('assessor') or current_user.is_admin)
        }
    
    logger.info("Registered role-based dashboard routes")