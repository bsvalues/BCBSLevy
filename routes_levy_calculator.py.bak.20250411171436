"""
Routes for the Levy Calculator module.

This module includes routes for:
- Basic levy calculation
- Bill impact calculator
- Rate comparison tools
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from sqlalchemy import func, desc
from decimal import Decimal, ROUND_HALF_UP
import json

from app import db
from models import TaxCode, TaxDistrict, Property, TaxCodeHistoricalRate

# Create blueprint
levy_calculator_bp = Blueprint('levy_calculator', __name__, url_prefix='/levy-calculator')

@levy_calculator_bp.route('/', methods=['GET', 'POST'])
def calculator():
    """
    Primary levy calculation tool for tax rates and amounts.
    """
    tax_codes = TaxCode.query.order_by(TaxCode.tax_code).all()
    
    return render_template(
        'levy_calculator.html',
        tax_codes=tax_codes
    )

@levy_calculator_bp.route('/impact-calculator', methods=['GET', 'POST'])
def impact_calculator():
    """
    Bill impact calculator to estimate the effect of levy changes on property taxes.
    """
    # Get all tax codes for dropdown
    tax_codes = TaxCode.query.order_by(TaxCode.tax_code).all()
    
    # Get all available years from historical rates
    years_query = db.session.query(
        TaxCodeHistoricalRate.year
    ).distinct().order_by(
        TaxCodeHistoricalRate.year.desc()
    ).all()
    available_years = [year[0] for year in years_query]
    
    # Initialize results dictionary
    impact_results = None
    
    if request.method == 'POST':
        # Get form data
        tax_code = request.form.get('tax_code')
        property_value = request.form.get('property_value')
        base_year = request.form.get('base_year')
        comparison_year = request.form.get('comparison_year')
        custom_rate = request.form.get('custom_rate')
        calculation_type = request.form.get('calculation_type', 'historical')
        
        if not tax_code or not property_value:
            flash('Please provide both tax code and property value', 'warning')
            return render_template(
                'bill_impact_calculator.html',
                tax_codes=tax_codes,
                available_years=available_years
            )
        
        try:
            # Convert property value to float
            property_value = float(property_value)
            
            # Get tax code object
            tax_code_obj = TaxCode.query.filter_by(tax_code=tax_code).first()
            if not tax_code_obj:
                flash(f'Tax code {tax_code} not found', 'warning')
                return render_template(
                    'bill_impact_calculator.html',
                    tax_codes=tax_codes,
                    available_years=available_years
                )
            
            # Initialize variables
            base_rate = None
            comparison_rate = None
            base_amount = None
            comparison_amount = None
            
            # Process based on calculation type
            if calculation_type == 'historical':
                # Check for required years
                if not base_year or not comparison_year:
                    flash('Please select both base and comparison years', 'warning')
                    return render_template(
                        'bill_impact_calculator.html',
                        tax_codes=tax_codes,
                        available_years=available_years
                    )
                
                # Get historical rates
                base_rate_obj = TaxCodeHistoricalRate.query.filter_by(
                    tax_code_id=tax_code_obj.id,
                    year=int(base_year)
                ).first()
                
                comparison_rate_obj = TaxCodeHistoricalRate.query.filter_by(
                    tax_code_id=tax_code_obj.id,
                    year=int(comparison_year)
                ).first()
                
                # Check if rates exist
                if not base_rate_obj:
                    flash(f'No rate found for tax code {tax_code} in year {base_year}', 'warning')
                    return render_template(
                        'bill_impact_calculator.html',
                        tax_codes=tax_codes,
                        available_years=available_years
                    )
                
                if not comparison_rate_obj:
                    flash(f'No rate found for tax code {tax_code} in year {comparison_year}', 'warning')
                    return render_template(
                        'bill_impact_calculator.html',
                        tax_codes=tax_codes,
                        available_years=available_years
                    )
                
                # Get rates
                base_rate = base_rate_obj.levy_rate
                comparison_rate = comparison_rate_obj.levy_rate
            else:  # custom rate
                # Validate custom rate
                if not custom_rate:
                    flash('Please provide a custom comparison rate', 'warning')
                    return render_template(
                        'bill_impact_calculator.html',
                        tax_codes=tax_codes,
                        available_years=available_years
                    )
                
                try:
                    custom_rate = float(custom_rate)
                except ValueError:
                    flash('Custom rate must be a number', 'warning')
                    return render_template(
                        'bill_impact_calculator.html',
                        tax_codes=tax_codes,
                        available_years=available_years
                    )
                
                # Use current tax code rate as base
                base_rate = tax_code_obj.levy_rate
                comparison_rate = custom_rate
                base_year = "Current"
                comparison_year = "Custom"
            
            # Calculate tax amounts
            # In property tax calculations, the levy rate is expressed per $1,000 of assessed value
            # So we divide the property value by 1000 before multiplying by the rate
            base_amount = (property_value / 1000) * base_rate
            comparison_amount = (property_value / 1000) * comparison_rate
            
            # Calculate difference and percentage change
            difference = comparison_amount - base_amount
            percent_change = 0
            if base_amount > 0:
                percent_change = (difference / base_amount) * 100
            
            # Package results
            impact_results = {
                'tax_code': tax_code,
                'property_value': property_value,
                'base_year': base_year,
                'comparison_year': comparison_year,
                'base_rate': base_rate,
                'comparison_rate': comparison_rate,
                'base_amount': base_amount,
                'comparison_amount': comparison_amount,
                'difference': difference,
                'percent_change': percent_change
            }
            
        except Exception as e:
            flash(f'Error calculating impact: {str(e)}', 'danger')
    
    return render_template(
        'bill_impact_calculator.html',
        tax_codes=tax_codes,
        available_years=available_years,
        impact_results=impact_results
    )

@levy_calculator_bp.route('/api/calculate', methods=['POST'])
def api_calculate():
    """
    API endpoint for levy calculations.
    
    Accepts POST with JSON:
    {
        "tax_code": "123456",
        "assessed_value": 300000,
        "year": 2025  // optional
    }
    
    Returns:
    {
        "tax_code": "123456",
        "levy_rate": 5.25,
        "assessed_value": 300000,
        "tax_amount": 1575.0
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        tax_code = data.get('tax_code')
        assessed_value = data.get('assessed_value')
        year = data.get('year')
        
        if not tax_code or not assessed_value:
            return jsonify({'error': 'Missing required parameters: tax_code, assessed_value'}), 400
        
        # Get tax code object
        tax_code_obj = TaxCode.query.filter_by(tax_code=tax_code).first()
        if not tax_code_obj:
            return jsonify({'error': f'Tax code {tax_code} not found'}), 404
        
        # Get levy rate (either current or historical)
        levy_rate = None
        if year:
            # Get historical rate
            historical_rate = TaxCodeHistoricalRate.query.filter_by(
                tax_code_id=tax_code_obj.id,
                year=year
            ).first()
            
            if not historical_rate:
                return jsonify({'error': f'No rate found for tax code {tax_code} in year {year}'}), 404
            
            levy_rate = historical_rate.levy_rate
        else:
            # Use current rate
            levy_rate = tax_code_obj.levy_rate
        
        # Calculate tax amount
        tax_amount = (assessed_value / 1000) * levy_rate
        
        # Format result to 2 decimal places
        tax_amount = round(tax_amount, 2)
        levy_rate = round(levy_rate, 4)
        
        result = {
            'tax_code': tax_code,
            'levy_rate': levy_rate,
            'assessed_value': assessed_value,
            'tax_amount': tax_amount
        }
        
        if year:
            result['year'] = year
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def register_levy_calculator_routes(app):
    """Initialize levy calculator routes with the Flask app."""
    app.register_blueprint(levy_calculator_bp)
    app.logger.info('Levy calculator routes initialized')