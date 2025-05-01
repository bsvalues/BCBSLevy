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
from flask import Blueprint, request, jsonify, render_template
import psycopg2
from psycopg2.extras import RealDictCursor

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