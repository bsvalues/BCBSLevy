"""
Sanitization utilities for the LevyMaster system.

These functions help sanitize data before displaying it in the UI or using it
in sensitive operations to prevent security issues like XSS attacks.
"""

import re
import html
from typing import Any, Dict, List, Union


def sanitize_html(text: str) -> str:
    """
    Sanitize a string to prevent XSS attacks by escaping HTML entities.
    
    Args:
        text: The input string to sanitize
        
    Returns:
        Sanitized string with HTML entities escaped
    """
    if not text:
        return ""
    return html.escape(str(text))


def sanitize_mcp_insights(insights: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize AI-generated insights to prevent XSS attacks.
    
    Args:
        insights: Dictionary containing AI-generated insights
        
    Returns:
        Sanitized insights dictionary
    """
    if not insights:
        return {}
    
    sanitized = {}
    
    # Sanitize scalar values
    for key in insights:
        if isinstance(insights[key], str):
            sanitized[key] = sanitize_html(insights[key])
        elif isinstance(insights[key], (int, float, bool)) or insights[key] is None:
            sanitized[key] = insights[key]
        elif isinstance(insights[key], list):
            if key in ["key_insights", "stakeholder_impacts", "recommendations"]:
                # These are lists of dictionaries
                sanitized[key] = sanitize_list_of_dicts(insights[key])
            elif key == "implementation_considerations":
                # This is a list of strings
                sanitized[key] = [sanitize_html(item) for item in insights[key]]
            else:
                # Default list handling
                sanitized[key] = sanitize_list(insights[key])
        elif isinstance(insights[key], dict):
            # Handle optimal_scenario specially
            if key == "optimal_scenario":
                sanitized[key] = sanitize_optimal_scenario(insights[key])
            else:
                sanitized[key] = sanitize_dict(insights[key])
        else:
            # Default to string conversion and sanitization for unknown types
            sanitized[key] = sanitize_html(str(insights[key]))
    
    return sanitized


def sanitize_list(items: List[Any]) -> List[Any]:
    """
    Sanitize a list of items.
    
    Args:
        items: List of items to sanitize
        
    Returns:
        Sanitized list
    """
    sanitized = []
    for item in items:
        if isinstance(item, str):
            sanitized.append(sanitize_html(item))
        elif isinstance(item, (int, float, bool)) or item is None:
            sanitized.append(item)
        elif isinstance(item, list):
            sanitized.append(sanitize_list(item))
        elif isinstance(item, dict):
            sanitized.append(sanitize_dict(item))
        else:
            # Default to string conversion and sanitization for unknown types
            sanitized.append(sanitize_html(str(item)))
    
    return sanitized


def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize a dictionary.
    
    Args:
        data: Dictionary to sanitize
        
    Returns:
        Sanitized dictionary
    """
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_html(value)
        elif isinstance(value, (int, float, bool)) or value is None:
            sanitized[key] = value
        elif isinstance(value, list):
            sanitized[key] = sanitize_list(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        else:
            # Default to string conversion and sanitization for unknown types
            sanitized[key] = sanitize_html(str(value))
    
    return sanitized


def sanitize_list_of_dicts(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sanitize a list of dictionaries.
    
    Args:
        items: List of dictionaries to sanitize
        
    Returns:
        Sanitized list of dictionaries
    """
    sanitized = []
    for item in items:
        if isinstance(item, dict):
            sanitized.append(sanitize_dict(item))
        else:
            # Skip non-dict items
            continue
    
    return sanitized


def sanitize_optimal_scenario(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize the optimal scenario dictionary.
    
    Args:
        scenario: Optimal scenario dictionary to sanitize
        
    Returns:
        Sanitized optimal scenario dictionary
    """
    sanitized = {}
    
    # Handle numeric values
    for key in ["rate_change", "value_change"]:
        if key in scenario:
            try:
                sanitized[key] = float(scenario[key])
            except (ValueError, TypeError):
                sanitized[key] = 0.0
    
    # Handle justification text
    if "justification" in scenario:
        sanitized["justification"] = sanitize_html(scenario["justification"])
    
    return sanitized