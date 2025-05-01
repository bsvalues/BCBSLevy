"""
Levy Worksheet Blueprint

This module integrates the Washington State DOR-style levy worksheet functionality
into the main TerraFusion application.
"""

import logging
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from levy_worksheet_service import register_levy_worksheet_blueprint, calculate_levy_worksheet, save_levy_calculation

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create blueprint
levy_worksheet_routes = Blueprint('levy_worksheet_routes', __name__, template_folder='templates')

@levy_worksheet_routes.route('/levy-worksheet')
@login_required
def worksheet_home():
    """Main levy worksheet dashboard page."""
    return render_template('levy_worksheet/dashboard.html')

@levy_worksheet_routes.route('/levy-worksheet/new')
@login_required
def new_worksheet():
    """New levy worksheet calculator page."""
    return render_template('levy_worksheet/calculator.html')

@levy_worksheet_routes.route('/levy-worksheet/<int:district_id>')
@login_required
def district_worksheet(district_id):
    """District-specific levy worksheet calculator page."""
    return render_template('levy_worksheet/calculator.html', district_id=district_id)

@levy_worksheet_routes.route('/levy-worksheet/scenario/<int:scenario_id>')
@login_required
def view_scenario(scenario_id):
    """View a saved levy scenario."""
    return render_template('levy_worksheet/view_scenario.html', scenario_id=scenario_id)

@levy_worksheet_routes.route('/api/v1/levy-worksheet/calculate', methods=['POST'])
@login_required
def api_calculate_worksheet():
    """API endpoint to calculate a levy worksheet."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Extract parameters
        district_id = data.get('district_id')
        year = data.get('year', 2025)
        highest_lawful_levy = data.get('highest_lawful_levy')
        new_construction_value = data.get('new_construction_value', 0)
        annexation_value = data.get('annexation_value', 0)
        refund_amount = data.get('refund_amount', 0)
        target_levy_amount = data.get('target_levy_amount')
        
        # Validate required parameters
        if not district_id:
            return jsonify({"error": "district_id is required"}), 400
        
        # Calculate worksheet
        worksheet = calculate_levy_worksheet(
            district_id=district_id,
            year=year,
            highest_lawful_levy=highest_lawful_levy,
            new_construction_value=new_construction_value,
            annexation_value=annexation_value,
            refund_amount=refund_amount,
            target_levy_amount=target_levy_amount
        )
        
        # Handle errors
        if "error" in worksheet:
            return jsonify(worksheet), 400
        
        # Return calculation without saving
        if not data.get('save', False):
            return jsonify({"worksheet": worksheet, "saved": False})
        
        # Save calculation if requested
        scenario_id = save_levy_calculation(worksheet, current_user.id if current_user.is_authenticated else None)
        
        if scenario_id:
            worksheet["scenario_id"] = scenario_id
            return jsonify({"worksheet": worksheet, "saved": True, "scenario_id": scenario_id})
        else:
            return jsonify({"worksheet": worksheet, "saved": False, 
                           "error": "Failed to save calculation"}), 500
    
    except Exception as e:
        logger.error(f"Error calculating worksheet: {str(e)}")
        return jsonify({"error": str(e)}), 500

@levy_worksheet_routes.route('/api/v1/levy-worksheet/export/<int:scenario_id>', methods=['GET'])
@login_required
def export_worksheet(scenario_id):
    """Export a worksheet in various formats."""
    format_type = request.args.get('format', 'pdf')
    
    # This would be implemented to generate PDF, Excel, or other formats
    # of the worksheet for printing or sharing
    
    return jsonify({"message": f"Export functionality for {format_type} format not yet implemented"}), 501

def init_app(app):
    """Initialize the levy worksheet routes with the Flask app."""
    app.register_blueprint(levy_worksheet_routes)
    register_levy_worksheet_blueprint(app)
    logger.info('Levy Worksheet routes initialized')