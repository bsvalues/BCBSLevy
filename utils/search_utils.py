"""
Search utilities for the Levy Calculation System.

This module provides utility functions for the intelligent search functionality
with fuzzy matching and autocomplete capabilities.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Union, Tuple, Optional

from fuzzywuzzy import fuzz, process
from flask_login import current_user
from sqlalchemy import or_, and_, func

from models import (
    TaxDistrict, 
    TaxCode, 
    Property, 
    User, 
    ImportLog,
    ExportLog,
    db
)

# Configure logger
logger = logging.getLogger(__name__)

# Define search entity types and their models
SEARCHABLE_ENTITIES = {
    'tax_district': TaxDistrict,
    'tax_code': TaxCode,
    'property': Property,
    'user': User,
    'import_log': ImportLog,
    'export_log': ExportLog
}

# Entity-specific search fields for both exact and fuzzy matching
ENTITY_SEARCH_FIELDS = {
    'tax_district': {
        'exact': ['tax_district_id', 'levy_code'],
        'fuzzy': ['name', 'description', 'county'],
        'exclude': ['created_at', 'updated_at', 'created_by_id', 'updated_by_id']
    },
    'tax_code': {
        'exact': ['tax_code_id', 'levy_code'],
        'fuzzy': ['description'],
        'exclude': ['created_at', 'updated_at', 'created_by_id', 'updated_by_id']
    },
    'property': {
        'exact': ['property_id', 'parcel_number'],
        'fuzzy': ['address', 'owner_name', 'description'],
        'exclude': ['created_at', 'updated_at', 'created_by_id', 'updated_by_id']
    },
    'user': {
        'exact': ['email'],
        'fuzzy': ['username', 'first_name', 'last_name', 'role'],
        'exclude': ['password_hash', 'created_at', 'updated_at']
    },
    'import_log': {
        'exact': ['file_name', 'status', 'import_type'],
        'fuzzy': ['notes'],
        'exclude': ['created_at', 'updated_at', 'created_by_id', 'updated_by_id']
    },
    'export_log': {
        'exact': ['file_name', 'status', 'export_type'],
        'fuzzy': ['notes'],
        'exclude': ['created_at', 'updated_at', 'created_by_id', 'updated_by_id']
    }
}

# Display formats for search results
ENTITY_DISPLAY_FORMATS = {
    'tax_district': {
        'title': '{name}',
        'subtitle': 'District ID: {tax_district_id}',
        'description': '{description}',
        'url': '/data/districts/{id}'
    },
    'tax_code': {
        'title': 'Tax Code {tax_code_id}',
        'subtitle': 'Levy Code: {levy_code}',
        'description': '{description}',
        'url': '/data/tax-codes/{id}'
    },
    'property': {
        'title': '{address}',
        'subtitle': 'Parcel: {parcel_number}',
        'description': 'Owner: {owner_name}',
        'url': '/data/properties/{id}'
    },
    'user': {
        'title': '{username}',
        'subtitle': '{email}',
        'description': '{role}',
        'url': '/admin/users/{id}'
    },
    'import_log': {
        'title': '{file_name}',
        'subtitle': '{import_type} Import - {status}',
        'description': 'Imported on {created_at}',
        'url': '/data/imports/{id}'
    },
    'export_log': {
        'title': '{file_name}',
        'subtitle': '{export_type} Export - {status}',
        'description': 'Exported on {created_at}',
        'url': '/data/exports/{id}'
    }
}

def search_entities(
    query: str, 
    entity_types: List[str] = None, 
    year: int = None, 
    limit: int = 5,
    min_score: int = 60
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Search across multiple entity types using intelligent fuzzy matching.
    
    Args:
        query: The search query text
        entity_types: List of entity types to search, defaults to all if None
        year: Optional year filter for entities with year attribute
        limit: Maximum number of results to return per entity type
        min_score: Minimum score (0-100) for fuzzy matching results
        
    Returns:
        Dictionary of entity types with their search results
    """
    if not query:
        return {}
    
    # Default to all entity types if none specified
    if not entity_types:
        entity_types = list(SEARCHABLE_ENTITIES.keys())
    else:
        # Filter to valid entity types only
        entity_types = [t for t in entity_types if t in SEARCHABLE_ENTITIES]
    
    # Initialize results dictionary
    results = {}
    
    # Log the search attempt
    logger.info(f"Search query: '{query}' in types: {entity_types}, year: {year}")
    
    # Perform search for each requested entity type
    for entity_type in entity_types:
        model = SEARCHABLE_ENTITIES[entity_type]
        
        # Get the relevant fields for this entity
        fields = ENTITY_SEARCH_FIELDS[entity_type]
        
        # Build the base query
        base_query = db.session.query(model)
        
        # Add year filter if applicable and the model has a year attribute
        if year and hasattr(model, 'year'):
            base_query = base_query.filter(model.year == year)
        
        # First try exact matching on exact fields
        exact_matches = []
        exact_conditions = []
        
        for field in fields['exact']:
            if hasattr(model, field):
                exact_conditions.append(getattr(model, field) == query)
        
        if exact_conditions:
            exact_query = base_query.filter(or_(*exact_conditions))
            exact_matches = exact_query.limit(limit).all()
        
        # Then try partial matching for text fields (LIKE queries)
        partial_matches = []
        partial_conditions = []
        
        for field in fields['exact'] + fields['fuzzy']:
            if hasattr(model, field):
                attr = getattr(model, field)
                # Only apply LIKE to string-based columns
                if hasattr(attr, 'type') and hasattr(attr.type, 'python_type') and \
                   issubclass(attr.type.python_type, str):
                    partial_conditions.append(attr.ilike(f"%{query}%"))
        
        if partial_conditions:
            # Exclude any already found exact matches
            if exact_matches:
                ids_to_exclude = [item.id for item in exact_matches]
                partial_query = base_query.filter(
                    and_(
                        or_(*partial_conditions),
                        model.id.notin_(ids_to_exclude)
                    )
                )
            else:
                partial_query = base_query.filter(or_(*partial_conditions))
            
            partial_matches = partial_query.limit(limit).all()
        
        # Get all objects and perform fuzzy matching in Python for remaining slots
        remaining_slots = limit - len(exact_matches) - len(partial_matches)
        
        fuzzy_matches = []
        if remaining_slots > 0 and fields['fuzzy']:
            # Get potential candidates (limiting to a reasonable number)
            candidates_query = base_query
            
            # Exclude already matched items
            ids_to_exclude = [item.id for item in exact_matches + partial_matches]
            if ids_to_exclude:
                candidates_query = candidates_query.filter(model.id.notin_(ids_to_exclude))
            
            candidates = candidates_query.limit(100).all()  # Reasonable limit
            
            if candidates:
                # Perform fuzzy matching on candidate objects
                candidate_texts = []
                for candidate in candidates:
                    # Concatenate all fuzzy fields for each candidate
                    texts = []
                    for field in fields['fuzzy']:
                        if hasattr(candidate, field):
                            value = getattr(candidate, field)
                            if value:
                                texts.append(str(value))
                    candidate_texts.append(" ".join(texts))
                
                # Get the best fuzzy matches
                if candidate_texts:
                    fuzzy_results = process.extract(
                        query, 
                        candidate_texts, 
                        limit=remaining_slots, 
                        scorer=fuzz.token_set_ratio
                    )
                    
                    # Only keep matches above min_score
                    for i, (_, score, idx) in enumerate(fuzzy_results):
                        if score >= min_score:
                            fuzzy_matches.append(candidates[idx])
        
        # Combine all matches, prioritizing exact matches
        all_matches = exact_matches + partial_matches + fuzzy_matches
        
        # Deduplicate results by ID
        unique_items = {}
        for item in all_matches:
            if item.id not in unique_items:
                unique_items[item.id] = item
        
        combined_results = list(unique_items.values())
        
        # Format results for consistent display
        formatted_results = []
        for item in combined_results[:limit]:  # Ensure we don't exceed limit
            formatted_result = format_search_result(item, entity_type)
            if formatted_result:
                formatted_results.append(formatted_result)
        
        # Only include entity type in results if we found something
        if formatted_results:
            results[entity_type] = formatted_results
    
    return results

def format_search_result(item: Any, entity_type: str) -> Optional[Dict[str, Any]]:
    """
    Format a database entity into a standardized search result.
    
    Args:
        item: Database entity object
        entity_type: Type of entity
    
    Returns:
        Formatted search result as a dictionary
    """
    if entity_type not in ENTITY_DISPLAY_FORMATS:
        return None
    
    format_template = ENTITY_DISPLAY_FORMATS[entity_type]
    result = {
        'id': item.id,
        'type': entity_type,
        'entity': item
    }
    
    # Apply the format templates
    for key, template in format_template.items():
        if key in ['title', 'subtitle', 'description', 'url']:
            try:
                # Format template with item attributes
                formatted_value = template.format(**{
                    attr: format_attribute_value(getattr(item, attr, None))
                    for attr in dir(item)
                    if not attr.startswith('_') and not callable(getattr(item, attr))
                })
                result[key] = formatted_value
            except (KeyError, AttributeError) as e:
                # Fallback for missing attributes
                result[key] = f"[Format error: {e}]"
    
    return result

def format_attribute_value(value: Any) -> str:
    """
    Format a value for display in search results.
    
    Args:
        value: The value to format
        
    Returns:
        Formatted string representation
    """
    if value is None:
        return "N/A"
    
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    
    return str(value)

def get_autocomplete_suggestions(
    prefix: str,
    entity_type: str = None,
    field: str = None,
    year: int = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get autocomplete suggestions for a given prefix.
    
    Args:
        prefix: The prefix text to autocomplete
        entity_type: The entity type to search
        field: Specific field to match
        year: Year filter (if applicable)
        limit: Maximum number of suggestions
        
    Returns:
        List of autocomplete suggestions
    """
    if not prefix or not entity_type or entity_type not in SEARCHABLE_ENTITIES:
        return []
    
    model = SEARCHABLE_ENTITIES[entity_type]
    fields = ENTITY_SEARCH_FIELDS[entity_type]
    
    # Default to all searchable fields if none specified
    search_fields = []
    if field and hasattr(model, field):
        search_fields = [field]
    else:
        search_fields = fields['exact'] + fields['fuzzy']
    
    # Filter to string-type fields that exist on the model
    valid_fields = []
    for field_name in search_fields:
        if hasattr(model, field_name):
            attr = getattr(model, field_name)
            if hasattr(attr, 'type') and hasattr(attr.type, 'python_type') and \
               issubclass(attr.type.python_type, str):
                valid_fields.append(field_name)
    
    if not valid_fields:
        return []
    
    # Build conditions for autocomplete
    conditions = []
    for field_name in valid_fields:
        attr = getattr(model, field_name)
        conditions.append(attr.ilike(f"{prefix}%"))
    
    # Create base query
    query = db.session.query(model).filter(or_(*conditions))
    
    # Add year filter if applicable
    if year and hasattr(model, 'year'):
        query = query.filter(model.year == year)
    
    # Get results and format for autocomplete
    results = query.limit(limit).all()
    suggestions = []
    
    for item in results:
        # Find which field matched for this item
        matched_field = None
        matched_value = None
        
        for field_name in valid_fields:
            value = getattr(item, field_name)
            str_value = str(value).lower() if value else ""
            
            if str_value.startswith(prefix.lower()):
                matched_field = field_name
                matched_value = str_value
                break
        
        if matched_field and matched_value:
            suggestions.append({
                'id': item.id,
                'type': entity_type,
                'field': matched_field,
                'value': matched_value,
                'display': format_search_result(item, entity_type)
            })
    
    return suggestions

def log_search_activity(
    query: str, 
    entity_types: List[str],
    result_count: int,
    year: Optional[int] = None
) -> None:
    """
    Log search activity for analytics purposes.
    
    Args:
        query: The search query
        entity_types: The entity types searched
        result_count: Number of results found
        year: Optional year filter
    """
    # Import here to avoid circular imports
    from models import UserActionLog
    
    try:
        log_entry = UserActionLog(
            user_id=current_user.id if not current_user.is_anonymous else None,
            action_type='SEARCH',
            module='search',
            action_details={
                'query': query,
                'entity_types': entity_types,
                'year': year,
                'result_count': result_count
            },
            success=True
        )
        
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error logging search activity: {str(e)}")