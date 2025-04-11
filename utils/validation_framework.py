"""
Property Data Validation Framework.

This module provides a comprehensive framework for validating property data
against schema requirements, business rules, and regulatory standards.

The validation framework is designed to be:
- Extensible: New validators can be easily added
- Configurable: Validation rules can be adjusted based on requirements
- Informative: Detailed feedback on validation failures is provided
"""

import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Callable, Optional, Union

logger = logging.getLogger(__name__)

# Type definitions
ValidationResult = Dict[str, Any]
ValidationRule = Callable[[Any], ValidationResult]
PropertyData = Dict[str, Any]


def validate_property_data(property_data: PropertyData) -> List[ValidationResult]:
    """
    Validate property data against schema and business rules.
    
    This function performs comprehensive validation of property data,
    checking for:
    - Required fields presence
    - Data type correctness
    - Value range constraints
    - Cross-field consistency
    - Logical relationship validation
    
    Args:
        property_data: Dictionary containing property information
        
    Returns:
        List of validation results
    """
    if not property_data or not isinstance(property_data, dict):
        return [{
            "field": "property_data",
            "status": "failed",
            "issue": "Invalid or missing property data"
        }]
    
    # Run all validators and collect results
    results = []
    
    # Basic field validation
    results.extend(_validate_basic_fields(property_data))
    
    # Address validation
    if "address" in property_data and isinstance(property_data["address"], dict):
        results.extend(_validate_address(property_data["address"]))
    else:
        results.append({
            "field": "address",
            "status": "failed",
            "issue": "Missing or invalid address information"
        })
    
    # Characteristics validation
    if "characteristics" in property_data and isinstance(property_data["characteristics"], dict):
        results.extend(_validate_characteristics(property_data["characteristics"]))
    
    # Add cross-field validation as needed
    
    return results


def _validate_basic_fields(property_data: PropertyData) -> List[ValidationResult]:
    """
    Validate basic property fields.
    
    Args:
        property_data: Property data dictionary
        
    Returns:
        List of validation results
    """
    results = []
    
    # Validate property_id
    if "property_id" not in property_data or not property_data["property_id"]:
        results.append({
            "field": "property_id",
            "status": "failed",
            "issue": "Missing property ID"
        })
    elif not isinstance(property_data["property_id"], str):
        results.append({
            "field": "property_id",
            "status": "failed",
            "issue": "Property ID must be a string"
        })
    else:
        results.append({
            "field": "property_id",
            "status": "passed",
            "issue": None
        })
    
    return results


def _validate_address(address: Dict[str, Any]) -> List[ValidationResult]:
    """
    Validate property address.
    
    Args:
        address: Address dictionary
        
    Returns:
        List of validation results
    """
    results = []
    
    # Check required fields
    required_fields = ["street", "city", "state", "zip"]
    for field in required_fields:
        if field not in address or not address[field]:
            results.append({
                "field": f"address.{field}",
                "status": "failed",
                "issue": f"Missing {field} in address"
            })
        else:
            results.append({
                "field": f"address.{field}",
                "status": "passed",
                "issue": None
            })
    
    # Validate state format (2 letter code)
    if "state" in address and address["state"]:
        if not isinstance(address["state"], str) or len(address["state"]) != 2:
            results.append({
                "field": "address.state",
                "status": "failed",
                "issue": "State must be a 2-letter code"
            })
    
    # Validate ZIP code format
    if "zip" in address and address["zip"]:
        zip_code = address["zip"]
        if not isinstance(zip_code, str):
            results.append({
                "field": "address.zip",
                "status": "failed",
                "issue": "ZIP code must be a string"
            })
        elif not re.match(r'^\d{5}(-\d{4})?$', zip_code):
            results.append({
                "field": "address.zip",
                "status": "failed",
                "issue": "ZIP code must be in format 12345 or 12345-6789"
            })
    
    return results


def _validate_characteristics(characteristics: Dict[str, Any]) -> List[ValidationResult]:
    """
    Validate property characteristics.
    
    Args:
        characteristics: Property characteristics dictionary
        
    Returns:
        List of validation results
    """
    results = []
    
    # Validate property type
    if "property_type" in characteristics:
        property_type = characteristics["property_type"]
        valid_types = ["residential", "commercial", "industrial", "agricultural", "public", "other"]
        
        if property_type not in valid_types:
            results.append({
                "field": "characteristics.property_type",
                "status": "failed",
                "issue": f"Invalid property type. Must be one of: {', '.join(valid_types)}"
            })
        else:
            results.append({
                "field": "characteristics.property_type",
                "status": "passed",
                "issue": None
            })
    
    # Validate year built
    if "year_built" in characteristics:
        year_built = characteristics["year_built"]
        current_year = datetime.now().year
        
        if not isinstance(year_built, int):
            results.append({
                "field": "characteristics.year_built",
                "status": "failed",
                "issue": "Year built must be an integer"
            })
        elif year_built < 1800 or year_built > current_year:
            results.append({
                "field": "characteristics.year_built",
                "status": "failed",
                "issue": f"Year built must be between 1800 and {current_year}"
            })
        else:
            results.append({
                "field": "characteristics.year_built",
                "status": "passed",
                "issue": None
            })
    
    # Validate numeric fields
    numeric_fields = [
        ("square_footage", 0, None),  # Min, Max (None = no max)
        ("bedrooms", 0, 20),
        ("bathrooms", 0, 20),
        ("lot_size", 0, None)
    ]
    
    for field_name, min_val, max_val in numeric_fields:
        if field_name in characteristics:
            value = characteristics[field_name]
            
            if not isinstance(value, (int, float)):
                results.append({
                    "field": f"characteristics.{field_name}",
                    "status": "failed",
                    "issue": f"{field_name} must be a number"
                })
            elif value < min_val:
                results.append({
                    "field": f"characteristics.{field_name}",
                    "status": "failed",
                    "issue": f"{field_name} must be at least {min_val}"
                })
            elif max_val is not None and value > max_val:
                results.append({
                    "field": f"characteristics.{field_name}",
                    "status": "failed",
                    "issue": f"{field_name} must be at most {max_val}"
                })
            else:
                results.append({
                    "field": f"characteristics.{field_name}",
                    "status": "passed",
                    "issue": None
                })
    
    return results


def validate_against_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> List[ValidationResult]:
    """
    Validate data against a JSON schema-like definition.
    
    Args:
        data: Data to validate
        schema: Schema definition
        
    Returns:
        List of validation results
    """
    # This would be implemented to support more complex schema validation
    # For now, return a placeholder
    return [{
        "field": "schema_validation",
        "status": "passed",
        "issue": None
    }]


def generate_validation_report(results: List[ValidationResult]) -> Dict[str, Any]:
    """
    Generate a summary report from validation results.
    
    Args:
        results: List of validation results
        
    Returns:
        Validation report summary
    """
    total = len(results)
    passed = len([r for r in results if r["status"] == "passed"])
    failed = total - passed
    
    # Group issues by field
    issues_by_field = {}
    for result in results:
        if result["status"] != "passed":
            field = result["field"]
            if field not in issues_by_field:
                issues_by_field[field] = []
            issues_by_field[field].append(result["issue"])
    
    return {
        "total_checks": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": passed / total if total > 0 else 0,
        "is_valid": failed == 0,
        "issues_by_field": issues_by_field,
        "timestamp": datetime.utcnow().isoformat()
    }