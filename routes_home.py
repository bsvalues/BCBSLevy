"""
Core routes for the TerraLevy application (PRIMARY HOME ROUTES).

This module provides the main routes for the application including
the dashboard, home page, and user settings. This is the standardized
version that integrates with app.py as the primary application entry point.

This module replaces the previous routes2.py approach and consolidates 
all home-related routes into a single blueprint that is properly registered
with the main app.py application.

Routes provided:
- / : Main landing page (index)
- /dashboard : Dashboard with summary statistics
- /about : About page
- /settings : User settings page
- /help : Help and documentation

Part of the TerraFusion Platform ecosystem.
"""
from flask import Blueprint, render_template, request, jsonify, current_app, session, redirect, url_for

from app import db
from models import TaxCode, Property, TaxDistrict

# Create a blueprint for the home routes
home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    """Render the home/landing page."""
    # For now, redirect to dashboard as our main entry point
    return redirect(url_for('home.dashboard'))

@home_bp.route('/dashboard')
def dashboard():
    """Render the main dashboard with TerraLevy design."""
    from datetime import datetime
    # Get current year
    current_year = datetime.now().year
    
    try:
        # Summary statistics
        tax_code_count = TaxCode.query.distinct(TaxCode.tax_code).count()
        property_count = Property.query.count()
        district_count = TaxDistrict.query.count()
        
        # Calculate aggregates for the template
        total_assessed_value = 0
        total_levy_amount = 0
        avg_levy_rate = 0
        
        # Create default recent imports (empty list)
        recent_imports = []
        
        # Create sample scenario data for dashboard
        recent_scenarios = [
            {'name': 'School District #123 - 2025', 'date': '04/20/2025', 'district': 'School District #123', 'levy_rate': 2.5498},
            {'name': 'City of Springfield - Forecast', 'date': '04/18/2025', 'district': 'City of Springfield', 'levy_rate': 1.8735},
            {'name': 'Fire District #7 - Final', 'date': '04/15/2025', 'district': 'Fire District #7', 'levy_rate': 0.9432}
        ]
        
        # Create statistics for dashboard
        stats = {
            'districts': district_count,
            'compliance_rate': '92.8%',
            'total_av': '$5.3B',
            'pending_actions': 7
        }
        
    except Exception as e:
        current_app.logger.error(f"Error fetching dashboard data: {str(e)}")
        tax_code_count = 0
        property_count = 0
        district_count = 0
        total_assessed_value = 0
        total_levy_amount = 0
        avg_levy_rate = 0
        recent_imports = []
        recent_scenarios = []
        stats = {
            'districts': 0,
            'compliance_rate': '0%',
            'total_av': '$0',
            'pending_actions': 0
        }
    
    return render_template(
        'dashboard.html',
        page_title="TerraLevy Dashboard",
        page_subtitle="Welcome to your comprehensive levy management hub",
        stats=stats,
        tax_code_count=tax_code_count,
        property_count=property_count,
        district_count=district_count,
        total_assessed_value=total_assessed_value,
        total_levy_amount=total_levy_amount,
        avg_levy_rate=avg_levy_rate,
        recent_imports=recent_imports,
        recent_scenarios=recent_scenarios,
        current_year=current_year,
        show_page_header=True
    )

@home_bp.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html', page_title="About")

@home_bp.route('/settings')
def settings():
    """Render the settings page."""
    return render_template('settings.html', page_title="Settings")

@home_bp.route('/help')
def help_page():
    """Render the help page."""
    return render_template('help.html', page_title="Help & Documentation")

@home_bp.route('/login')
def login_redirect():
    """Redirect /login to /auth/login for better compatibility."""
    return redirect(url_for('auth.login'))

@home_bp.route('/reports')
def reports_redirect():
    """Redirect /reports to /reports/dashboard for better compatibility."""
    return redirect(url_for('reports.reports_dashboard'))

@home_bp.route('/demo-dashboard')
def demo_dashboard():
    """Render the enhanced demo dashboard for Benton County."""
    return render_template('demo_dashboard.html', page_title="Benton County Levy Dashboard")

def init_home_routes(app):
    """Register home routes with the Flask app."""
    app.register_blueprint(home_bp)
    app.logger.info('TerraLevy home routes initialized')