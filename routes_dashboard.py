"""
Dashboard routes for the Levy Calculation System.

This module provides routes for the main dashboard interface,
which displays key metrics and statistics for authenticated users.
"""

import logging
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func

from app import db
from models import (
    TaxDistrict, TaxCode, Property, ImportLog, ExportLog, 
    LevyRate, TaxCodeHistoricalRate, User
)
from utils.dashboard_utils import (
    get_recent_imports, 
    get_import_count, 
    get_export_count, 
    get_import_success_count, 
    get_export_success_count
)

# Create blueprint
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# Configure logger
logger = logging.getLogger(__name__)


@dashboard_bp.route('/')
@login_required
def index():
    """
    Main dashboard view.
    
    Displays key metrics and statistics for the Levy Calculation System.
    """
    # Get current year
    current_year = datetime.now().year
    
    # Get statistics
    try:
        # Count entities (with year filter for TaxCode since it now has a year column)
        current_year = datetime.now().year
        district_count = TaxDistrict.query.filter_by(is_active=True).count()
        tax_code_count = TaxCode.query.filter_by(year=current_year).count() if TaxCode.query.count() > 0 else 0
        property_count = Property.query.count()
        
        # Calculate aggregates
        levy_stats = db.session.query(
            func.sum(TaxCode.total_assessed_value).label('total_assessed_value'),
            func.sum(TaxCode.total_levy_amount).label('total_levy_amount'),
            func.avg(TaxCode.effective_tax_rate).label('avg_levy_rate')
        ).first()
        
        total_assessed_value = levy_stats.total_assessed_value or 0
        total_levy_amount = levy_stats.total_levy_amount or 0
        avg_levy_rate = levy_stats.avg_levy_rate or 0
        
        # Get recent imports (last 5)
        recent_imports = get_recent_imports(limit=5)
        
    except Exception as e:
        import traceback
        error_tb = traceback.format_exc()
        logger.error(f"Error fetching dashboard data: {str(e)}\n{error_tb}")
        district_count = 0
        tax_code_count = 0
        property_count = 0
        total_assessed_value = 0
        total_levy_amount = 0
        avg_levy_rate = 0
        recent_imports = []
    
    # Prepare stats object as expected by the template
    stats = {
        'districts': district_count,
        'tax_codes': tax_code_count,
        'properties': property_count,
        'total_av': f'${total_assessed_value / 1000000000:.1f}B' if total_assessed_value else '$0.0B',
        'total_levy': f'${total_levy_amount / 1000000:.1f}M' if total_levy_amount else '$0.0M',
        'avg_rate': f'{avg_levy_rate:.4f}' if avg_levy_rate else '0.0000',
        'compliance_rate': '92.8%',  # Default for now, will be calculated from actual data in future
        'pending_actions': 7  # Default for now, will be calculated from actual data in future
    }
    
    # Calculate YoY changes (placeholders for now)
    stats_changes = {
        'av_change': '+7.2%',
        'levy_change': '+3.5%',
        'compliance_change': '+5.0%'
    }
    
    # Process recent imports for the activity feed
    recent_activity = []
    for imp in recent_imports:
        user_name = "System"
        try:
            if imp.user_id:
                user = User.query.get(imp.user_id)
                if user:
                    user_name = user.username
        except:
            pass
            
        recent_activity.append({
            'type': 'import',
            'title': f'{imp.import_type.capitalize()} Import Completed',
            'description': f'{imp.filename} imported successfully.',
            'timestamp': imp.created_at,
            'user': user_name
        })
    
    return render_template(
        'dashboard.html',
        stats=stats,
        stats_changes=stats_changes,
        recent_activity=recent_activity,
        current_year=current_year
    )


@dashboard_bp.route('/metrics')
@login_required
def dashboard_metrics():
    """
    API endpoint for dashboard metrics.
    
    Returns JSON with key metrics for the dashboard charts and widgets.
    """
    year = request.args.get('year', datetime.now().year, type=int)
    
    try:
        # Get district types and their levy amounts
        district_metrics = db.session.query(
            TaxDistrict.district_type,
            func.sum(LevyRate.levy_amount).label('levy_amount')
        ).join(
            LevyRate, LevyRate.tax_district_id == TaxDistrict.id
        ).filter(
            LevyRate.year == year
        ).group_by(
            TaxDistrict.district_type
        ).all()
        
        # Convert to dictionary for easier use in frontend
        district_data = {
            'labels': [d.district_type for d in district_metrics],
            'values': [float(d.levy_amount) for d in district_metrics]
        }
        
        # Get historical rates for last 5 years
        end_year = year
        start_year = end_year - 4
        
        historical_rates = db.session.query(
            TaxCodeHistoricalRate.year,
            func.avg(TaxCodeHistoricalRate.levy_rate).label('avg_rate')
        ).filter(
            TaxCodeHistoricalRate.year.between(start_year, end_year)
        ).group_by(
            TaxCodeHistoricalRate.year
        ).order_by(
            TaxCodeHistoricalRate.year
        ).all()
        
        historical_data = {
            'labels': [r.year for r in historical_rates],
            'values': [float(r.avg_rate) for r in historical_rates]
        }
        
        return jsonify({
            'status': 'success',
            'district_data': district_data,
            'historical_data': historical_data
        })
        
    except Exception as e:
        import traceback
        error_tb = traceback.format_exc()
        logger.error(f"Error fetching dashboard metrics: {str(e)}\n{error_tb}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch dashboard metrics'
        }), 500


@dashboard_bp.route('/stats')
@login_required
def dashboard_stats():
    """
    API endpoint for dashboard statistics.
    
    Returns JSON with statistics for the dashboard.
    """
    try:
        # Current year
        current_year = datetime.now().year
        
        # System stats (User queries should be reliable, so keeping them direct)
        user_count = User.query.filter_by(is_active=True).count()
        admin_count = User.query.filter_by(is_active=True, is_admin=True).count()
        
        # Use safe utility functions for import/export counts
        import_count = get_import_count(year=current_year)
        export_count = get_export_count(year=current_year)
        
        # Success rates with safe utility functions
        import_success_rate = 0
        if import_count > 0:
            success_imports = get_import_success_count(year=current_year)
            import_success_rate = (success_imports / import_count) * 100
        
        export_success_rate = 0
        if export_count > 0:
            success_exports = get_export_success_count(year=current_year)
            export_success_rate = (success_exports / export_count) * 100
        
        return jsonify({
            'status': 'success',
            'stats': {
                'user_count': user_count,
                'admin_count': admin_count,
                'import_count': import_count,
                'export_count': export_count,
                'import_success_rate': import_success_rate,
                'export_success_rate': export_success_rate
            }
        })
        
    except Exception as e:
        import traceback
        error_tb = traceback.format_exc()
        logger.error(f"Error fetching dashboard stats: {str(e)}\n{error_tb}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch dashboard statistics'
        }), 500


def register_dashboard_routes(app):
    """
    Register dashboard routes with the Flask application.
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(dashboard_bp)
    logger.info("Registered dashboard routes")