"""
Advanced Historical Analysis Utilities

This module provides various analytical functions for processing historical tax rate data,
including statistical analysis, trend forecasting, anomaly detection, and comparison reporting.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
from sqlalchemy import func, and_, or_, desc, asc
import json
import logging

from app import db
from models import TaxCode, TaxCodeHistoricalRate, TaxDistrict

# Configure logging
logger = logging.getLogger(__name__)

def compute_basic_statistics(tax_code: str, years: Optional[List[int]] = None) -> Dict:
    """
    Compute basic statistical measures for a tax code's historical rates.
    
    Args:
        tax_code: The tax code to analyze
        years: Optional list of years to include in analysis
        
    Returns:
        Dictionary with statistical measures and historical data
    """
    try:
        # Get tax code ID
        tax_code_obj = TaxCode.query.filter_by(tax_code=tax_code).first()
        if not tax_code_obj:
            return {'error': f'Tax code {tax_code} not found'}
        
        # Build query
        query = TaxCodeHistoricalRate.query.filter_by(tax_code_id=tax_code_obj.id)
        
        # Filter by years if provided
        if years:
            query = query.filter(TaxCodeHistoricalRate.year.in_(years))
        
        # Get historical rates
        historical_rates = query.order_by(TaxCodeHistoricalRate.year.asc()).all()
        
        if not historical_rates:
            return {
                'tax_code': tax_code,
                'error': 'No historical data found',
                'historical_data': []
            }
        
        # Extract data into arrays
        years_data = [rate.year for rate in historical_rates]
        rates_data = [rate.levy_rate for rate in historical_rates]
        
        # Convert to numpy arrays for calculations
        rates_array = np.array(rates_data)
        
        # Compute basic statistics
        statistics = {
            'tax_code': tax_code,
            'years': years_data,
            'count': len(rates_data),
            'mean': float(np.mean(rates_array)),
            'median': float(np.median(rates_array)),
            'std_dev': float(np.std(rates_array)),
            'min': float(np.min(rates_array)),
            'max': float(np.max(rates_array)),
            'range': float(np.max(rates_array) - np.min(rates_array)),
            'first_year': years_data[0],
            'last_year': years_data[-1],
            'first_rate': float(rates_data[0]),
            'last_rate': float(rates_data[-1]),
            'total_change': float(rates_data[-1] - rates_data[0]),
            'percent_change': float((rates_data[-1] - rates_data[0]) / rates_data[0] * 100) if rates_data[0] != 0 else None,
            'historical_data': [
                {'year': rate.year, 'levy_rate': rate.levy_rate}
                for rate in historical_rates
            ]
        }
        
        # Calculate compound annual growth rate (CAGR)
        if years_data[-1] > years_data[0] and rates_data[0] > 0:
            year_diff = years_data[-1] - years_data[0]
            statistics['cagr'] = float((pow(rates_data[-1] / rates_data[0], 1 / year_diff) - 1) * 100)
        else:
            statistics['cagr'] = None
        
        return statistics
    
    except Exception as e:
        logger.error(f"Error in compute_basic_statistics: {str(e)}")
        return {'error': str(e)}

def compute_moving_average(tax_code: str, window_size: int = 3, years: Optional[List[int]] = None) -> Dict:
    """
    Compute moving average of historical rates for a tax code.
    
    Args:
        tax_code: The tax code to analyze
        window_size: Size of the moving average window
        years: Optional list of years to include in analysis
        
    Returns:
        Dictionary with moving averages and historical data
    """
    try:
        # Get tax code ID
        tax_code_obj = TaxCode.query.filter_by(tax_code=tax_code).first()
        if not tax_code_obj:
            return {'error': f'Tax code {tax_code} not found'}
        
        # Build query
        query = TaxCodeHistoricalRate.query.filter_by(tax_code_id=tax_code_obj.id)
        
        # Filter by years if provided
        if years:
            query = query.filter(TaxCodeHistoricalRate.year.in_(years))
        
        # Get historical rates
        historical_rates = query.order_by(TaxCodeHistoricalRate.year.asc()).all()
        
        if not historical_rates:
            return {
                'tax_code': tax_code,
                'error': 'No historical data found',
                'historical_data': []
            }
        
        # Extract data into arrays
        years_data = [rate.year for rate in historical_rates]
        rates_data = [rate.levy_rate for rate in historical_rates]
        
        # Compute moving average
        moving_avgs = []
        for i in range(len(rates_data) - window_size + 1):
            window = rates_data[i:i+window_size]
            avg = sum(window) / window_size
            moving_avgs.append({
                'year_range': f"{years_data[i]}-{years_data[i+window_size-1]}",
                'moving_avg': float(avg)
            })
        
        result = {
            'tax_code': tax_code,
            'window_size': window_size,
            'moving_averages': moving_avgs,
            'historical_data': [
                {'year': rate.year, 'levy_rate': rate.levy_rate}
                for rate in historical_rates
            ]
        }
        
        return result
    
    except Exception as e:
        logger.error(f"Error in compute_moving_average: {str(e)}")
        return {'error': str(e)}

def forecast_future_rates(
    tax_code: str, 
    forecast_years: int = 3, 
    method: str = 'linear',
    years: Optional[List[int]] = None
) -> Dict:
    """
    Forecast future levy rates for a tax code.
    
    Args:
        tax_code: The tax code to forecast
        forecast_years: Number of years to forecast
        method: Forecasting method ('linear', 'average', 'weighted', 'exponential', 'arima')
        years: Optional list of years to include in analysis
        
    Returns:
        Dictionary with forecasted values and quality metrics
    """
    try:
        # Get tax code ID
        tax_code_obj = TaxCode.query.filter_by(tax_code=tax_code).first()
        if not tax_code_obj:
            return {'error': f'Tax code {tax_code} not found'}
        
        # Build query
        query = TaxCodeHistoricalRate.query.filter_by(tax_code_id=tax_code_obj.id)
        
        # Filter by years if provided
        if years:
            query = query.filter(TaxCodeHistoricalRate.year.in_(years))
        
        # Get historical rates
        historical_rates = query.order_by(TaxCodeHistoricalRate.year.asc()).all()
        
        if not historical_rates:
            return {
                'tax_code': tax_code,
                'error': 'No historical data found',
                'historical_data': []
            }
        
        if len(historical_rates) < 2:
            return {
                'tax_code': tax_code,
                'error': 'Insufficient historical data for forecasting',
                'historical_data': [
                    {'year': rate.year, 'levy_rate': rate.levy_rate}
                    for rate in historical_rates
                ]
            }
        
        # Extract data into arrays
        years_data = np.array([rate.year for rate in historical_rates])
        rates_data = np.array([rate.levy_rate for rate in historical_rates])
        
        # Forecast future rates
        forecasted_years = np.array([max(years_data) + i + 1 for i in range(forecast_years)])
        forecasted_rates = []
        forecast_method_details = {}
        
        # Linear regression
        if method == 'linear':
            # Reshape for scikit-learn style
            X = years_data.reshape(-1, 1)
            y = rates_data
            
            # Simple linear regression
            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict future rates
            X_future = forecasted_years.reshape(-1, 1)
            forecasted_rates = model.predict(X_future)
            
            # Compute R^2 for quality assessment
            y_pred = model.predict(X)
            r2 = 1 - (np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2))
            
            forecast_method_details = {
                'method': 'linear',
                'coefficient': float(model.coef_[0]),
                'intercept': float(model.intercept_),
                'r_squared': float(r2),
                'equation': f"y = {model.coef_[0]:.6f}x + {model.intercept_:.6f}"
            }
        
        # Simple average
        elif method == 'average':
            avg_rate = np.mean(rates_data)
            forecasted_rates = np.full(forecasted_years.shape, avg_rate)
            
            forecast_method_details = {
                'method': 'average',
                'average_value': float(avg_rate)
            }
        
        # Weighted average (more recent years have higher weight)
        elif method == 'weighted':
            weights = np.arange(1, len(rates_data) + 1)
            weighted_avg = np.sum(rates_data * weights) / np.sum(weights)
            forecasted_rates = np.full(forecasted_years.shape, weighted_avg)
            
            forecast_method_details = {
                'method': 'weighted',
                'weighted_average': float(weighted_avg)
            }
        
        # Exponential smoothing
        elif method == 'exponential':
            from statsmodels.tsa.holtwinters import ExponentialSmoothing
            
            # Convert to pandas series for statsmodels
            rate_series = pd.Series(rates_data, index=years_data)
            
            # Try different trend types and select the best
            best_aic = float('inf')
            best_model = None
            for trend_type in ['add', 'mul']:
                try:
                    model = ExponentialSmoothing(
                        rate_series, 
                        trend=trend_type, 
                        seasonal=None
                    ).fit()
                    
                    if model.aic < best_aic:
                        best_aic = model.aic
                        best_model = model
                except:
                    continue
            
            if best_model is None:
                # Fallback to simple model if none worked
                best_model = ExponentialSmoothing(
                    rate_series, 
                    trend='add', 
                    seasonal=None
                ).fit()
            
            # Forecast
            forecast = best_model.forecast(forecast_years)
            forecasted_rates = forecast.values
            
            forecast_method_details = {
                'method': 'exponential',
                'trend_type': best_model.params['trend'],
                'alpha': float(best_model.params['smoothing_level']),
                'beta': float(best_model.params['smoothing_trend']),
                'aic': float(best_model.aic) if hasattr(best_model, 'aic') else None
            }
        
        # ARIMA model
        elif method == 'arima':
            from statsmodels.tsa.arima.model import ARIMA
            
            # Convert to pandas series for statsmodels
            rate_series = pd.Series(rates_data, index=years_data)
            
            # Try different orders and select best
            best_aic = float('inf')
            best_model = None
            for p in range(0, 2):
                for d in range(0, 2):
                    for q in range(0, 2):
                        try:
                            model = ARIMA(rate_series, order=(p, d, q))
                            model_fit = model.fit()
                            
                            if model_fit.aic < best_aic:
                                best_aic = model_fit.aic
                                best_model = model_fit
                        except:
                            continue
            
            if best_model is None:
                # Fallback to simple model if none worked
                best_model = ARIMA(rate_series, order=(1, 0, 0)).fit()
            
            # Forecast
            forecast = best_model.forecast(forecast_years)
            forecasted_rates = forecast.values
            
            forecast_method_details = {
                'method': 'arima',
                'order': best_model.model.order,
                'aic': float(best_model.aic)
            }
        
        # Format forecast results
        forecast_results = []
        for i, year in enumerate(forecasted_years):
            forecast_results.append({
                'year': int(year),
                'levy_rate': float(forecasted_rates[i]),
                'is_forecast': True
            })
        
        # Prepare historical data for the response
        historical_data = [
            {'year': rate.year, 'levy_rate': rate.levy_rate, 'is_forecast': False}
            for rate in historical_rates
        ]
        
        result = {
            'tax_code': tax_code,
            'forecast_method': method,
            'forecast_years': forecast_years,
            'forecast_details': forecast_method_details,
            'forecasted_data': forecast_results,
            'historical_data': historical_data,
            'all_data': historical_data + forecast_results
        }
        
        return result
    
    except Exception as e:
        logger.error(f"Error in forecast_future_rates: {str(e)}")
        return {'error': str(e), 'tax_code': tax_code}

def detect_levy_rate_anomalies(
    tax_code: str, 
    threshold: float = 2.0,
    years: Optional[List[int]] = None
) -> Dict:
    """
    Detect anomalies in historical levy rates using Z-score.
    
    Args:
        tax_code: The tax code to analyze
        threshold: Z-score threshold for anomaly detection
        years: Optional list of years to include in analysis
        
    Returns:
        Dictionary with anomaly detection results
    """
    try:
        # Get tax code ID
        tax_code_obj = TaxCode.query.filter_by(tax_code=tax_code).first()
        if not tax_code_obj:
            return {'error': f'Tax code {tax_code} not found'}
        
        # Build query
        query = TaxCodeHistoricalRate.query.filter_by(tax_code_id=tax_code_obj.id)
        
        # Filter by years if provided
        if years:
            query = query.filter(TaxCodeHistoricalRate.year.in_(years))
        
        # Get historical rates
        historical_rates = query.order_by(TaxCodeHistoricalRate.year.asc()).all()
        
        if not historical_rates:
            return {
                'tax_code': tax_code,
                'error': 'No historical data found',
                'all_rates': []
            }
        
        if len(historical_rates) < 3:
            return {
                'tax_code': tax_code,
                'error': 'Insufficient data for anomaly detection',
                'all_rates': [
                    {'year': rate.year, 'levy_rate': rate.levy_rate}
                    for rate in historical_rates
                ]
            }
        
        # Extract data into arrays
        years_data = np.array([rate.year for rate in historical_rates])
        rates_data = np.array([rate.levy_rate for rate in historical_rates])
        
        # Calculate annual percent changes
        changes = []
        for i in range(1, len(rates_data)):
            if rates_data[i-1] != 0:
                pct_change = (rates_data[i] - rates_data[i-1]) / rates_data[i-1] * 100
                changes.append({
                    'from_year': int(years_data[i-1]),
                    'to_year': int(years_data[i]),
                    'from_rate': float(rates_data[i-1]),
                    'to_rate': float(rates_data[i]),
                    'change': float(rates_data[i] - rates_data[i-1]),
                    'percent_change': float(pct_change)
                })
        
        # Calculate Z-scores for the percent changes
        if changes:
            pct_changes = np.array([c['percent_change'] for c in changes])
            mean_change = np.mean(pct_changes)
            std_change = np.std(pct_changes)
            
            if std_change > 0:  # Avoid division by zero
                for i, change in enumerate(changes):
                    z_score = (change['percent_change'] - mean_change) / std_change
                    changes[i]['z_score'] = float(z_score)
                    changes[i]['is_anomaly'] = abs(z_score) > threshold
            else:
                # If standard deviation is zero, no anomalies (all changes are the same)
                for i in range(len(changes)):
                    changes[i]['z_score'] = 0.0
                    changes[i]['is_anomaly'] = False
        
        # Detect level shifts (step changes in the levy rate)
        level_shifts = []
        if len(rates_data) >= 3:
            avg_abs_change = np.mean(np.abs(np.diff(rates_data)))
            for i in range(1, len(rates_data) - 1):
                before_avg = np.mean(rates_data[:i])
                after_avg = np.mean(rates_data[i+1:])
                shift_magnitude = abs(after_avg - before_avg)
                
                if shift_magnitude > avg_abs_change * threshold:
                    level_shifts.append({
                        'year': int(years_data[i]),
                        'before_avg': float(before_avg),
                        'after_avg': float(after_avg),
                        'shift_magnitude': float(shift_magnitude),
                        'shift_percent': float(shift_magnitude / before_avg * 100) if before_avg != 0 else None
                    })
        
        # Prepare rate data with anomaly flags
        all_rates = []
        for i, rate in enumerate(historical_rates):
            rate_info = {
                'year': rate.year,
                'levy_rate': rate.levy_rate,
                'is_anomaly': False,
                'anomaly_type': None
            }
            
            # Check if this year is part of a change anomaly
            for change in changes:
                if change.get('is_anomaly', False) and change['to_year'] == rate.year:
                    rate_info['is_anomaly'] = True
                    rate_info['anomaly_type'] = 'change'
                    rate_info['z_score'] = change.get('z_score')
                    break
            
            # Check if this year is a level shift
            for shift in level_shifts:
                if shift['year'] == rate.year:
                    rate_info['is_anomaly'] = True
                    rate_info['anomaly_type'] = 'level_shift'
                    rate_info['shift_magnitude'] = shift['shift_magnitude']
                    break
            
            all_rates.append(rate_info)
        
        result = {
            'tax_code': tax_code,
            'threshold': threshold,
            'avg_rate': float(np.mean(rates_data)),
            'std_dev': float(np.std(rates_data)),
            'changes': changes,
            'level_shifts': level_shifts,
            'all_rates': all_rates,
            'anomaly_count': sum(1 for r in all_rates if r['is_anomaly'])
        }
        
        return result
    
    except Exception as e:
        logger.error(f"Error in detect_levy_rate_anomalies: {str(e)}")
        return {'error': str(e), 'tax_code': tax_code}

def aggregate_by_district(
    district_id: int, 
    years: Optional[List[int]] = None
) -> Dict:
    """
    Aggregate historical levy data by tax district.
    
    Args:
        district_id: The tax district ID to analyze
        years: Optional list of years to include in analysis
        
    Returns:
        Dictionary with aggregated district data
    """
    try:
        # Get the district
        district = TaxDistrict.query.get(district_id)
        if not district:
            return {'error': f'Tax district with ID {district_id} not found'}
        
        # Get tax codes for this district
        tax_codes = TaxCode.query.filter_by(tax_district_id=district_id).all()
        if not tax_codes:
            return {
                'district_id': district_id,
                'district_name': district.district_name,
                'error': 'No tax codes found for this district',
                'tax_codes': []
            }
        
        tax_code_ids = [tc.id for tc in tax_codes]
        
        # Build query for historical rates
        query = TaxCodeHistoricalRate.query.filter(
            TaxCodeHistoricalRate.tax_code_id.in_(tax_code_ids)
        )
        
        # Filter by years if provided
        if years:
            query = query.filter(TaxCodeHistoricalRate.year.in_(years))
        
        # Get historical rates
        historical_rates = query.all()
        
        if not historical_rates:
            return {
                'district_id': district_id,
                'district_name': district.district_name,
                'error': 'No historical rates found for this district',
                'tax_codes': [tc.tax_code for tc in tax_codes]
            }
        
        # Group rates by year and tax code
        data_by_year = {}
        for rate in historical_rates:
            year = rate.year
            tax_code = next((tc.tax_code for tc in tax_codes if tc.id == rate.tax_code_id), None)
            
            if not tax_code:
                continue
            
            if year not in data_by_year:
                data_by_year[year] = {
                    'year': year,
                    'rates': [],
                    'tax_codes': []
                }
            
            data_by_year[year]['rates'].append(rate.levy_rate)
            data_by_year[year]['tax_codes'].append(tax_code)
        
        # Calculate aggregate statistics by year
        yearly_stats = []
        for year, data in sorted(data_by_year.items()):
            rates = np.array(data['rates'])
            
            yearly_stats.append({
                'year': year,
                'tax_code_count': len(data['tax_codes']),
                'tax_codes': data['tax_codes'],
                'min_rate': float(np.min(rates)),
                'max_rate': float(np.max(rates)),
                'avg_rate': float(np.mean(rates)),
                'median_rate': float(np.median(rates)),
                'std_dev': float(np.std(rates)),
                'total_rate': float(np.sum(rates))
            })
        
        # Calculate year-over-year changes
        for i in range(1, len(yearly_stats)):
            prev_avg = yearly_stats[i-1]['avg_rate']
            curr_avg = yearly_stats[i]['avg_rate']
            
            yearly_stats[i]['change_from_prev'] = float(curr_avg - prev_avg)
            yearly_stats[i]['percent_change'] = float((curr_avg - prev_avg) / prev_avg * 100) if prev_avg != 0 else None
        
        result = {
            'district_id': district_id,
            'district_name': district.district_name,
            'district_code': district.district_code,
            'tax_codes': [tc.tax_code for tc in tax_codes],
            'yearly_stats': yearly_stats
        }
        
        return result
    
    except Exception as e:
        logger.error(f"Error in aggregate_by_district: {str(e)}")
        return {'error': str(e), 'district_id': district_id}

def generate_comparison_report(
    start_year: int,
    end_year: int,
    min_change_threshold: float = 0.01
) -> Dict:
    """
    Generate a comparison report between two years.
    
    Args:
        start_year: The starting year for comparison
        end_year: The ending year for comparison
        min_change_threshold: Minimum change threshold to include in report (as decimal)
        
    Returns:
        Dictionary with detailed comparison report
    """
    try:
        if start_year >= end_year:
            return {'error': 'End year must be greater than start year'}
        
        # Get all tax codes with rates in both years
        start_query = db.session.query(
            TaxCodeHistoricalRate.tax_code_id
        ).filter_by(year=start_year)
        
        end_query = db.session.query(
            TaxCodeHistoricalRate.tax_code_id
        ).filter_by(year=end_year)
        
        common_tax_code_ids = db.session.query(
            TaxCodeHistoricalRate.tax_code_id
        ).filter(
            TaxCodeHistoricalRate.tax_code_id.in_(start_query),
            TaxCodeHistoricalRate.tax_code_id.in_(end_query)
        ).all()
        
        if not common_tax_code_ids:
            return {
                'start_year': start_year,
                'end_year': end_year,
                'error': 'No tax codes found with rates in both years',
                'comparisons': []
            }
        
        # Extract IDs from result tuples
        common_tax_code_ids = [tc_id[0] for tc_id in common_tax_code_ids]
        
        # Get the tax codes
        tax_codes = TaxCode.query.filter(TaxCode.id.in_(common_tax_code_ids)).all()
        
        # Create a lookup for tax code objects
        tax_code_lookup = {tc.id: tc for tc in tax_codes}
        
        # Get rates for start year
        start_rates = TaxCodeHistoricalRate.query.filter(
            TaxCodeHistoricalRate.tax_code_id.in_(common_tax_code_ids),
            TaxCodeHistoricalRate.year == start_year
        ).all()
        
        # Create a lookup for start year rates
        start_rates_lookup = {rate.tax_code_id: rate for rate in start_rates}
        
        # Get rates for end year
        end_rates = TaxCodeHistoricalRate.query.filter(
            TaxCodeHistoricalRate.tax_code_id.in_(common_tax_code_ids),
            TaxCodeHistoricalRate.year == end_year
        ).all()
        
        # Generate comparisons
        comparisons = []
        for rate in end_rates:
            tax_code_id = rate.tax_code_id
            if tax_code_id not in start_rates_lookup:
                continue
            
            start_rate = start_rates_lookup[tax_code_id]
            tax_code_obj = tax_code_lookup.get(tax_code_id)
            
            if not tax_code_obj:
                continue
            
            abs_change = rate.levy_rate - start_rate.levy_rate
            percent_change = (abs_change / start_rate.levy_rate * 100) if start_rate.levy_rate != 0 else None
            
            # Only include if change exceeds threshold
            if abs(abs_change) >= min_change_threshold * start_rate.levy_rate or abs_change == 0:
                comparisons.append({
                    'tax_code': tax_code_obj.tax_code,
                    'tax_code_id': tax_code_id,
                    'start_year': start_year,
                    'end_year': end_year,
                    'start_rate': start_rate.levy_rate,
                    'end_rate': rate.levy_rate,
                    'absolute_change': float(abs_change),
                    'percent_change': float(percent_change) if percent_change is not None else None,
                    'change_direction': 'increase' if abs_change > 0 else ('decrease' if abs_change < 0 else 'unchanged')
                })
        
        # Sort by percent change (descending)
        comparisons.sort(key=lambda x: abs(x.get('percent_change', 0) or 0), reverse=True)
        
        # Calculate summary statistics
        if comparisons:
            changes = np.array([c['absolute_change'] for c in comparisons])
            percent_changes = np.array([c['percent_change'] for c in comparisons if c['percent_change'] is not None])
            
            summary = {
                'count': len(comparisons),
                'increased_count': sum(1 for c in comparisons if c['change_direction'] == 'increase'),
                'decreased_count': sum(1 for c in comparisons if c['change_direction'] == 'decrease'),
                'unchanged_count': sum(1 for c in comparisons if c['change_direction'] == 'unchanged'),
                'avg_abs_change': float(np.mean(changes)),
                'median_abs_change': float(np.median(changes)),
                'max_increase': float(np.max(changes)),
                'max_decrease': float(np.min(changes)),
                'avg_pct_change': float(np.mean(percent_changes)) if len(percent_changes) > 0 else None
            }
        else:
            summary = {
                'count': 0,
                'increased_count': 0,
                'decreased_count': 0,
                'unchanged_count': 0
            }
        
        result = {
            'start_year': start_year,
            'end_year': end_year,
            'year_difference': end_year - start_year,
            'min_change_threshold': min_change_threshold * 100,  # Convert to percentage
            'summary': summary,
            'comparisons': comparisons
        }
        
        return result
    
    except Exception as e:
        logger.error(f"Error in generate_comparison_report: {str(e)}")
        return {'error': str(e)}