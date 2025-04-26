"""
Routes for advanced historical data analysis and visualization.

This module includes routes for:
- Statistical analysis of historical data
- Trend forecasting and prediction
- Advanced data comparisons
- Multi-year report generation
"""

import json
from typing import Dict, List, Optional, Any
from flask import Blueprint, render_template, request, jsonify, abort, flash, redirect, url_for
from sqlalchemy import func, and_, or_, desc, asc

from app import db
from models import TaxCode, TaxCodeHistoricalRate, TaxDistrict
from utils.advanced_historical_analysis import (
    compute_basic_statistics,
    compute_moving_average,
    forecast_future_rates,
    detect_levy_rate_anomalies,
    aggregate_by_district,
    generate_comparison_report,
)

# Create blueprint
historical_analysis_bp = Blueprint('historical_analysis', __name__, url_prefix='/historical-analysis')

@historical_analysis_bp.route('/', methods=['GET', 'POST'])
def advanced_historical_analysis():
    """
    Advanced historical analysis dashboard with multiple analytical tools.
    """
    # Get all tax codes for dropdowns
    tax_codes = TaxCode.query.order_by(TaxCode.tax_code).all()
    
    # Get all available years from the historical rates table
    years_query = db.session.query(
        TaxCodeHistoricalRate.year
    ).distinct().order_by(
        TaxCodeHistoricalRate.year.desc()
    ).all()
    available_years = [year[0] for year in years_query]
    
    # Get all district IDs
    districts_query = db.session.query(
        TaxDistrict.id
    ).distinct().order_by(
        TaxDistrict.id
    ).all()
    districts = [district[0] for district in districts_query]
    
    # Initialize result variables
    stats_data = None
    forecast_data = None
    anomaly_data = None
    district_data = None
    comparison_report = None
    
    # Process form submissions
    if request.method == 'POST':
        # Statistical analysis
        if 'analyze_statistics' in request.form:
            try:
                tax_code = request.form.get('stats_tax_code')
                years_input = request.form.getlist('stats_years')
                years = [int(year) for year in years_input] if years_input else None
                
                stats_data = compute_basic_statistics(tax_code, years)
                if not stats_data.get('historical_data'):
                    flash(f'No historical data found for tax code {tax_code}', 'warning')
            except Exception as e:
                flash(f'Error computing statistics: {str(e)}', 'danger')
        
        # Trend forecasting
        elif 'forecast_trends' in request.form:
            try:
                tax_code = request.form.get('forecast_tax_code')
                years_input = request.form.getlist('forecast_base_years')
                years = [int(year) for year in years_input] if years_input else None
                forecast_years = int(request.form.get('forecast_years', 3))
                method = request.form.get('forecast_method', 'linear')
                
                forecast_data = forecast_future_rates(
                    tax_code, 
                    forecast_years=forecast_years,
                    method=method,
                    years=years
                )
                if not forecast_data.get('historical_data'):
                    flash(f'Insufficient historical data for forecasting tax code {tax_code}', 'warning')
            except Exception as e:
                flash(f'Error generating forecast: {str(e)}', 'danger')
        
        # Anomaly detection
        elif 'detect_anomalies' in request.form:
            try:
                tax_code = request.form.get('anomaly_tax_code')
                years_input = request.form.getlist('anomaly_years')
                years = [int(year) for year in years_input] if years_input else None
                threshold = float(request.form.get('anomaly_threshold', 2.0))
                
                anomaly_data = detect_levy_rate_anomalies(
                    tax_code, 
                    threshold=threshold,
                    years=years
                )
                if not anomaly_data.get('all_rates'):
                    flash(f'Insufficient data for anomaly detection for tax code {tax_code}', 'warning')
            except Exception as e:
                flash(f'Error detecting anomalies: {str(e)}', 'danger')
        
        # District analysis
        elif 'aggregate_district' in request.form:
            try:
                district_id = int(request.form.get('district_id'))
                years_input = request.form.getlist('district_years')
                years = [int(year) for year in years_input] if years_input else None
                
                district_data = aggregate_by_district(
                    district_id, 
                    years=years
                )
                if district_data.get('error'):
                    flash(district_data['error'], 'warning')
            except Exception as e:
                flash(f'Error analyzing district: {str(e)}', 'danger')
        
        # Year comparison
        elif 'generate_comparison' in request.form:
            try:
                start_year = int(request.form.get('start_year'))
                end_year = int(request.form.get('end_year'))
                min_change = float(request.form.get('min_change', 1.0)) / 100.0  # Convert percent to decimal
                
                comparison_report = generate_comparison_report(
                    start_year,
                    end_year,
                    min_change_threshold=min_change
                )
                if comparison_report.get('error'):
                    flash(comparison_report['error'], 'warning')
            except Exception as e:
                flash(f'Error generating comparison report: {str(e)}', 'danger')
    
    return render_template(
        'advanced_historical_analysis.html',
        tax_codes=tax_codes,
        available_years=available_years,
        districts=districts,
        stats_data=stats_data,
        forecast_data=forecast_data,
        anomaly_data=anomaly_data,
        district_data=district_data,
        comparison_report=comparison_report
    )

@historical_analysis_bp.route('/api/statistics', methods=['GET'])
def api_historical_statistics():
    """
    API endpoint for basic statistical analysis of historical levy rates.
    
    Query parameters:
    - tax_code: The tax code to analyze
    - years: Optional comma-separated list of years to include in analysis
    
    Returns:
    - JSON object with statistical measures
    """
    tax_code = request.args.get('tax_code')
    years_param = request.args.get('years')
    
    if not tax_code:
        return jsonify({'error': 'Missing required parameter: tax_code'}), 400
    
    years = None
    if years_param:
        try:
            years = [int(year.strip()) for year in years_param.split(',')]
        except ValueError:
            return jsonify({'error': 'Invalid years format. Use comma-separated integers'}), 400
    
    try:
        stats_data = compute_basic_statistics(tax_code, years)
        return jsonify(stats_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@historical_analysis_bp.route('/api/forecast', methods=['GET'])
def api_historical_forecast():
    """
    API endpoint for forecasting future levy rates.
    
    Query parameters:
    - tax_code: The tax code to forecast
    - forecast_years: Number of years to forecast (default: 3)
    - method: Forecasting method ('linear', 'average', 'weighted', 'exponential', 'arima')
    - years: Optional comma-separated list of years to include in analysis
    
    Returns:
    - JSON object with forecasting results and quality metrics
    """
    tax_code = request.args.get('tax_code')
    forecast_years = request.args.get('forecast_years', '3')
    method = request.args.get('method', 'linear')
    years_param = request.args.get('years')
    
    if not tax_code:
        return jsonify({'error': 'Missing required parameter: tax_code'}), 400
    
    years = None
    if years_param:
        try:
            years = [int(year.strip()) for year in years_param.split(',')]
        except ValueError:
            return jsonify({'error': 'Invalid years format. Use comma-separated integers'}), 400
    
    try:
        forecast_years = int(forecast_years)
    except ValueError:
        return jsonify({'error': 'forecast_years must be an integer'}), 400
    
    if method not in ['linear', 'average', 'weighted', 'exponential', 'arima']:
        return jsonify({'error': 'method must be one of: linear, average, weighted, exponential, arima'}), 400
    
    try:
        forecast_data = forecast_future_rates(
            tax_code, 
            forecast_years=forecast_years,
            method=method,
            years=years
        )
        return jsonify(forecast_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@historical_analysis_bp.route('/api/anomalies', methods=['GET'])
def api_historical_anomalies():
    """
    API endpoint for detecting anomalies in historical levy rates.
    
    Query parameters:
    - tax_code: The tax code to analyze
    - threshold: Z-score threshold for anomaly detection (default: 2.0)
    - years: Optional comma-separated list of years to include in analysis
    
    Returns:
    - JSON object with anomaly detection results
    """
    tax_code = request.args.get('tax_code')
    threshold = request.args.get('threshold', '2.0')
    years_param = request.args.get('years')
    
    if not tax_code:
        return jsonify({'error': 'Missing required parameter: tax_code'}), 400
    
    years = None
    if years_param:
        try:
            years = [int(year.strip()) for year in years_param.split(',')]
        except ValueError:
            return jsonify({'error': 'Invalid years format. Use comma-separated integers'}), 400
    
    try:
        threshold = float(threshold)
    except ValueError:
        return jsonify({'error': 'threshold must be a number'}), 400
    
    try:
        anomaly_data = detect_levy_rate_anomalies(
            tax_code, 
            threshold=threshold,
            years=years
        )
        return jsonify(anomaly_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@historical_analysis_bp.route('/api/district', methods=['GET'])
def api_historical_district():
    """
    API endpoint for aggregating historical levy data by tax district.
    
    Query parameters:
    - district_id: The tax district ID to analyze
    - years: Optional comma-separated list of years to include in analysis
    
    Returns:
    - JSON object with aggregated district data
    """
    try:
        district_id = int(request.args.get('district_id', 0))
    except ValueError:
        return jsonify({'error': 'district_id must be an integer'}), 400
    
    if district_id <= 0:
        return jsonify({'error': 'Missing or invalid required parameter: district_id'}), 400
    
    years_param = request.args.get('years')
    years = None
    if years_param:
        try:
            years = [int(year.strip()) for year in years_param.split(',')]
        except ValueError:
            return jsonify({'error': 'Invalid years format. Use comma-separated integers'}), 400
    
    try:
        district_data = aggregate_by_district(
            district_id, 
            years=years
        )
        return jsonify(district_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@historical_analysis_bp.route('/api/comparison', methods=['GET'])
def api_historical_comparison():
    """
    API endpoint for generating year-over-year comparison reports.
    
    Query parameters:
    - start_year: The starting year for comparison
    - end_year: The ending year for comparison
    - min_change: Minimum change threshold to include in report (as percentage)
    
    Returns:
    - JSON object with detailed comparison report
    """
    start_year = request.args.get('start_year')
    end_year = request.args.get('end_year')
    min_change = request.args.get('min_change', '1.0')
    
    if not start_year or not end_year:
        return jsonify({'error': 'Missing required parameters: start_year, end_year'}), 400
    
    try:
        start_year = int(start_year)
        end_year = int(end_year)
    except ValueError:
        return jsonify({'error': 'Years must be integers'}), 400
    
    try:
        min_change = float(min_change) / 100.0  # Convert percentage to decimal
    except ValueError:
        return jsonify({'error': 'min_change must be a number'}), 400
    
    try:
        comparison_data = generate_comparison_report(
            start_year,
            end_year,
            min_change_threshold=min_change
        )
        return jsonify(comparison_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@historical_analysis_bp.route('/historical-rates', methods=['GET'])
def historical_rates():
    """
    Display historical tax rates page with visualization options.
    
    This is the main entry point for users to access historical rate data.
    It provides a simplified interface to the advanced analysis tools.
    """
    # Get all tax codes for dropdowns
    tax_codes = TaxCode.query.order_by(TaxCode.tax_code).all()
    
    # Get all available years from the historical rates table
    years_query = db.session.query(
        TaxCodeHistoricalRate.year
    ).distinct().order_by(
        TaxCodeHistoricalRate.year.desc()
    ).all()
    available_years = [year[0] for year in years_query]
    
    # Pre-select the most recent tax code for convenience
    selected_tax_code = request.args.get('tax_code')
    if not selected_tax_code and tax_codes:
        selected_tax_code = tax_codes[0].tax_code
    
    # Get historical data for the selected tax code
    historical_data = None
    if selected_tax_code:
        try:
            historical_data = compute_basic_statistics(selected_tax_code)
        except Exception as e:
            flash(f"Error retrieving historical data: {str(e)}", "danger")
    
    return render_template(
        'historical_rates.html',
        tax_codes=tax_codes,
        available_years=available_years,
        selected_tax_code=selected_tax_code,
        historical_data=historical_data
    )

@historical_analysis_bp.route('/compliance', methods=['GET', 'POST'])
def compliance():
    """
    Check levy compliance against statutory limits and requirements.
    
    This tool helps users verify that levy rates comply with state laws
    and identify potential issues before they become problems.
    """
    tax_codes = TaxCode.query.order_by(TaxCode.tax_code).all()
    
    # Get available years
    years_query = db.session.query(
        TaxCodeHistoricalRate.year
    ).distinct().order_by(
        TaxCodeHistoricalRate.year.desc()
    ).all()
    available_years = [year[0] for year in years_query]
    
    # Initialize variables
    compliance_results = None
    selected_year = None
    selected_tax_code = None
    
    if request.method == 'POST':
        selected_year = request.form.get('year')
        selected_tax_code = request.form.get('tax_code')
        
        if selected_tax_code and selected_year:
            # For demonstration, we'll implement a simple compliance check
            try:
                # Get tax code details
                tax_code_obj = TaxCode.query.filter_by(tax_code=selected_tax_code).first()
                if not tax_code_obj:
                    flash(f'Tax code {selected_tax_code} not found', 'warning')
                    return render_template(
                        'enhanced_compliance.html',
                        tax_codes=tax_codes,
                        available_years=available_years
                    )
                
                # Get historical rate for selected year
                historical_rate = TaxCodeHistoricalRate.query.filter_by(
                    tax_code_id=tax_code_obj.id,
                    year=int(selected_year)
                ).first()
                
                if not historical_rate:
                    flash(f'No rate data found for tax code {selected_tax_code} in year {selected_year}', 'warning')
                    return render_template(
                        'enhanced_compliance.html',
                        tax_codes=tax_codes,
                        available_years=available_years
                    )
                
                # Implement compliance checks
                # For example, check if levy rate is within statutory maximum
                statutory_max = 5.90  # Example maximum rate
                is_compliant = historical_rate.levy_rate <= statutory_max
                
                # Check year-over-year increase
                prev_year_rate = TaxCodeHistoricalRate.query.filter_by(
                    tax_code_id=tax_code_obj.id,
                    year=int(selected_year) - 1
                ).first()
                
                yoy_increase = None
                yoy_limit = 1.01  # 1% limit
                yoy_compliant = True
                
                if prev_year_rate:
                    yoy_increase = (historical_rate.levy_rate - prev_year_rate.levy_rate) / prev_year_rate.levy_rate
                    yoy_compliant = yoy_increase <= (yoy_limit - 1)
                
                # Package results
                compliance_results = {
                    'tax_code': selected_tax_code,
                    'year': selected_year,
                    'levy_rate': historical_rate.levy_rate,
                    'statutory_max': statutory_max,
                    'is_compliant': is_compliant,
                    'yoy_increase': yoy_increase,
                    'yoy_limit': yoy_limit - 1,  # Convert to percentage
                    'yoy_compliant': yoy_compliant,
                    'overall_compliance': is_compliant and yoy_compliant
                }
                
            except Exception as e:
                flash(f'Error checking compliance: {str(e)}', 'danger')
    
    return render_template(
        'enhanced_compliance.html',
        tax_codes=tax_codes,
        available_years=available_years,
        compliance_results=compliance_results,
        selected_year=selected_year,
        selected_tax_code=selected_tax_code
    )

def init_historical_analysis_routes(app):
    """Initialize historical analysis routes with the Flask app."""
    app.register_blueprint(historical_analysis_bp)
    app.logger.info('Historical analysis routes initialized')