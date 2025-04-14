"""
Budget Impact Visualization routes for the Levy Calculation System.

This module provides routes for the interactive budget impact visualization 
features, allowing users to analyze and understand how changes in tax rates 
and assessed values impact district budgets.
"""

from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app
from sqlalchemy import desc, func, and_, text
from models import db, TaxDistrict, TaxCode, TaxCodeHistoricalRate, Property
from utils.sanitize_utils import sanitize_html, sanitize_mcp_insights

# Create blueprint
budget_impact_bp = Blueprint('budget_impact', __name__, url_prefix='/budget-impact')

@budget_impact_bp.route('/')
def index():
    """
    Main page for the interactive budget impact visualization.
    
    This view allows users to visualize how changes in tax rates and
    assessed values impact district budgets through various interactive
    visualizations.
    
    Returns:
        Rendered budget impact visualization template
    """
    try:
        # Get available years with error handling
        try:
            available_years = db.session.query(TaxDistrict.year).distinct().order_by(desc(TaxDistrict.year)).all()
            available_years = [year[0] for year in available_years] or [datetime.now().year]
        except Exception as e:
            current_app.logger.error(f"Error fetching available years: {str(e)}")
            available_years = [datetime.now().year]
            
        # Get selected year (default to most recent)
        current_year = available_years[0] if available_years else datetime.now().year
        year = request.args.get('year', current_year, type=int)
        
        # Get districts for selected year with tax codes
        try:
            districts = TaxDistrict.query.filter(TaxDistrict.year == year).options(
                db.joinedload(TaxDistrict.tax_codes)
            ).order_by(TaxDistrict.district_name).all()
        except Exception as e:
            current_app.logger.error(f"Error fetching districts: {str(e)}")
            districts = []
            
        # Get district types for filtering
        try:
            district_types = db.session.query(TaxDistrict.district_type).distinct().order_by(TaxDistrict.district_type).all()
            district_types = [district_type[0] for district_type in district_types] if district_types else []
        except Exception as e:
            current_app.logger.error(f"Error fetching district types: {str(e)}")
            district_types = []
        
        # If database connection was lost, try to reconnect
        if not districts and not district_types:
            current_app.logger.warning("No data retrieved, attempting to reconnect to database")
            try:
                db.session.remove()
                db.session.rollback()
                db.engine.dispose()
                # After disposing, try a simple query to test connection
                db.session.execute(text("SELECT 1")).scalar()
                current_app.logger.info("Database reconnection successful")
            except Exception as e:
                current_app.logger.error(f"Database reconnection failed: {str(e)}")
        
        return render_template(
            'budget-impact/index.html',
            districts=districts,
            district_types=district_types,
            available_years=available_years,
            year=year,
            error=None
        )
    except Exception as e:
        current_app.logger.error(f"Error in budget impact index route: {str(e)}")
        return render_template(
            'budget-impact/index.html',
            districts=[],
            district_types=[],
            available_years=[datetime.now().year],
            year=datetime.now().year,
            error="An error occurred while loading budget impact data. Please try again later."
        )

@budget_impact_bp.route('/api/simulation', methods=['POST'])
def api_budget_simulation():
    """
    API endpoint for simulating budget impacts based on tax rate changes.
    
    This endpoint processes simulation scenarios with modified tax rates
    and returns the calculated impact on district budgets.
    
    Returns:
        JSON response with simulation results
    """
    try:
        # Validate request has JSON data
        if not request.is_json:
            current_app.logger.warning("Invalid request format - JSON expected")
            return jsonify({
                'success': False,
                'error': 'Invalid request format. JSON expected.',
                'baseline': {},
                'simulation': {},
                'impact': {}
            }), 400
        
        # Get request data
        data = request.json
        
        # Extract parameters from request with validation
        year = data.get('year', datetime.now().year)
        if not isinstance(year, int):
            try:
                year = int(year)
            except (ValueError, TypeError):
                year = datetime.now().year
                current_app.logger.warning(f"Invalid year format: {data.get('year')}, using current year")
                
        scenario = data.get('scenario', {})
        if not isinstance(scenario, dict):
            current_app.logger.warning(f"Invalid scenario format: {type(scenario)}")
            return jsonify({
                'success': False,
                'error': 'Invalid scenario format. Dictionary expected.',
                'baseline': {},
                'simulation': {},
                'impact': {}
            }), 400
            
        district_ids = data.get('district_ids', [])
        if not isinstance(district_ids, list):
            current_app.logger.warning(f"Invalid district_ids format: {type(district_ids)}")
            return jsonify({
                'success': False,
                'error': 'Invalid district_ids format. List expected.',
                'baseline': {},
                'simulation': {},
                'impact': {}
            }), 400
        
        # Get baseline data for comparison
        baseline_data = get_district_budget_data(district_ids, year)
        
        # Apply scenario modifications to create simulation data
        simulation_data = simulate_budget_changes(baseline_data, scenario)
        
        # Calculate impact metrics
        impact_analysis = calculate_impact_metrics(baseline_data, simulation_data)
        
        # Log successful simulation
        current_app.logger.info(f"Budget simulation completed for year {year} with {len(district_ids)} districts")
        
        return jsonify({
            'success': True,
            'baseline': baseline_data,
            'simulation': simulation_data,
            'impact': impact_analysis
        })
    except Exception as e:
        error_msg = str(e)
        current_app.logger.error(f"Error in budget simulation: {error_msg}")
        return jsonify({
            'success': False,
            'error': sanitize_html(error_msg),
            'baseline': {},
            'simulation': {},
            'impact': {}
        }), 500

@budget_impact_bp.route('/api/districts/<int:year>')
def api_districts_by_year(year):
    """
    API endpoint to get district data for a specific year.
    
    Args:
        year: The year to get district data for
        
    Returns:
        JSON response with district data
    """
    # Get districts for the selected year
    districts = TaxDistrict.query.filter(TaxDistrict.year == year).options(
        db.joinedload(TaxDistrict.tax_codes)
    ).order_by(TaxDistrict.district_name).all()
    
    # Convert to JSON-serializable format
    districts_data = [{
        'id': d.id,
        'district_name': d.district_name,
        'district_code': d.district_code,
        'district_type': d.district_type,
        'tax_codes': [{
            'id': tc.id,
            'tax_code': tc.tax_code,
            'levy_rate': tc.effective_tax_rate or 0,
            'levy_amount': tc.total_levy_amount or 0,
            'total_assessed_value': tc.total_assessed_value or 0
        } for tc in d.tax_codes] if d.tax_codes else [],
        'year': d.year
    } for d in districts]
    
    return jsonify(districts_data)

@budget_impact_bp.route('/api/district-budget/<int:district_id>')
def api_district_budget(district_id):
    """
    API endpoint to get detailed budget data for a specific district.
    
    Args:
        district_id: The unique district identifier
        
    Returns:
        JSON response with district budget details
    """
    # Get district
    district = TaxDistrict.query.options(
        db.joinedload(TaxDistrict.tax_codes)
    ).get_or_404(district_id)
    
    # Get budget data for this district
    budget_data = get_district_budget_data([district_id], district.year)
    
    return jsonify(budget_data[0] if budget_data else {})

def get_district_budget_data(district_ids, year):
    """
    Get detailed budget data for specified districts.
    
    Args:
        district_ids: List of district IDs to get data for
        year: The year to get data for
        
    Returns:
        List of district budget data dictionaries
    """
    results = []
    
    for district_id in district_ids:
        # Get district with tax codes
        district = TaxDistrict.query.filter(
            TaxDistrict.id == district_id,
            TaxDistrict.year == year
        ).options(
            db.joinedload(TaxDistrict.tax_codes)
        ).first()
        
        if not district:
            continue
            
        # Calculate budget metrics
        total_levy_amount = sum(tc.total_levy_amount or 0 for tc in district.tax_codes)
        total_assessed_value = sum(tc.total_assessed_value or 0 for tc in district.tax_codes)
        
        # Get average levy rate
        avg_levy_rate = 0
        if total_assessed_value > 0:
            avg_levy_rate = (total_levy_amount / total_assessed_value) * 1000
        
        # Get property count
        property_count = Property.query.join(
            TaxCode, Property.tax_code == TaxCode.tax_code
        ).filter(
            TaxCode.tax_district_id == district.id,
            Property.year == district.year,
            TaxCode.year == district.year
        ).count()
        
        # Calculate average tax per property
        avg_tax_per_property = 0
        if property_count > 0:
            avg_tax_per_property = total_levy_amount / property_count
        
        # Get historical data for trends
        historical_data = []
        for tax_code in district.tax_codes:
            historical_rates = TaxCodeHistoricalRate.query.filter(
                TaxCodeHistoricalRate.tax_code_id == tax_code.id
            ).order_by(TaxCodeHistoricalRate.year).all()
            
            for rate in historical_rates:
                historical_data.append({
                    'year': rate.year,
                    'levy_rate': rate.levy_rate,
                    'levy_amount': rate.levy_amount,
                    'total_assessed_value': rate.total_assessed_value
                })
        
        # Compile district budget data
        district_data = {
            'id': district.id,
            'district_name': district.district_name,
            'district_code': district.district_code,
            'district_type': district.district_type,
            'year': district.year,
            'tax_codes': [{
                'id': tc.id,
                'tax_code': tc.tax_code,
                'levy_rate': tc.effective_tax_rate or 0,
                'levy_amount': tc.total_levy_amount or 0,
                'total_assessed_value': tc.total_assessed_value or 0
            } for tc in district.tax_codes],
            'total_levy_amount': total_levy_amount,
            'total_assessed_value': total_assessed_value,
            'avg_levy_rate': avg_levy_rate,
            'property_count': property_count,
            'avg_tax_per_property': avg_tax_per_property,
            'historical_data': historical_data
        }
        
        results.append(district_data)
    
    return results

def simulate_budget_changes(baseline_data, scenario):
    """
    Simulate budget changes based on scenario parameters.
    
    Args:
        baseline_data: List of baseline district budget data
        scenario: Dictionary with simulation parameters
        
    Returns:
        List of simulated district budget data
    """
    # Apply scenario modifications to create simulation data
    simulation_data = []
    
    # Get scenario parameters
    rate_change_percent = scenario.get('rate_change_percent', 0)
    assessed_value_change_percent = scenario.get('assessed_value_change_percent', 0)
    district_type_filters = scenario.get('district_type_filters', [])
    
    for district in baseline_data:
        # Deep copy of district data for simulation
        district_sim = district.copy()
        district_sim['tax_codes'] = [tc.copy() for tc in district['tax_codes']]
        
        # Apply filter - only modify districts of specified types if filters provided
        if district_type_filters and district['district_type'] not in district_type_filters:
            simulation_data.append(district_sim)
            continue
        
        # Apply changes to each tax code
        for tc in district_sim['tax_codes']:
            # Apply rate change
            if rate_change_percent != 0:
                tc['levy_rate'] = tc['levy_rate'] * (1 + rate_change_percent / 100)
            
            # Apply assessed value change
            if assessed_value_change_percent != 0:
                tc['total_assessed_value'] = tc['total_assessed_value'] * (1 + assessed_value_change_percent / 100)
            
            # Recalculate levy amount based on new rate and assessed value
            tc['levy_amount'] = (tc['levy_rate'] / 1000) * tc['total_assessed_value']
        
        # Recalculate district totals
        district_sim['total_levy_amount'] = sum(tc['levy_amount'] for tc in district_sim['tax_codes'])
        district_sim['total_assessed_value'] = sum(tc['total_assessed_value'] for tc in district_sim['tax_codes'])
        
        # Recalculate average levy rate
        district_sim['avg_levy_rate'] = 0
        if district_sim['total_assessed_value'] > 0:
            district_sim['avg_levy_rate'] = (district_sim['total_levy_amount'] / district_sim['total_assessed_value']) * 1000
        
        # Recalculate average tax per property
        if district_sim['property_count'] > 0:
            district_sim['avg_tax_per_property'] = district_sim['total_levy_amount'] / district_sim['property_count']
        
        simulation_data.append(district_sim)
    
    return simulation_data

def calculate_impact_metrics(baseline_data, simulation_data):
    """
    Calculate impact metrics between baseline and simulation.
    
    Args:
        baseline_data: List of baseline district budget data
        simulation_data: List of simulated district budget data
        
    Returns:
        Dictionary with impact analysis metrics
    """
    # Match districts in baseline and simulation
    impact_analysis = {}
    
    for i, baseline in enumerate(baseline_data):
        # Find matching district in simulation data
        for simulation in simulation_data:
            if simulation['id'] == baseline['id']:
                district_id = baseline['id']
                district_name = baseline['district_name']
                
                # Calculate changes
                levy_amount_change = simulation['total_levy_amount'] - baseline['total_levy_amount']
                levy_amount_percent = 0
                if baseline['total_levy_amount'] > 0:
                    levy_amount_percent = (levy_amount_change / baseline['total_levy_amount']) * 100
                
                assessed_value_change = simulation['total_assessed_value'] - baseline['total_assessed_value']
                assessed_value_percent = 0
                if baseline['total_assessed_value'] > 0:
                    assessed_value_percent = (assessed_value_change / baseline['total_assessed_value']) * 100
                
                levy_rate_change = simulation['avg_levy_rate'] - baseline['avg_levy_rate']
                levy_rate_percent = 0
                if baseline['avg_levy_rate'] > 0:
                    levy_rate_percent = (levy_rate_change / baseline['avg_levy_rate']) * 100
                
                tax_per_property_change = simulation['avg_tax_per_property'] - baseline['avg_tax_per_property']
                tax_per_property_percent = 0
                if baseline['avg_tax_per_property'] > 0:
                    tax_per_property_percent = (tax_per_property_change / baseline['avg_tax_per_property']) * 100
                
                # Store impact metrics
                impact_analysis[district_id] = {
                    'district_id': district_id,
                    'district_name': district_name,
                    'district_type': baseline['district_type'],
                    'levy_amount': {
                        'baseline': baseline['total_levy_amount'],
                        'simulation': simulation['total_levy_amount'],
                        'change': levy_amount_change,
                        'percent': levy_amount_percent
                    },
                    'assessed_value': {
                        'baseline': baseline['total_assessed_value'],
                        'simulation': simulation['total_assessed_value'],
                        'change': assessed_value_change,
                        'percent': assessed_value_percent
                    },
                    'levy_rate': {
                        'baseline': baseline['avg_levy_rate'],
                        'simulation': simulation['avg_levy_rate'],
                        'change': levy_rate_change,
                        'percent': levy_rate_percent
                    },
                    'tax_per_property': {
                        'baseline': baseline['avg_tax_per_property'],
                        'simulation': simulation['avg_tax_per_property'],
                        'change': tax_per_property_change,
                        'percent': tax_per_property_percent
                    }
                }
                
                break
    
    return impact_analysis

@budget_impact_bp.route('/api/ai-simulation', methods=['POST'])
def api_ai_budget_simulation():
    """
    API endpoint for AI-powered budget impact simulations with advanced insights.
    
    This endpoint leverages the LevyAuditAgent's AI capabilities to provide more 
    sophisticated budget impact simulations with detailed scenario analysis,
    stakeholder impact assessments, and optimization recommendations.
    
    Returns:
        JSON response with simulation results and AI-generated insights
    """
    try:
        # Validate request has JSON data
        if not request.is_json:
            current_app.logger.warning("Invalid request format for AI simulation - JSON expected")
            return jsonify({
                'success': False,
                'error': 'Invalid request format. JSON expected.',
                'simulation_results': {}
            }), 400
            
        # Get request data
        data = request.json
        
        # Extract parameters from request with validation
        year = data.get('year', datetime.now().year)
        if not isinstance(year, int):
            try:
                year = int(year)
            except (ValueError, TypeError):
                year = datetime.now().year
                current_app.logger.warning(f"Invalid year format in AI simulation: {data.get('year')}, using current year")
                
        district_id = data.get('district_id')
        if district_id is not None and not isinstance(district_id, int):
            try:
                district_id = int(district_id)
            except (ValueError, TypeError):
                current_app.logger.warning(f"Invalid district_id format: {data.get('district_id')}")
                return jsonify({
                    'success': False,
                    'error': 'Invalid district_id format. Integer expected.',
                    'simulation_results': {}
                }), 400
                
        scenario_parameters = data.get('scenario_parameters', {})
        if not isinstance(scenario_parameters, dict):
            current_app.logger.warning(f"Invalid scenario_parameters format: {type(scenario_parameters)}")
            return jsonify({
                'success': False,
                'error': 'Invalid scenario_parameters format. Dictionary expected.',
                'simulation_results': {}
            }), 400
            
        multi_year = data.get('multi_year', False)
        sensitivity_analysis = data.get('sensitivity_analysis', False)
        
        # Check if MCP Army is available
        try:
            from utils.mcp_agent_manager import get_agent, AgentNotAvailableError
        except ImportError:
            current_app.logger.error("MCP agent manager import failed")
            return jsonify({
                'success': False,
                'error': 'MCP agent manager not available',
                'simulation_results': {}
            }), 500
            
        # Import required modules for MCP
        try:
            from flask import current_app
        except ImportError:
            return jsonify({
                'success': False,
                'error': 'Required Flask imports not available',
                'simulation_results': {}
            }), 500
            
        # Check if MCP is enabled
        MCP_ARMY_ENABLED = current_app.config.get('MCP_ARMY_ENABLED', False)
        MCP_INTEGRATED = current_app.config.get('MCP_INTEGRATED', False)
        
        mcp_army_available = (MCP_ARMY_ENABLED or MCP_INTEGRATED) and get_agent is not None
        
        if not mcp_army_available:
            current_app.logger.warning("MCP Army not available for AI budget impact simulation")
            
            # Fall back to standard simulation
            # Get baseline data for comparison
            if district_id:
                district_ids = [district_id]
            else:
                # If no district specified, use all districts for the year
                districts = TaxDistrict.query.filter(TaxDistrict.year == year).all()
                district_ids = [d.id for d in districts]
                
            baseline_data = get_district_budget_data(district_ids, year)
            
            # Apply scenario modifications to create simulation data
            simulation_data = simulate_budget_changes(baseline_data, scenario_parameters)
            
            # Calculate impact metrics
            impact_analysis = calculate_impact_metrics(baseline_data, simulation_data)
            
            return jsonify({
                'success': True,
                'baseline': baseline_data,
                'simulation': simulation_data,
                'impact': impact_analysis,
                'note': 'Standard simulation used (AI capabilities not available)'
            })
        
        # Get the Levy Audit Agent
        try:
            levy_audit_agent = get_agent('Lev')
            if not levy_audit_agent:
                current_app.logger.warning("Levy Audit Agent not available")
                return jsonify({
                    'success': False, 
                    'error': 'Required audit agent not available',
                    'simulation_results': {}
                })
            
            # Execute the budget impact simulation
            current_app.logger.info(f"Running AI budget impact simulation")
            simulation_result = levy_audit_agent.execute_capability(
                'simulate_budget_impact',
                {
                    'district_id': district_id,
                    'scenario_parameters': scenario_parameters,
                    'year': year,
                    'multi_year': multi_year,
                    'sensitivity_analysis': sensitivity_analysis
                }
            )
            
            if 'error' in simulation_result:
                return jsonify({
                    'success': False,
                    'error': simulation_result['error'],
                    'simulation_results': {}
                })
            
            # Add additional metadata
            simulation_result['generated_at'] = datetime.now().isoformat()
            
            # Log the activity
            try:
                from models import db, DataQualityActivity
                
                activity = DataQualityActivity(
                    activity_type='SIMULATION',
                    title='AI Budget Impact Simulation Run',
                    description=f'Executed {"multi-year" if multi_year else "single-year"} budget impact simulation {"with sensitivity analysis" if sensitivity_analysis else ""}',
                    user_id=current_app.config.get('TESTING_USER_ID', 1),
                    entity_type='BudgetImpactSimulation',
                    icon='calculator',
                    icon_class='success'
                )
                db.session.add(activity)
                db.session.commit()
            except Exception as log_error:
                current_app.logger.warning(f"Could not log simulation activity: {str(log_error)}")
            
            # Sanitize the simulation results before sending to browser
            sanitized_simulation_result = sanitize_mcp_insights(simulation_result)
            
            # Extract optimization recommendations if they exist
            optimization_recommendations = {}
            try:
                if 'ai_insights' in sanitized_simulation_result and 'optimization_recommendations' in sanitized_simulation_result['ai_insights']:
                    optimization_recommendations = sanitized_simulation_result['ai_insights']['optimization_recommendations']
            except Exception as extract_error:
                current_app.logger.warning(f"Error extracting optimization recommendations: {str(extract_error)}")
                # Provide fallback recommendations
                optimization_recommendations = {
                    "property_value_growth": 2.0,
                    "new_construction_growth": 1.5,
                    "exemption_rate": 0.5,
                    "tax_rate_adjustment": 1.0,
                    "compliance_rate": 98.0,
                    "collection_efficiency": 97.0,
                    "explanation": "These are default recommended values. Please rerun the AI simulation for customized recommendations."
                }
            
            return jsonify({
                'success': True,
                'simulation_results': sanitized_simulation_result,
                'optimization_recommendations': optimization_recommendations
            })
            
        except AgentNotAvailableError:
            current_app.logger.warning("Agent not available error")
            return jsonify({
                'success': False,
                'error': 'Levy Audit Agent not available',
                'simulation_results': {}
            })
            
        except Exception as agent_error:
            error_msg = f"Agent error: {str(agent_error)}"
            current_app.logger.error(f"Error executing budget impact simulation: {str(agent_error)}")
            return jsonify({
                'success': False,
                'error': sanitize_html(error_msg),
                'simulation_results': {}
            })
    
    except Exception as e:
        error_msg = str(e)
        current_app.logger.error(f"Error in AI budget impact simulation route: {error_msg}")
        return jsonify({
            'success': False,
            'error': sanitize_html(error_msg),
            'simulation_results': {}
        }), 500