"""
Utility functions for detailed statutory compliance checks.

This module provides functions to analyze property tax data for compliance with
statutory requirements and limitations.
"""
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime

from app import db
from models import TaxCode, Property, TaxDistrict, ImportLog, ExportLog

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define statutory requirements and limits
STATUTORY_REQUIREMENTS = {
    'max_regular_levy_rate': 5.90,  # Maximum regular levy rate per $1,000 of assessed value
    'max_annual_increase': 0.01,    # Maximum 1% annual levy increase
    'max_consolidated_rate': 10.0,  # Maximum consolidated levy rate per $1,000 for all districts
    'senior_exemption_threshold': 40000,  # Income threshold for senior exemption
    'filing_deadline': {
        'month': 11,  # November
        'day': 30
    },
    'special_levy_voting_requirement': 0.60,  # 60% voter approval required for special levies
    'banked_capacity_expiration_years': 5  # Banked capacity typically expires after 5 years
}

def check_levy_rates_compliance(tax_codes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Check if levy rates comply with statutory limits.
    
    Args:
        tax_codes: List of tax code dictionaries with rate information
        
    Returns:
        Dictionary containing compliance check results
    """
    compliance_results = {
        'compliant': True,
        'regular_levy_compliance': [],
        'consolidated_levy_compliance': [],
        'summary': {
            'total_tax_codes': len(tax_codes),
            'compliant_tax_codes': 0,
            'non_compliant_tax_codes': 0
        }
    }
    
    for tax_code in tax_codes:
        code = tax_code.get('code')
        levy_rate = tax_code.get('levy_rate', 0)
        previous_rate = tax_code.get('previous_year_rate', 0)
        
        # Check regular levy rate against maximum
        regular_levy_compliant = levy_rate <= STATUTORY_REQUIREMENTS['max_regular_levy_rate']
        
        # Check annual increase against 101% limit
        annual_increase_compliant = True
        if previous_rate and previous_rate > 0:
            increase_ratio = levy_rate / previous_rate
            annual_increase_compliant = increase_ratio <= (1 + STATUTORY_REQUIREMENTS['max_annual_increase'])
        
        # Add to compliance results
        code_compliance = {
            'code': code,
            'levy_rate': levy_rate,
            'previous_rate': previous_rate,
            'regular_levy_compliant': regular_levy_compliant,
            'annual_increase_compliant': annual_increase_compliant,
            'compliant': regular_levy_compliant and annual_increase_compliant,
            'issues': []
        }
        
        if not regular_levy_compliant:
            code_compliance['issues'].append(
                f"Levy rate {levy_rate:.4f} exceeds maximum regular levy rate of {STATUTORY_REQUIREMENTS['max_regular_levy_rate']:.2f}"
            )
        
        if not annual_increase_compliant:
            increase_percentage = ((levy_rate / previous_rate) - 1) * 100 if previous_rate else 0
            code_compliance['issues'].append(
                f"Annual increase of {increase_percentage:.2f}% exceeds maximum allowed increase of {STATUTORY_REQUIREMENTS['max_annual_increase'] * 100:.1f}%"
            )
        
        compliance_results['regular_levy_compliance'].append(code_compliance)
        
        if code_compliance['compliant']:
            compliance_results['summary']['compliant_tax_codes'] += 1
        else:
            compliance_results['summary']['non_compliant_tax_codes'] += 1
            compliance_results['compliant'] = False
    
    # Check consolidated levy rates by district
    district_levy_rates = {}
    tax_codes_by_district = {}
    
    # Get all tax districts
    districts = db.session.query(TaxDistrict).all()
    
    for district in districts:
        district_id = district.tax_district_id
        levy_code = district.levy_code
        
        if district_id not in district_levy_rates:
            district_levy_rates[district_id] = 0
            tax_codes_by_district[district_id] = []
        
        # Find tax code
        for tax_code in tax_codes:
            if tax_code.get('code') == levy_code:
                district_levy_rates[district_id] += tax_code.get('levy_rate', 0)
                tax_codes_by_district[district_id].append(levy_code)
    
    # Check consolidated levy rates
    for district_id, total_rate in district_levy_rates.items():
        consolidated_compliant = total_rate <= STATUTORY_REQUIREMENTS['max_consolidated_rate']
        
        district_compliance = {
            'district_id': district_id,
            'total_levy_rate': total_rate,
            'tax_codes': tax_codes_by_district.get(district_id, []),
            'compliant': consolidated_compliant
        }
        
        if not consolidated_compliant:
            district_compliance['issue'] = (
                f"Consolidated levy rate of {total_rate:.4f} exceeds "
                f"maximum of {STATUTORY_REQUIREMENTS['max_consolidated_rate']:.2f}"
            )
            compliance_results['compliant'] = False
        
        compliance_results['consolidated_levy_compliance'].append(district_compliance)
    
    return compliance_results


def check_filing_deadline_compliance() -> Dict[str, Any]:
    """
    Check if levy filings are on track to meet statutory deadlines.
    
    Returns:
        Dictionary containing deadline compliance information
    """
    today = datetime.now()
    deadline_month = STATUTORY_REQUIREMENTS['filing_deadline']['month']
    deadline_day = STATUTORY_REQUIREMENTS['filing_deadline']['day']
    
    # Calculate days until deadline
    deadline_date = datetime(today.year, deadline_month, deadline_day)
    if today > deadline_date:
        # If past deadline for this year, use next year
        deadline_date = datetime(today.year + 1, deadline_month, deadline_day)
    
    days_remaining = (deadline_date - today).days
    
    # Check if required data is present for filing
    tax_codes_count = TaxCode.query.count()
    properties_count = Property.query.count()
    tax_districts_count = TaxDistrict.query.count()
    
    # Get most recent imports
    recent_property_imports = ImportLog.query.filter_by(import_type='property').order_by(ImportLog.import_date.desc()).first()
    recent_district_imports = ImportLog.query.filter_by(import_type='district').order_by(ImportLog.import_date.desc()).first()
    
    data_complete = tax_codes_count > 0 and properties_count > 0 and tax_districts_count > 0
    data_recent = False
    
    if recent_property_imports and recent_district_imports:
        # Check if imports were within last 90 days
        property_import_age = (today - recent_property_imports.import_date).days
        district_import_age = (today - recent_district_imports.import_date).days
        data_recent = property_import_age <= 90 and district_import_age <= 90
    
    filing_status = {
        'deadline_date': deadline_date.strftime('%Y-%m-%d'),
        'days_remaining': days_remaining,
        'data_complete': data_complete,
        'data_recent': data_recent,
        'tax_codes_count': tax_codes_count,
        'properties_count': properties_count,
        'tax_districts_count': tax_districts_count,
        'recent_property_import': recent_property_imports.import_date.strftime('%Y-%m-%d') if recent_property_imports else None,
        'recent_district_import': recent_district_imports.import_date.strftime('%Y-%m-%d') if recent_district_imports else None,
        'status': 'compliant' if days_remaining > 30 or (data_complete and data_recent) else 'at_risk',
        'warnings': []
    }
    
    # Add specific warnings
    if days_remaining <= 30:
        filing_status['warnings'].append(f"Only {days_remaining} days remaining until filing deadline")
    
    if not data_complete:
        filing_status['warnings'].append(f"Missing required data: Tax Codes: {tax_codes_count}, Properties: {properties_count}, Tax Districts: {tax_districts_count}")
    
    if not data_recent:
        filing_status['warnings'].append("Data may be outdated. Consider refreshing imports before filing")
    
    return filing_status


def check_banked_capacity_compliance() -> Dict[str, Any]:
    """
    Check banked capacity usage and compliance with statutory limits.
    
    Returns:
        Dictionary containing banked capacity compliance information
    """
    # Analyze banked capacity usage
    # This would require historical data about unused levy capacity
    
    # Since full banked capacity tracking requires historical data that may not be 
    # available in the current database schema, we'll implement a simplified version
    
    # Get tax codes with rates
    tax_codes = TaxCode.query.all()
    
    banked_capacity_results = {
        'tax_codes_with_banked_capacity': [],
        'expiring_capacity': [],
        'total_banked_capacity': 0.0,
        'recommendations': []
    }
    
    current_year = datetime.now().year
    
    for tax_code in tax_codes:
        if tax_code.levy_rate and tax_code.previous_year_rate:
            # Calculate potential banked capacity
            # When the actual increase is less than the allowed 1%
            actual_ratio = tax_code.levy_rate / tax_code.previous_year_rate if tax_code.previous_year_rate else 1.0
            max_allowed_ratio = 1 + STATUTORY_REQUIREMENTS['max_annual_increase']
            
            if actual_ratio < max_allowed_ratio:
                # Calculate banked capacity as dollar amount based on total assessed value
                available_increase = max_allowed_ratio - actual_ratio
                potential_banked_amount = 0
                
                if tax_code.total_assessed_value:
                    potential_banked_amount = (tax_code.total_assessed_value / 1000) * tax_code.previous_year_rate * available_increase
                
                banked_capacity_results['tax_codes_with_banked_capacity'].append({
                    'code': tax_code.code,
                    'actual_increase_ratio': actual_ratio,
                    'potential_banked_capacity_rate': tax_code.previous_year_rate * available_increase,
                    'potential_banked_amount': potential_banked_amount,
                    'expiration_year': current_year + STATUTORY_REQUIREMENTS['banked_capacity_expiration_years']
                })
                
                banked_capacity_results['total_banked_capacity'] += potential_banked_amount
    
    # Add recommendations
    if banked_capacity_results['tax_codes_with_banked_capacity']:
        banked_capacity_results['recommendations'].append(
            "Consider tracking banked capacity formally to ensure it doesn't expire unused"
        )
        
        if banked_capacity_results['total_banked_capacity'] > 100000:
            banked_capacity_results['recommendations'].append(
                f"Substantial banked capacity available (${banked_capacity_results['total_banked_capacity']:,.2f}). "
                "Review future levy needs and consider utilizing banked capacity strategically"
            )
    
    return banked_capacity_results


def generate_compliance_report() -> Dict[str, Any]:
    """
    Generate a comprehensive compliance report with all statutory checks.
    
    Returns:
        Dictionary containing the complete compliance report
    """
    # Get all tax codes with their data
    tax_codes = db.session.query(TaxCode).all()
    tax_code_data = [
        {
            'code': tc.code,
            'levy_rate': tc.levy_rate,
            'previous_year_rate': tc.previous_year_rate,
            'total_assessed_value': tc.total_assessed_value,
            'levy_amount': tc.levy_amount
        }
        for tc in tax_codes
    ]
    
    # Run all compliance checks
    levy_compliance = check_levy_rates_compliance(tax_code_data)
    filing_compliance = check_filing_deadline_compliance()
    banked_capacity_compliance = check_banked_capacity_compliance()
    
    # Compile overall compliance status
    overall_compliant = levy_compliance['compliant'] and filing_compliance['status'] == 'compliant'
    
    # Calculate compliance percentage
    total_checks = levy_compliance['summary']['total_tax_codes'] * 2  # Regular and annual increase checks
    passed_checks = levy_compliance['summary']['compliant_tax_codes'] * 2  # For fully compliant tax codes
    
    # Add partial compliance for tax codes that passed one check but not both
    for code_compliance in levy_compliance['regular_levy_compliance']:
        if not code_compliance['compliant']:  # Already counted fully compliant ones
            if code_compliance['regular_levy_compliant']:
                passed_checks += 1
            if code_compliance['annual_increase_compliant']:
                passed_checks += 1
    
    compliance_percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    
    # Generate full report
    report = {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'overall_compliant': overall_compliant,
        'compliance_percentage': compliance_percentage,
        'statutory_limits': STATUTORY_REQUIREMENTS,
        'levy_rate_compliance': levy_compliance,
        'filing_deadline_compliance': filing_compliance,
        'banked_capacity_compliance': banked_capacity_compliance,
        'critical_issues': [],
        'warnings': [],
        'recommendations': []
    }
    
    # Extract critical issues, warnings and recommendations
    if levy_compliance['summary']['non_compliant_tax_codes'] > 0:
        report['critical_issues'].append(
            f"{levy_compliance['summary']['non_compliant_tax_codes']} tax codes have statutory compliance issues"
        )
        
        # Add specific issues
        for code_compliance in levy_compliance['regular_levy_compliance']:
            if not code_compliance['compliant']:
                for issue in code_compliance['issues']:
                    report['critical_issues'].append(f"Tax code {code_compliance['code']}: {issue}")
    
    # Add filing deadline warnings
    for warning in filing_compliance['warnings']:
        report['warnings'].append(warning)
    
    # Add banked capacity recommendations
    for recommendation in banked_capacity_compliance['recommendations']:
        report['recommendations'].append(recommendation)
    
    # Add general recommendations based on overall report
    if compliance_percentage < 95:
        report['recommendations'].append(
            "Review all non-compliant tax codes and adjust levy rates to meet statutory requirements"
        )
    
    if compliance_percentage == 100 and not filing_compliance['warnings']:
        report['recommendations'].append(
            "All compliance checks passed. Consider running levy scenarios to optimize revenue while maintaining compliance"
        )
    
    return report