"""
Levy Worksheet Microservice

This module implements a Washington State DOR-style levy worksheet calculator
that integrates with the TerraFusion database and provides advanced levy
calculation capabilities with step-by-step visualization.

Features:
- Detailed step-by-step worksheet calculations
- Historical data integration
- Real-time validation against statutory limits
- Exportable calculations in multiple formats
- Audit trail for all calculations
"""

import os
import json
import logging
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from flask import Blueprint, request, jsonify, render_template, send_file, make_response
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_login import login_required, current_user

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Blueprint for levy worksheet routes
levy_worksheet_bp = Blueprint('levy_worksheet', __name__)

# Constants
PRIOR_YEAR_STATUTORY_LIMIT = 1.01  # 1% increase limit
MINIMUM_RATE = Decimal('0.001')  # Minimum valid levy rate
DEFAULT_COUNTY = "Benton"
DEFAULT_STATE = "WA"

# Helper Functions
def get_db_connection():
    """Get a connection to the database."""
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL environment variable not found")
        return None
    
    try:
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return None

def decimal_to_currency(value):
    """Format decimal as currency string."""
    if value is None:
        return "$0.00"
    return f"${value:,.2f}"

def decimal_to_rate(value):
    """Format decimal as rate with 6 decimal places."""
    if value is None:
        return "0.000000"
    return f"{value:.6f}"

def currency_to_decimal(value):
    """Convert currency string to Decimal."""
    if not value:
        return Decimal('0')
    if isinstance(value, str):
        value = value.replace('$', '').replace(',', '')
    return Decimal(str(value))

def get_district_info(district_id, year):
    """Get district information from the database."""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT d.*, 
                (SELECT SUM(total_assessed_value) 
                 FROM tax_code 
                 WHERE tax_district_id = d.id AND year = %s) as total_assessed_value
            FROM tax_district d
            WHERE d.id = %s AND d.year = %s
            """,
            (year, district_id, year)
        )
        
        district = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return district
    
    except Exception as e:
        logger.error(f"Error getting district info: {str(e)}")
        if conn:
            conn.close()
        return None

def get_district_prior_year_levy(district_id, year):
    """Get the district's prior year levy amount."""
    prior_year = year - 1
    
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        # First try to get from historical data
        cursor.execute(
            """
            SELECT SUM(levy_amount) as total_levy
            FROM tax_code
            WHERE tax_district_id = %s AND year = %s
            """,
            (district_id, prior_year)
        )
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result and result['total_levy']:
            return Decimal(str(result['total_levy']))
        
        return Decimal('0')
    
    except Exception as e:
        logger.error(f"Error getting prior year levy: {str(e)}")
        if conn:
            conn.close()
        return Decimal('0')

def calculate_levy_worksheet(district_id, year, highest_lawful_levy=None, new_construction_value=None, 
                            annexation_value=None, refund_amount=None, target_levy_amount=None):
    """
    Calculate a complete levy worksheet with all steps and validation.
    
    Args:
        district_id: The tax district ID
        year: The levy year
        highest_lawful_levy: Previous year's highest lawful levy amount
        new_construction_value: Value of new construction
        annexation_value: Value of annexed property
        refund_amount: Refund amount
        target_levy_amount: The levy amount requested (if specific amount requested)
    
    Returns:
        A complete worksheet calculation with all intermediate steps
    """
    try:
        # Get district information
        district = get_district_info(district_id, year)
        if not district:
            return {"error": f"District {district_id} not found for year {year}"}
        
        # Get prior year levy if not provided
        prior_year_levy = get_district_prior_year_levy(district_id, year)
        if highest_lawful_levy is None:
            highest_lawful_levy = prior_year_levy
        else:
            highest_lawful_levy = currency_to_decimal(highest_lawful_levy)
        
        # Initialize values
        new_construction_value = currency_to_decimal(new_construction_value) if new_construction_value else Decimal('0')
        annexation_value = currency_to_decimal(annexation_value) if annexation_value else Decimal('0')
        refund_amount = currency_to_decimal(refund_amount) if refund_amount else Decimal('0')
        target_levy_amount = currency_to_decimal(target_levy_amount) if target_levy_amount else None
        
        # Current assessed value from the district
        total_assessed_value = currency_to_decimal(district['total_assessed_value']) if district['total_assessed_value'] else Decimal('0')
        
        # 1. Calculate 101% limit (default statutory limit)
        limit_101_amount = (highest_lawful_levy * PRIOR_YEAR_STATUTORY_LIMIT).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # 2. Calculate new construction levy
        # Typical new construction rate is the prior year levy rate
        if prior_year_levy > 0 and total_assessed_value > 0:
            prior_year_rate = (prior_year_levy / total_assessed_value) * Decimal('1000')
        else:
            prior_year_rate = Decimal('0')
            
        new_construction_levy = (new_construction_value * prior_year_rate / Decimal('1000')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # 3. Calculate annexation levy (using same rate as new construction)
        annexation_levy = (annexation_value * prior_year_rate / Decimal('1000')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # 4. Calculate maximum allowable levy
        max_allowable_levy = limit_101_amount + new_construction_levy + annexation_levy + refund_amount
        
        # 5. Determine final levy amount (either target or max allowable)
        if target_levy_amount and target_levy_amount < max_allowable_levy:
            final_levy_amount = target_levy_amount
            is_at_max = False
        else:
            final_levy_amount = max_allowable_levy
            is_at_max = True
            
        # 6. Calculate levy rate per $1000 assessed value
        if total_assessed_value > 0:
            levy_rate = (final_levy_amount / total_assessed_value) * Decimal('1000')
            levy_rate = levy_rate.quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
        else:
            levy_rate = Decimal('0')
        
        # Check if rate is below minimum valid rate
        is_below_minimum = levy_rate < MINIMUM_RATE if levy_rate > 0 else False
            
        # 7. Prepare detailed worksheet results
        worksheet = {
            "district_info": {
                "id": district_id,
                "name": district['district_name'],
                "type": district['district_type'],
                "county": district['county'],
                "state": district['state'],
                "year": year
            },
            "inputs": {
                "highest_lawful_levy": decimal_to_currency(highest_lawful_levy),
                "prior_year_levy": decimal_to_currency(prior_year_levy),
                "total_assessed_value": decimal_to_currency(total_assessed_value),
                "new_construction_value": decimal_to_currency(new_construction_value),
                "annexation_value": decimal_to_currency(annexation_value),
                "refund_amount": decimal_to_currency(refund_amount),
                "target_levy_amount": decimal_to_currency(target_levy_amount) if target_levy_amount else "Not specified"
            },
            "calculation_steps": {
                "step1_101_limit": {
                    "description": "Highest lawful levy × 101%",
                    "calculation": f"{decimal_to_currency(highest_lawful_levy)} × 1.01",
                    "result": decimal_to_currency(limit_101_amount)
                },
                "step2_new_construction": {
                    "description": "New construction levy",
                    "calculation": f"{decimal_to_currency(new_construction_value)} × {decimal_to_rate(prior_year_rate)} ÷ 1000",
                    "result": decimal_to_currency(new_construction_levy)
                },
                "step3_annexation": {
                    "description": "Annexation levy",
                    "calculation": f"{decimal_to_currency(annexation_value)} × {decimal_to_rate(prior_year_rate)} ÷ 1000",
                    "result": decimal_to_currency(annexation_levy)
                },
                "step4_maximum_levy": {
                    "description": "Maximum allowable levy",
                    "calculation": f"{decimal_to_currency(limit_101_amount)} + {decimal_to_currency(new_construction_levy)} + {decimal_to_currency(annexation_levy)} + {decimal_to_currency(refund_amount)}",
                    "result": decimal_to_currency(max_allowable_levy)
                }
            },
            "results": {
                "prior_year_rate": decimal_to_rate(prior_year_rate),
                "final_levy_amount": decimal_to_currency(final_levy_amount),
                "levy_rate": decimal_to_rate(levy_rate),
                "is_at_maximum": is_at_max,
                "is_below_minimum_rate": is_below_minimum,
                "timestamp": datetime.utcnow().isoformat()
            },
            "warnings": []
        }
        
        # Add warnings if needed
        if is_below_minimum:
            worksheet["warnings"].append({
                "type": "RATE_TOO_LOW",
                "message": f"Calculated rate of {decimal_to_rate(levy_rate)} is below the minimum valid rate of {decimal_to_rate(MINIMUM_RATE)}."
            })
            
        if target_levy_amount and target_levy_amount > max_allowable_levy:
            worksheet["warnings"].append({
                "type": "TARGET_EXCEEDS_MAXIMUM",
                "message": f"Requested levy amount of {decimal_to_currency(target_levy_amount)} exceeds maximum allowable amount of {decimal_to_currency(max_allowable_levy)}."
            })
            
        if total_assessed_value == 0:
            worksheet["warnings"].append({
                "type": "ZERO_ASSESSED_VALUE",
                "message": "Total assessed value is zero, cannot calculate a valid levy rate."
            })
            
        return worksheet
        
    except Exception as e:
        logger.error(f"Error calculating levy worksheet: {str(e)}")
        return {"error": str(e)}

def save_levy_calculation(worksheet, user_id=None):
    """Save the levy calculation to the database and create audit record."""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Extract key values from worksheet
        district_id = worksheet["district_info"]["id"]
        year = worksheet["district_info"]["year"]
        final_levy_amount = currency_to_decimal(worksheet["results"]["final_levy_amount"])
        levy_rate = Decimal(worksheet["results"]["levy_rate"])
        
        # Create a levy scenario record
        now = datetime.utcnow()
        cursor.execute(
            """
            INSERT INTO levy_scenario (
                tax_district_id, year, name, description, 
                target_year, levy_amount, result_levy_rate, user_id,
                created_at, updated_at, created_by_id, updated_by_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                district_id, year, f"Worksheet Calculation {now.strftime('%Y-%m-%d %H:%M')}",
                "Created from Levy Worksheet Module", 
                year, final_levy_amount, levy_rate, user_id,
                now, now, user_id, user_id
            )
        )
        
        scenario_id = cursor.fetchone()['id']
        
        # Save the full worksheet as JSON in scenario adjustments
        cursor.execute(
            """
            INSERT INTO levy_scenario_adjustment (
                levy_scenario_id, adjustment_type, amount, 
                description, calculation_details, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                scenario_id, "WORKSHEET", 0,
                "Complete worksheet calculation", 
                json.dumps(worksheet), now, now
            )
        )
        
        # Create entries for each component if they exist
        components = [
            ("101_LIMIT", worksheet["calculation_steps"]["step1_101_limit"]["result"], 
             "101% Statutory Limit"),
            ("NEW_CONSTRUCTION", worksheet["calculation_steps"]["step2_new_construction"]["result"], 
             "New Construction Addition"),
            ("ANNEXATION", worksheet["calculation_steps"]["step3_annexation"]["result"], 
             "Annexation Addition"),
            ("REFUND", worksheet["inputs"]["refund_amount"], 
             "Refund Levy")
        ]
        
        for adj_type, amount_str, description in components:
            amount = currency_to_decimal(amount_str)
            if amount > 0:
                cursor.execute(
                    """
                    INSERT INTO levy_scenario_adjustment (
                        levy_scenario_id, adjustment_type, amount, 
                        description, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        scenario_id, adj_type, amount,
                        description, now, now
                    )
                )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return scenario_id
    
    except Exception as e:
        logger.error(f"Error saving levy calculation: {str(e)}")
        if conn:
            conn.rollback()
            conn.close()
        return False

# API Endpoints
@levy_worksheet_bp.route('/api/levy-worksheet/calculate', methods=['POST'])
def calculate_worksheet():
    """API endpoint to calculate a complete levy worksheet."""
    data = request.json
    
    # Required parameters
    district_id = data.get('district_id')
    year = data.get('year', datetime.now().year)
    
    # Optional parameters
    highest_lawful_levy = data.get('highest_lawful_levy')
    new_construction_value = data.get('new_construction_value', 0)
    annexation_value = data.get('annexation_value', 0)
    refund_amount = data.get('refund_amount', 0)
    target_levy_amount = data.get('target_levy_amount')
    
    # Validate required parameters
    if not district_id:
        return jsonify({"error": "district_id is required"}), 400
    
    # Calculate the worksheet
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
    
    # Save the calculation to the database
    user_id = request.headers.get('X-User-Id')
    scenario_id = save_levy_calculation(worksheet, user_id)
    
    if scenario_id:
        worksheet["scenario_id"] = scenario_id
    
    return jsonify(worksheet)

@levy_worksheet_bp.route('/api/levy-worksheet/districts', methods=['GET'])
def get_districts():
    """API endpoint to get available districts for a given year."""
    year = request.args.get('year', datetime.now().year)
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, district_name, district_type, county, state
            FROM tax_district
            WHERE year = %s AND is_active = TRUE
            ORDER BY district_name
            """,
            (year,)
        )
        
        districts = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({"districts": districts})
    
    except Exception as e:
        logger.error(f"Error fetching districts: {str(e)}")
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

@levy_worksheet_bp.route('/api/levy-worksheet/history/<int:district_id>', methods=['GET'])
def get_district_history(district_id):
    """API endpoint to get historical levy data for a district."""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT year, SUM(levy_amount) as total_levy, 
                   SUM(total_assessed_value) as total_assessed_value
            FROM tax_code
            WHERE tax_district_id = %s
            GROUP BY year
            ORDER BY year DESC
            """,
            (district_id,)
        )
        
        history = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Format history data
        formatted_history = []
        for record in history:
            formatted_history.append({
                "year": record['year'],
                "total_levy": decimal_to_currency(record['total_levy']),
                "total_assessed_value": decimal_to_currency(record['total_assessed_value']),
                "levy_rate": decimal_to_rate(Decimal(str(record['total_levy'])) / Decimal(str(record['total_assessed_value'])) * 1000)
                              if record['total_assessed_value'] else "0.000000"
            })
        
        return jsonify({"history": formatted_history})
    
    except Exception as e:
        logger.error(f"Error fetching district history: {str(e)}")
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

@levy_worksheet_bp.route('/api/levy-worksheet/scenarios/<int:district_id>', methods=['GET'])
def get_district_scenarios(district_id):
    """API endpoint to get saved levy scenarios for a district."""
    year = request.args.get('year', datetime.now().year)
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT s.id, s.name, s.description, s.levy_amount, s.result_levy_rate,
                   s.created_at, u.username as created_by
            FROM levy_scenario s
            LEFT JOIN "user" u ON s.created_by_id = u.id
            WHERE s.tax_district_id = %s AND s.year = %s
            ORDER BY s.created_at DESC
            """,
            (district_id, year)
        )
        
        scenarios = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({"scenarios": scenarios})
    
    except Exception as e:
        logger.error(f"Error fetching scenarios: {str(e)}")
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

# Web routes for serving the main worksheet page
@levy_worksheet_bp.route('/levy-worksheet', methods=['GET'])
def worksheet_page():
    """Main levy worksheet page."""
    return render_template('levy_worksheet.html')

@levy_worksheet_bp.route('/levy-worksheet/calculator/<int:district_id>', methods=['GET'])
def district_worksheet(district_id):
    """District-specific levy worksheet calculator page."""
    year = request.args.get('year', datetime.now().year)
    return render_template('levy_calculator.html', district_id=district_id, year=year)

# Main function
def register_levy_worksheet_blueprint(app):
    """Register the levy worksheet blueprint with the Flask app."""
    app.register_blueprint(levy_worksheet_bp)

# Multi-district comparison functionality
@levy_worksheet_bp.route('/api/v1/levy-worksheet/compare', methods=['POST'])
@login_required
def compare_districts():
    """Compare levy worksheets for multiple districts."""
    data = request.json
    
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid request data"}), 400
    
    # Extract parameters
    district_ids = data.get('district_ids', [])
    year = data.get('year', datetime.now().year)
    comparison_type = data.get('comparison_type', 'standard')  # standard, hypothetical
    
    if not district_ids or not isinstance(district_ids, list) or len(district_ids) < 2:
        return jsonify({"error": "At least two district_ids are required for comparison"}), 400
    
    try:
        # Get district information
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor()
        districts_info = []
        
        # Get information for each district
        for district_id in district_ids:
            cursor.execute(
                """
                SELECT id, district_name, district_type, county, state, year
                FROM tax_district
                WHERE id = %s
                """,
                (district_id,)
            )
            
            district = cursor.fetchone()
            if not district:
                continue
                
            # Get assessed value
            cursor.execute(
                """
                SELECT SUM(total_assessed_value) as total_assessed_value
                FROM tax_code
                WHERE tax_district_id = %s AND year = %s
                """,
                (district_id, year)
            )
            
            av_result = cursor.fetchone()
            assessed_value = av_result['total_assessed_value'] if av_result else None
            
            # Get prior year levy
            cursor.execute(
                """
                SELECT SUM(levy_amount) as total_levy
                FROM tax_code
                WHERE tax_district_id = %s AND year = %s
                """,
                (district_id, year - 1)
            )
            
            levy_result = cursor.fetchone()
            prior_levy = levy_result['total_levy'] if levy_result else None
            
            # Store district info
            districts_info.append({
                "id": district_id,
                "name": district['district_name'],
                "type": district['district_type'],
                "county": district['county'],
                "state": district['state'],
                "assessed_value": assessed_value,
                "prior_year_levy": prior_levy
            })
        
        cursor.close()
        conn.close()
        
        if not districts_info:
            return jsonify({"error": "No valid districts found"}), 404
        
        # Calculate worksheets for each district
        comparison_results = []
        
        for district in districts_info:
            # Skip districts with missing data
            if not district['assessed_value'] or not district['prior_year_levy']:
                comparison_results.append({
                    "district_id": district['id'],
                    "district_name": district['name'],
                    "error": "Missing assessed value or prior year levy data"
                })
                continue
            
            # Calculate worksheet for this district
            worksheet = calculate_levy_worksheet(
                district_id=district['id'],
                year=year,
                highest_lawful_levy=district['prior_year_levy'],
                new_construction_value=data.get('new_construction_value', 0),
                annexation_value=data.get('annexation_value', 0),
                refund_amount=data.get('refund_amount', 0)
            )
            
            # Add key comparison metrics
            comparison_results.append({
                "district_id": district['id'],
                "district_name": district['name'],
                "district_type": district['type'],
                "county": district['county'],
                "assessed_value": decimal_to_currency(district['assessed_value']),
                "prior_year_levy": decimal_to_currency(district['prior_year_levy']),
                "max_allowable_levy": worksheet['calculation_steps']['step4_maximum_levy']['result'],
                "final_levy_amount": worksheet['results']['final_levy_amount'],
                "levy_rate": worksheet['results']['levy_rate'],
                "percent_increase": f"{((currency_to_decimal(worksheet['results']['final_levy_amount']) / district['prior_year_levy']) - 1) * 100:.2f}%",
                "worksheet": worksheet
            })
        
        # Prepare comparison data
        comparison_data = {
            "year": year,
            "comparison_type": comparison_type,
            "districts": comparison_results,
            "summary": {
                "count": len(comparison_results),
                "avg_rate": sum([float(d.get('levy_rate', 0)) for d in comparison_results if 'levy_rate' in d]) / len(comparison_results) if comparison_results else 0,
                "total_assessed_value": sum([currency_to_decimal(d.get('assessed_value', "$0")) for d in comparison_results if 'assessed_value' in d]),
                "total_levy": sum([currency_to_decimal(d.get('final_levy_amount', "$0")) for d in comparison_results if 'final_levy_amount' in d])
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return jsonify(comparison_data)
    
    except Exception as e:
        logger.error(f"Error comparing districts: {str(e)}")
        return jsonify({"error": str(e)}), 500

def export_worksheet_impl(scenario_id, format_type='pdf'):
    """Implementation for exporting a worksheet in various formats."""
    try:
        # Get scenario data
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor()
        
        # Get scenario info
        cursor.execute(
            """
            SELECT s.*, d.district_name, d.district_type, d.county, d.state
            FROM levy_scenario s
            JOIN tax_district d ON s.tax_district_id = d.id
            WHERE s.id = %s
            """,
            (scenario_id,)
        )
        
        scenario = cursor.fetchone()
        if not scenario:
            cursor.close()
            conn.close()
            return jsonify({"error": f"Scenario {scenario_id} not found"}), 404
        
        # Get adjustment details
        cursor.execute(
            """
            SELECT adjustment_type, amount, description, calculation_details
            FROM levy_scenario_adjustment
            WHERE levy_scenario_id = %s
            """,
            (scenario_id,)
        )
        
        adjustments = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Find worksheet details
        worksheet_data = None
        for adj in adjustments:
            if adj['adjustment_type'] == 'WORKSHEET' and adj['calculation_details']:
                try:
                    worksheet_data = json.loads(adj['calculation_details'])
                    break
                except:
                    pass
        
        if not worksheet_data:
            return jsonify({"error": "Worksheet calculation details not found"}), 404
        
        # Export based on format type
        if format_type == 'json':
            # Return raw JSON data
            response = {
                "scenario": scenario,
                "worksheet": worksheet_data
            }
            return jsonify(response)
            
        elif format_type == 'excel':
            # Generate Excel file with xlsxwriter
            try:
                import io
                import xlsxwriter
                from flask import send_file
                
                output = io.BytesIO()
                workbook = xlsxwriter.Workbook(output)
                worksheet = workbook.add_worksheet('Levy Worksheet')
                
                # Formats
                header_format = workbook.add_format({
                    'bold': True, 'bg_color': '#337ab7', 'color': 'white', 
                    'border': 1, 'align': 'center'
                })
                title_format = workbook.add_format({
                    'bold': True, 'font_size': 14, 'align': 'center'
                })
                section_format = workbook.add_format({
                    'bold': True, 'bg_color': '#f5f5f5', 'border': 1
                })
                cell_format = workbook.add_format({'border': 1})
                number_format = workbook.add_format({'border': 1, 'num_format': '#,##0.00'})
                currency_format = workbook.add_format({'border': 1, 'num_format': '$#,##0.00'})
                rate_format = workbook.add_format({'border': 1, 'num_format': '0.000000'})
                
                # Set column widths
                worksheet.set_column('A:A', 40)
                worksheet.set_column('B:B', 15)
                worksheet.set_column('C:C', 20)
                
                # Title
                row = 0
                worksheet.merge_range('A1:C1', f"{scenario['district_name']} Levy Worksheet", title_format)
                worksheet.merge_range('A2:C2', f"Tax Year {scenario['year']}", title_format)
                row += 3
                
                # Header
                worksheet.write(row, 0, 'Description', header_format)
                worksheet.write(row, 1, 'Rate', header_format)
                worksheet.write(row, 2, 'Amount', header_format)
                row += 1
                
                # Step 1: Previous Year Highest Lawful Levy
                worksheet.merge_range(f'A{row+1}:C{row+1}', 'Step 1: Previous Year\'s Highest Lawful Levy', section_format)
                row += 1
                worksheet.write(row, 0, 'Highest Lawful Levy', cell_format)
                worksheet.write(row, 1, '', cell_format)
                worksheet.write(row, 2, currency_to_decimal(worksheet_data['inputs']['highest_lawful_levy']), currency_format)
                row += 1
                
                # Step 2: 101% Limit
                worksheet.merge_range(f'A{row+1}:C{row+1}', 'Step 2: Statutory 101% Limit', section_format)
                row += 1
                worksheet.write(row, 0, 'Multiply by Limit Factor of 101%', cell_format)
                worksheet.write(row, 1, '1.01', cell_format)
                worksheet.write(row, 2, currency_to_decimal(worksheet_data['calculation_steps']['step1_101_limit']['result']), currency_format)
                row += 1
                
                # Step 3: New Construction
                worksheet.merge_range(f'A{row+1}:C{row+1}', 'Step 3: New Construction', section_format)
                row += 1
                worksheet.write(row, 0, 'New Construction Value', cell_format)
                worksheet.write(row, 1, '', cell_format)
                worksheet.write(row, 2, currency_to_decimal(worksheet_data['inputs']['new_construction_value']), currency_format)
                row += 1
                
                worksheet.write(row, 0, 'Multiply by Last Year\'s Levy Rate', cell_format)
                worksheet.write(row, 1, worksheet_data['results']['prior_year_rate'], rate_format)
                worksheet.write(row, 2, currency_to_decimal(worksheet_data['calculation_steps']['step2_new_construction']['result']), currency_format)
                row += 1
                
                # Step 4: Annexation
                worksheet.merge_range(f'A{row+1}:C{row+1}', 'Step 4: Annexation', section_format)
                row += 1
                worksheet.write(row, 0, 'Annexation Value', cell_format)
                worksheet.write(row, 1, '', cell_format)
                worksheet.write(row, 2, currency_to_decimal(worksheet_data['inputs']['annexation_value']), currency_format)
                row += 1
                
                worksheet.write(row, 0, 'Multiply by Last Year\'s Levy Rate', cell_format)
                worksheet.write(row, 1, worksheet_data['results']['prior_year_rate'], rate_format)
                worksheet.write(row, 2, currency_to_decimal(worksheet_data['calculation_steps']['step3_annexation']['result']), currency_format)
                row += 1
                
                # Step 5: Refund
                worksheet.merge_range(f'A{row+1}:C{row+1}', 'Step 5: Refund Levy', section_format)
                row += 1
                worksheet.write(row, 0, 'Refund Amount', cell_format)
                worksheet.write(row, 1, '', cell_format)
                worksheet.write(row, 2, currency_to_decimal(worksheet_data['inputs']['refund_amount']), currency_format)
                row += 1
                
                # Step 6: Maximum Allowable
                worksheet.merge_range(f'A{row+1}:C{row+1}', 'Step 6: Maximum Allowable Levy', section_format)
                row += 1
                worksheet.write(row, 0, 'Maximum Allowable Levy', cell_format)
                worksheet.write(row, 1, '', cell_format)
                worksheet.write(row, 2, currency_to_decimal(worksheet_data['calculation_steps']['step4_maximum_levy']['result']), currency_format)
                row += 1
                
                # Target Levy (if applicable)
                if worksheet_data['inputs']['target_levy_amount'] != "Not specified":
                    worksheet.merge_range(f'A{row+1}:C{row+1}', 'Step 7: Target Levy Amount', section_format)
                    row += 1
                    worksheet.write(row, 0, 'Requested Levy Amount', cell_format)
                    worksheet.write(row, 1, '', cell_format)
                    worksheet.write(row, 2, currency_to_decimal(worksheet_data['inputs']['target_levy_amount']), currency_format)
                    row += 1
                
                # Final Results
                worksheet.merge_range(f'A{row+1}:C{row+1}', 'Final Levy Results', section_format)
                row += 1
                worksheet.write(row, 0, 'Final Levy Amount', cell_format)
                worksheet.write(row, 1, '', cell_format)
                worksheet.write(row, 2, currency_to_decimal(worksheet_data['results']['final_levy_amount']), currency_format)
                row += 1
                
                worksheet.write(row, 0, 'Current Year Assessed Value', cell_format)
                worksheet.write(row, 1, '', cell_format)
                worksheet.write(row, 2, currency_to_decimal(worksheet_data['inputs']['total_assessed_value']), currency_format)
                row += 1
                
                worksheet.write(row, 0, 'Calculated Levy Rate', cell_format)
                worksheet.write(row, 1, worksheet_data['results']['levy_rate'], rate_format)
                worksheet.write(row, 2, '', cell_format)
                row += 1
                
                # Warnings
                if worksheet_data['warnings'] and len(worksheet_data['warnings']) > 0:
                    row += 1
                    worksheet.merge_range(f'A{row+1}:C{row+1}', 'Warnings', section_format)
                    row += 1
                    
                    for warning in worksheet_data['warnings']:
                        worksheet.merge_range(f'A{row+1}:C{row+1}', warning['message'], cell_format)
                        row += 1
                
                # Footer
                row += 1
                worksheet.merge_range(f'A{row+1}:C{row+1}', f"Generated by TerraFusion on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", workbook.add_format({'italic': True}))
                
                workbook.close()
                
                # Prepare response
                output.seek(0)
                
                return send_file(
                    output, 
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                    as_attachment=True,
                    download_name=f"levy_worksheet_{scenario_id}.xlsx"
                )
            except ImportError:
                return jsonify({"error": "Excel export functionality not available. Missing dependency: xlsxwriter"}), 500
            
        elif format_type == 'pdf':
            # Generate PDF file with WeasyPrint
            try:
                from weasyprint import HTML, CSS
                from weasyprint.text.fonts import FontConfiguration
                from flask import make_response
                import tempfile
                
                # Create HTML template
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Levy Worksheet {scenario_id}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 30px; }}
                        .header {{ text-align: center; margin-bottom: 20px; }}
                        .title {{ font-size: 22px; font-weight: bold; margin-bottom: 5px; }}
                        .subtitle {{ font-size: 16px; margin-bottom: 20px; }}
                        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                        th {{ background-color: #337ab7; color: white; padding: 8px; text-align: left; }}
                        td {{ padding: 8px; border: 1px solid #ddd; }}
                        .section-header {{ background-color: #f5f5f5; font-weight: bold; }}
                        .currency {{ text-align: right; }}
                        .rate {{ text-align: right; }}
                        .footer {{ text-align: center; font-size: 10px; color: #666; margin-top: 30px; }}
                        .warning {{ background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin-bottom: 20px; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <div class="title">{scenario['district_name']} Levy Worksheet</div>
                        <div class="subtitle">Tax Year {scenario['year']}</div>
                    </div>
                    
                    <table>
                        <tr>
                            <th width="60%">Description</th>
                            <th width="15%">Rate</th>
                            <th width="25%">Amount</th>
                        </tr>
                        
                        <!-- Step 1: Previous Year's Highest Lawful Levy -->
                        <tr class="section-header">
                            <td colspan="3">Step 1: Previous Year's Highest Lawful Levy</td>
                        </tr>
                        <tr>
                            <td>Highest Lawful Levy</td>
                            <td></td>
                            <td class="currency">{worksheet_data['inputs']['highest_lawful_levy']}</td>
                        </tr>
                        
                        <!-- Step 2: 101% Limit -->
                        <tr class="section-header">
                            <td colspan="3">Step 2: Statutory 101% Limit</td>
                        </tr>
                        <tr>
                            <td>Multiply by Limit Factor of 101%</td>
                            <td class="rate">1.01</td>
                            <td class="currency">{worksheet_data['calculation_steps']['step1_101_limit']['result']}</td>
                        </tr>
                        
                        <!-- Step 3: New Construction -->
                        <tr class="section-header">
                            <td colspan="3">Step 3: New Construction</td>
                        </tr>
                        <tr>
                            <td>New Construction Value</td>
                            <td></td>
                            <td class="currency">{worksheet_data['inputs']['new_construction_value']}</td>
                        </tr>
                        <tr>
                            <td>Multiply by Last Year's Levy Rate</td>
                            <td class="rate">{worksheet_data['results']['prior_year_rate']}</td>
                            <td class="currency">{worksheet_data['calculation_steps']['step2_new_construction']['result']}</td>
                        </tr>
                        
                        <!-- Step 4: Annexation -->
                        <tr class="section-header">
                            <td colspan="3">Step 4: Annexation</td>
                        </tr>
                        <tr>
                            <td>Annexation Value</td>
                            <td></td>
                            <td class="currency">{worksheet_data['inputs']['annexation_value']}</td>
                        </tr>
                        <tr>
                            <td>Multiply by Last Year's Levy Rate</td>
                            <td class="rate">{worksheet_data['results']['prior_year_rate']}</td>
                            <td class="currency">{worksheet_data['calculation_steps']['step3_annexation']['result']}</td>
                        </tr>
                        
                        <!-- Step 5: Refund -->
                        <tr class="section-header">
                            <td colspan="3">Step 5: Refund Levy</td>
                        </tr>
                        <tr>
                            <td>Refund Amount</td>
                            <td></td>
                            <td class="currency">{worksheet_data['inputs']['refund_amount']}</td>
                        </tr>
                        
                        <!-- Step 6: Maximum Allowable -->
                        <tr class="section-header">
                            <td colspan="3">Step 6: Maximum Allowable Levy</td>
                        </tr>
                        <tr>
                            <td>Maximum Allowable Levy</td>
                            <td></td>
                            <td class="currency">{worksheet_data['calculation_steps']['step4_maximum_levy']['result']}</td>
                        </tr>
                """
                
                # Add target levy if specified
                if worksheet_data['inputs']['target_levy_amount'] != "Not specified":
                    html_content += f"""
                        <!-- Step 7: Target Levy Amount -->
                        <tr class="section-header">
                            <td colspan="3">Step 7: Target Levy Amount</td>
                        </tr>
                        <tr>
                            <td>Requested Levy Amount</td>
                            <td></td>
                            <td class="currency">{worksheet_data['inputs']['target_levy_amount']}</td>
                        </tr>
                    """
                
                # Add final results
                html_content += f"""
                        <!-- Final Results -->
                        <tr class="section-header">
                            <td colspan="3">Final Levy Results</td>
                        </tr>
                        <tr>
                            <td><strong>Final Levy Amount</strong></td>
                            <td></td>
                            <td class="currency">{worksheet_data['results']['final_levy_amount']}</td>
                        </tr>
                        <tr>
                            <td><strong>Current Year Assessed Value</strong></td>
                            <td></td>
                            <td class="currency">{worksheet_data['inputs']['total_assessed_value']}</td>
                        </tr>
                        <tr>
                            <td><strong>Calculated Levy Rate</strong></td>
                            <td class="rate">{worksheet_data['results']['levy_rate']}</td>
                            <td></td>
                        </tr>
                    </table>
                """
                
                # Add warnings if present
                if worksheet_data['warnings'] and len(worksheet_data['warnings']) > 0:
                    html_content += """
                    <div class="warning">
                        <h3>Warnings</h3>
                        <ul>
                    """
                    
                    for warning in worksheet_data['warnings']:
                        html_content += f"<li>{warning['message']}</li>"
                    
                    html_content += """
                        </ul>
                    </div>
                    """
                
                # Add footer
                html_content += f"""
                    <div class="footer">
                        Generated by TerraFusion Levy Worksheet Module on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
                    </div>
                </body>
                </html>
                """
                
                # Generate PDF
                font_config = FontConfiguration()
                html = HTML(string=html_content)
                css = CSS(string='''
                    @page {
                        size: letter;
                        margin: 1cm;
                        @bottom-center {
                            content: "Page " counter(page) " of " counter(pages);
                        }
                    }
                ''', font_config=font_config)
                
                pdf_file = html.write_pdf(stylesheets=[css], font_config=font_config)
                
                # Create a response
                response = make_response(pdf_file)
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = f'attachment; filename=levy_worksheet_{scenario_id}.pdf'
                
                return response
            except ImportError:
                return jsonify({"error": "PDF export functionality not available. Missing dependency: weasyprint"}), 500
            
        else:
            return jsonify({"error": f"Unsupported format: {format_type}"}), 400
    
    except Exception as e:
        logger.error(f"Error exporting worksheet: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # For testing purposes only
    test_district_id = 95  # Benton County
    test_year = 2025
    
    worksheet = calculate_levy_worksheet(
        district_id=test_district_id,
        year=test_year,
        highest_lawful_levy=1000000,
        new_construction_value=5000000,
        annexation_value=0,
        refund_amount=25000
    )
    
    print(json.dumps(worksheet, indent=2))