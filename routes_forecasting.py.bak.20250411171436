"""
Routes for the forecasting module of the Levy Calculation Application.

This module provides routes for generating forecasts of levy rates
using historical data and various statistical models, including AI-enhanced forecasting.
"""
import json
import logging
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from sqlalchemy import func
import numpy as np

from models import TaxCode, TaxCodeHistoricalRate, TaxDistrict
from app import db
from utils.forecasting_utils import (
    generate_forecast_for_tax_code,
    create_forecast_chart_data,
    InsufficientDataError,
    FORECAST_MODELS
)

# Setup AI-enhanced forecasting if available
try:
    from utils.ai_forecasting_utils import (
        generate_forecast_explanation,
        generate_forecast_recommendations,
        ai_forecast_model_selector,
        detect_anomalies_with_ai
    )
    from utils.advanced_ai_agent import get_advanced_analysis_agent
    
    # Import district analysis utilities
    from utils.district_analysis import (
        get_district_details,
        get_district_tax_codes,
        get_district_historical_rates,
        calculate_comprehensive_statistics,
        calculate_trend_statistics,
        calculate_compliance_statistics
    )
    
    AI_FORECASTING_AVAILABLE = True
except ImportError:
    AI_FORECASTING_AVAILABLE = False
    
# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
forecasting_bp = Blueprint('forecasting', __name__, url_prefix='/forecasting')

@forecasting_bp.route('/', methods=['GET'])
def index():
    """Render the forecasting index page."""
    # Get tax codes with sufficient historical data (at least 3 years)
    tax_codes_with_counts = db.session.query(
        TaxCode,
        func.count(TaxCodeHistoricalRate.id).label('history_count')
    ).join(
        TaxCodeHistoricalRate,
        TaxCode.id == TaxCodeHistoricalRate.tax_code_id
    ).group_by(
        TaxCode.id
    ).having(
        func.count(TaxCodeHistoricalRate.id) >= 3
    ).order_by(
        TaxCode.tax_code
    ).all()
    
    # Format for the template
    tax_codes = []
    for tax_code, history_count in tax_codes_with_counts:
        tax_code.history_count = history_count
        tax_codes.append(tax_code)
    
    return render_template(
        'forecasting/index.html',
        page_title='Levy Rate Forecasting',
        tax_codes=tax_codes,
        ai_forecasting_available=AI_FORECASTING_AVAILABLE
    )

@forecasting_bp.route('/analyze/<int:tax_code_id>', methods=['GET'])
def analyze(tax_code_id: int):
    """Analyze historical data for a specific tax code."""
    # Get the tax code
    tax_code = TaxCode.query.get_or_404(tax_code_id)
    
    # Get historical rates for this tax code
    historical_rates = TaxCodeHistoricalRate.query.filter_by(
        tax_code_id=tax_code_id
    ).order_by(
        TaxCodeHistoricalRate.year
    ).all()
    
    if len(historical_rates) < 3:
        flash('Insufficient historical data for analysis. At least 3 years of data is required.', 'warning')
        return redirect(url_for('forecasting.index'))
    
    # Extract data for the template
    years = [rate.year for rate in historical_rates]
    rates = [rate.levy_rate for rate in historical_rates]
    levy_amounts = [rate.levy_amount for rate in historical_rates]
    assessed_values = [rate.total_assessed_value for rate in historical_rates]
    
    # Prepare JSON data for charts
    years_json = json.dumps(years)
    rates_json = json.dumps(rates)
    levy_amounts_json = json.dumps(levy_amounts)
    assessed_values_json = json.dumps(assessed_values)
    
    return render_template(
        'forecasting/analyze.html',
        page_title=f'Tax Code Analysis: {tax_code.tax_code}',
        tax_code=tax_code,
        historical_rates=historical_rates,
        years=years,
        rates=rates,
        years_json=years_json,
        rates_json=rates_json,
        levy_amounts_json=levy_amounts_json,
        assessed_values_json=assessed_values_json
    )

@forecasting_bp.route('/forecast', methods=['GET', 'POST'])
def forecast():
    """Generate forecasts for a specific tax code."""
    # Get tax codes with sufficient historical data
    tax_codes_with_counts = db.session.query(
        TaxCode,
        func.count(TaxCodeHistoricalRate.id).label('history_count')
    ).join(
        TaxCodeHistoricalRate,
        TaxCode.id == TaxCodeHistoricalRate.tax_code_id
    ).group_by(
        TaxCode.id
    ).having(
        func.count(TaxCodeHistoricalRate.id) >= 3
    ).order_by(
        TaxCode.tax_code
    ).all()
    
    # Format for the template
    tax_codes = []
    for tax_code, history_count in tax_codes_with_counts:
        tax_code.history_count = history_count
        tax_codes.append(tax_code)
    
    # For GET requests, show the form
    if request.method == 'GET':
        # Get optional pre-selected tax code from query string
        tax_code_id = request.args.get('tax_code_id', type=int)
        
        return render_template(
            'forecasting/forecast.html',
            page_title='Generate Forecast',
            tax_codes=tax_codes,
            tax_code_id=tax_code_id,
            years_to_forecast=3,
            confidence_level=0.95,
            preferred_model=None,
            include_explanation=AI_FORECASTING_AVAILABLE
        )
    
    # For POST requests, generate the forecast
    # Get form parameters
    tax_code_id = request.form.get('tax_code_id', type=int)
    years_to_forecast = request.form.get('years_to_forecast', type=int, default=3)
    confidence_level = request.form.get('confidence_level', type=float, default=0.95)
    preferred_model = request.form.get('preferred_model', default=None)
    include_explanation = request.form.get('include_explanation') == 'true'
    
    # Validate inputs
    if not tax_code_id:
        flash('Please select a tax code', 'danger')
        return render_template(
            'forecasting/forecast.html',
            page_title='Generate Forecast',
            tax_codes=tax_codes,
            years_to_forecast=years_to_forecast,
            confidence_level=confidence_level,
            preferred_model=preferred_model,
            include_explanation=include_explanation
        )
    
    if years_to_forecast < 1 or years_to_forecast > 10:
        flash('Years to forecast must be between 1 and 10', 'danger')
        return render_template(
            'forecasting/forecast.html',
            page_title='Generate Forecast',
            tax_codes=tax_codes,
            tax_code_id=tax_code_id,
            years_to_forecast=3,
            confidence_level=confidence_level,
            preferred_model=preferred_model,
            include_explanation=include_explanation
        )
    
    if preferred_model and preferred_model not in FORECAST_MODELS:
        flash(f'Invalid forecast model. Valid options are: {", ".join(FORECAST_MODELS)}', 'danger')
        return render_template(
            'forecasting/forecast.html',
            page_title='Generate Forecast',
            tax_codes=tax_codes,
            tax_code_id=tax_code_id,
            years_to_forecast=years_to_forecast,
            confidence_level=0.95,
            preferred_model=None,
            include_explanation=include_explanation
        )
    
    # Generate the forecast
    try:
        result = generate_forecast_for_tax_code(
            tax_code_id=tax_code_id,
            years_to_forecast=years_to_forecast,
            confidence_level=confidence_level,
            preferred_model=preferred_model
        )
        
        # Prepare chart data
        chart_data = create_forecast_chart_data(
            years=result['historical_years'],
            values=result['historical_rates'],
            future_years=result['forecast_years'],
            forecasts={
                result['best_model']: result['forecasts'][result['best_model']]
            }
        )
        
        # Generate AI-enhanced explanation if requested
        ai_explanation = None
        ai_recommendations = None
        
        if include_explanation and AI_FORECASTING_AVAILABLE:
            try:
                ai_explanation = generate_forecast_explanation(
                    tax_code=result['tax_code'],
                    historical_years=result['historical_years'],
                    historical_rates=result['historical_rates'],
                    forecast_years=result['forecast_years'],
                    forecast_rates=result['forecasts'][result['best_model']]['forecast'],
                    best_model=result['best_model'],
                    anomalies=result['anomalies']
                )
                
                ai_recommendations = generate_forecast_recommendations(
                    tax_code=result['tax_code'],
                    historical_rates=result['historical_rates'],
                    forecast_rates=result['forecasts'][result['best_model']]['forecast'],
                    current_year=result['historical_years'][-1],
                    forecast_years=result['forecast_years']
                )
            except Exception as e:
                logger.error(f"Error generating AI explanation: {str(e)}")
                flash('AI-enhanced explanation could not be generated.', 'warning')
        
        # Format data for the chart
        all_years_json = json.dumps(chart_data['years'])
        historical_with_nulls_json = json.dumps(chart_data['historical'])
        forecast_json = json.dumps(chart_data[f'{result["best_model"]}_forecast'])
        lower_bound_json = json.dumps(chart_data[f'{result["best_model"]}_lower'])
        upper_bound_json = json.dumps(chart_data[f'{result["best_model"]}_upper'])
        
        # Display confidence level as percentage
        confidence_percent = int(confidence_level * 100)
        
        return render_template(
            'forecasting/forecast_result.html',
            page_title=f'Forecast Results: {result["tax_code"]}',
            result=result,
            confidence_level=confidence_percent,
            all_years_json=all_years_json,
            historical_with_nulls_json=historical_with_nulls_json,
            forecast_json=forecast_json,
            lower_bound_json=lower_bound_json,
            upper_bound_json=upper_bound_json,
            ai_explanation=ai_explanation,
            ai_recommendations=ai_recommendations
        )
    
    except InsufficientDataError:
        flash('Insufficient historical data for forecasting. At least 3 years of data is required.', 'danger')
    except ValueError as e:
        flash(f'Error generating forecast: {str(e)}', 'danger')
    except Exception as e:
        logger.exception(f"Unexpected error in forecast: {str(e)}")
        flash('An unexpected error occurred while generating the forecast.', 'danger')
    
    return render_template(
        'forecasting/forecast.html',
        page_title='Generate Forecast',
        tax_codes=tax_codes,
        tax_code_id=tax_code_id,
        years_to_forecast=years_to_forecast,
        confidence_level=confidence_level,
        preferred_model=preferred_model,
        include_explanation=include_explanation
    )


@forecasting_bp.route('/ai', methods=['GET'])
def ai_dashboard():
    """Render the AI-enhanced forecasting dashboard."""
    if not AI_FORECASTING_AVAILABLE:
        flash('AI-enhanced forecasting is not available.', 'warning')
        return redirect(url_for('forecasting.index'))
    
    # Get tax codes with sufficient historical data (at least 3 years)
    tax_codes_with_counts = db.session.query(
        TaxCode,
        func.count(TaxCodeHistoricalRate.id).label('history_count')
    ).join(
        TaxCodeHistoricalRate,
        TaxCode.id == TaxCodeHistoricalRate.tax_code_id
    ).group_by(
        TaxCode.id
    ).having(
        func.count(TaxCodeHistoricalRate.id) >= 3
    ).order_by(
        TaxCode.tax_code
    ).all()
    
    # Format for the template
    tax_codes = []
    for tax_code, history_count in tax_codes_with_counts:
        tax_codes.append({
            'id': tax_code.id,
            'code': tax_code.tax_code,
            'description': tax_code.description or f"District: {tax_code.district.district_name if hasattr(tax_code, 'district') and tax_code.district else 'Unknown'}",
            'history_count': history_count
        })
    
    return render_template(
        'forecasting/ai_dashboard.html',
        page_title='AI-Enhanced Forecasting',
        tax_codes=tax_codes
    )


@forecasting_bp.route('/ai/generate', methods=['POST'])
def generate_ai_forecast():
    """Generate an AI-enhanced forecast and return JSON data."""
    if not AI_FORECASTING_AVAILABLE:
        return jsonify({'error': 'AI-enhanced forecasting is not available.'}), 400
    
    try:
        # Get form parameters
        tax_code = request.form.get('tax_code')
        years_ahead = request.form.get('years_ahead', type=int, default=3)
        scenario = request.form.get('scenario', default='baseline')
        
        # Validate parameters
        if not tax_code:
            return jsonify({'error': 'Please select a tax code.'}), 400
        
        if years_ahead < 1 or years_ahead > 10:
            return jsonify({'error': 'Years ahead must be between 1 and 10.'}), 400
        
        if scenario not in ['baseline', 'optimistic', 'pessimistic']:
            return jsonify({'error': 'Invalid scenario.'}), 400
        
        # Get the tax code from the database
        tax_code_obj = TaxCode.query.filter_by(tax_code=tax_code).first()
        
        if not tax_code_obj:
            return jsonify({'error': f'Tax code {tax_code} not found.'}), 404
        
        # Get historical rates for this tax code
        historical_rates = TaxCodeHistoricalRate.query.filter_by(
            tax_code_id=tax_code_obj.id
        ).order_by(
            TaxCodeHistoricalRate.year
        ).all()
        
        if len(historical_rates) < 3:
            return jsonify({'error': 'Insufficient historical data. At least 3 years of data is required.'}), 400
        
        # Extract data for analysis
        historical_years = [rate.year for rate in historical_rates]
        historical_rates_values = [rate.levy_rate for rate in historical_rates]
        
        # Get additional data for ML analysis
        assessed_values = [rate.total_assessed_value for rate in historical_rates if rate.total_assessed_value is not None]
        levy_amounts = [rate.levy_amount for rate in historical_rates if rate.levy_amount is not None]
        
        # Use AI to select the best forecasting model
        data = {
            'years': historical_years,
            'rates': historical_rates_values,
            'assessed_values': assessed_values if assessed_values else None,
            'levy_amounts': levy_amounts if levy_amounts else None
        }
        
        # Select model using AI
        selected_model = ai_forecast_model_selector(data)
        
        # Fit the model and generate forecast
        selected_model.fit()
        
        # Generate future years
        last_year = historical_years[-1]
        forecast_years = [last_year + i + 1 for i in range(years_ahead)]
        
        # Apply scenario adjustment to the forecast
        scenario_adjustment = 1.0  # Baseline scenario
        if scenario == 'optimistic':
            scenario_adjustment = 0.85  # More favorable rates (lower)
        elif scenario == 'pessimistic':
            scenario_adjustment = 1.15  # Less favorable rates (higher)
        
        # Generate point forecasts with scenario adjustment
        forecast_rates = [selected_model.predict(year) * scenario_adjustment for year in forecast_years]
        
        # Calculate confidence intervals (95% by default)
        historical_std = np.std(historical_rates_values)
        z_score = 1.96  # for 95% confidence
        
        confidence_intervals = []
        for i, rate in enumerate(forecast_rates):
            # Adjust confidence interval width based on forecast horizon
            # Further in the future = wider interval
            margin = z_score * historical_std * (1 + (i * 0.1))
            lower = max(0, rate - margin)
            upper = rate + margin
            confidence_intervals.append([lower, upper])
        
        # Optional: Use AI to detect anomalies in the historical data
        anomalies = detect_anomalies_with_ai(
            years=historical_years,
            rates=historical_rates_values
        )
        
        # Prepare response data
        response_data = {
            'tax_code': tax_code,
            'scenario': scenario,
            'years': historical_years + forecast_years,
            'historical_rates': historical_rates_values + [None] * len(forecast_years),
            'forecast_rates': [None] * len(historical_years) + forecast_rates,
            'confidence_intervals': [None] * len(historical_years) + confidence_intervals,
            'anomalies': anomalies,
            'model_name': selected_model.name
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        logger.exception(f"Error in AI forecast: {str(e)}")
        return jsonify({'error': str(e)}), 500

@forecasting_bp.route('/ai/explain', methods=['POST'])
def generate_ai_explanation():
    """Generate an AI-enhanced explanation of a forecast."""
    if not AI_FORECASTING_AVAILABLE:
        return jsonify({'error': 'AI-enhanced forecasting is not available.'}), 400
    
    try:
        # Get form parameters
        tax_code = request.form.get('tax_code')
        historical_years = request.form.getlist('historical_years[]', type=int)
        historical_rates = request.form.getlist('historical_rates[]', type=float)
        forecast_years = request.form.getlist('forecast_years[]', type=int)
        forecast_rates = request.form.getlist('forecast_rates[]', type=float)
        anomalies = request.form.getlist('anomalies[]', type=int)
        model_name = request.form.get('model_name')
        
        # Validate parameters
        if not tax_code or not historical_years or not historical_rates:
            return jsonify({'error': 'Missing required parameters.'}), 400
        
        # Generate explanation and recommendations
        explanation = generate_forecast_explanation(
            tax_code=tax_code,
            historical_years=historical_years,
            historical_rates=historical_rates,
            forecast_years=forecast_years,
            forecast_rates=forecast_rates,
            best_model=model_name,
            anomalies=anomalies
        )
        
        recommendations = generate_forecast_recommendations(
            tax_code=tax_code,
            historical_rates=historical_rates,
            forecast_rates=forecast_rates,
            current_year=historical_years[-1],
            forecast_years=forecast_years
        )
        
        return jsonify({
            'explanation': explanation,
            'recommendations': recommendations
        })
    
    except Exception as e:
        logger.exception(f"Error generating AI explanation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@forecasting_bp.route('/ai/enhanced', methods=['GET'])
def ai_enhanced():
    """Render the AI-enhanced comprehensive analysis page."""
    if not AI_FORECASTING_AVAILABLE:
        flash('AI-enhanced analysis is not available.', 'warning')
        return redirect(url_for('forecasting.index'))
    
    # Get all tax districts
    districts = TaxDistrict.query.order_by(TaxDistrict.district_name).all()
    
    return render_template(
        'forecasting/ai_enhanced.html',
        page_title='AI-Enhanced Comprehensive Analysis',
        districts=districts,
        ai_available=AI_FORECASTING_AVAILABLE
    )

@forecasting_bp.route('/ai/analyze', methods=['POST'])
def execute_ai_comprehensive_analysis():
    """Execute a comprehensive AI analysis on a tax district."""
    if not AI_FORECASTING_AVAILABLE:
        return jsonify({'error': 'AI-enhanced analysis is not available.'}), 400
    
    try:
        # Get form parameters
        district_id = request.form.get('district_id')
        analysis_type = request.form.get('analysis_type', default='comprehensive')
        years = request.form.get('years', type=int, default=3)
        
        # Validate parameters
        if not district_id:
            return jsonify({'error': 'Please select a tax district.'}), 400
        
        if years < 1 or years > 10:
            return jsonify({'error': 'Years must be between 1 and 10.'}), 400
        
        if analysis_type not in ['comprehensive', 'trend', 'compliance']:
            return jsonify({'error': 'Invalid analysis type.'}), 400
        
        # Get advanced analysis agent
        try:
            advanced_agent = get_advanced_analysis_agent()
        except Exception as e:
            logger.error(f"Error initializing advanced analysis agent: {str(e)}")
            return jsonify({'error': 'Could not initialize AI analysis agent.'}), 500
        
        # Execute multi-step analysis
        analysis_result = advanced_agent.perform_multistep_analysis(
            tax_district_id=district_id,
            analysis_type=analysis_type,
            years=years
        )
        
        # Check for errors
        if 'error' in analysis_result:
            return jsonify({
                'error': analysis_result['error'],
                'partial_results': analysis_result
            }), 400
        
        return jsonify(analysis_result)
    
    except Exception as e:
        logger.exception(f"Error in AI comprehensive analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@forecasting_bp.route('/district/<int:district_id>/analysis', methods=['GET'])
def district_analysis(district_id: int):
    """Render the AI district analysis page for a specific tax district."""
    if not AI_FORECASTING_AVAILABLE:
        flash('AI-enhanced district analysis is not available.', 'warning')
        return redirect(url_for('forecasting.index'))
    
    # Get the district
    district = TaxDistrict.query.get_or_404(district_id)
    
    # Get the district details
    district_details = get_district_details(str(district_id))
    
    # Get all tax codes associated with this district
    tax_codes = get_district_tax_codes(str(district_id))
    
    # Get historical rates for this district
    historical_rates = get_district_historical_rates(str(district_id), years=3)
    
    # Calculate comprehensive statistics
    comprehensive_stats = calculate_comprehensive_statistics(tax_codes, historical_rates)
    
    # Calculate trend statistics
    trend_stats = calculate_trend_statistics(tax_codes, historical_rates)
    
    # Calculate compliance statistics
    compliance_stats = calculate_compliance_statistics(tax_codes, historical_rates)
    
    return render_template(
        'forecasting/district_analysis.html',
        page_title=f'District Analysis: {district.district_name}',
        district=district,
        district_details=district_details,
        tax_codes=tax_codes,
        historical_rates=historical_rates,
        comprehensive_stats=comprehensive_stats,
        trend_stats=trend_stats,
        compliance_stats=compliance_stats,
        ai_available=AI_FORECASTING_AVAILABLE
    )

@forecasting_bp.route('/api/tax_codes', methods=['GET'])
def api_get_tax_codes():
    """API endpoint to get tax codes with sufficient historical data."""
    try:
        # Get tax codes with sufficient historical data (at least 3 years)
        tax_codes_with_counts = db.session.query(
            TaxCode,
            func.count(TaxCodeHistoricalRate.id).label('history_count')
        ).join(
            TaxCodeHistoricalRate,
            TaxCode.id == TaxCodeHistoricalRate.tax_code_id
        ).group_by(
            TaxCode.id
        ).having(
            func.count(TaxCodeHistoricalRate.id) >= 3
        ).order_by(
            TaxCode.tax_code
        ).all()
        
        # Format for JSON
        response = []
        for tax_code, history_count in tax_codes_with_counts:
            response.append({
                'id': tax_code.id,
                'code': tax_code.tax_code,
                'description': tax_code.description or "",
                'history_count': history_count
            })
        
        return jsonify(response)
    
    except Exception as e:
        logger.exception(f"Error in API get_tax_codes: {str(e)}")
        return jsonify({'error': str(e)}), 500