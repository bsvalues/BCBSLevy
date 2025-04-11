"""
Search utilities for the Levy Calculation System.

This module provides functions for intelligent search with fuzzy matching
and autocomplete functionality across various entity types in the system.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from fuzzywuzzy import fuzz, process
from sqlalchemy import or_, and_, func

from models import (
    User, TaxDistrict, TaxCode, Property, TaxCodeHistoricalRate, 
    LevyRate, LevyScenario, Forecast
)

logger = logging.getLogger(__name__)

# Define search fields for each model
SEARCH_CONFIG = {
    'user': {
        'model': User,
        'fields': ['username', 'email', 'first_name', 'last_name'],
        'label_field': 'username',
        'id_field': 'id',
        'additional_fields': ['email', 'full_name', 'is_admin'],
        'type_label': 'User',
    },
    'tax_district': {
        'model': TaxDistrict,
        'fields': ['district_name', 'district_code', 'district_type', 'county', 'state'],
        'label_field': 'district_name',
        'id_field': 'id',
        'additional_fields': ['district_code', 'district_type', 'county', 'state'],
        'type_label': 'Tax District',
    },
    'tax_code': {
        'model': TaxCode,
        'fields': ['tax_code', 'description'],
        'label_field': 'tax_code',
        'id_field': 'id',
        'additional_fields': ['description', 'total_assessed_value', 'total_levy_amount'],
        'type_label': 'Tax Code',
    },
    'property': {
        'model': Property,
        'fields': ['property_id', 'owner_name', 'property_address', 'city'],
        'label_field': 'property_id',
        'id_field': 'id',
        'additional_fields': ['property_address', 'city', 'state', 'assessed_value'],
        'type_label': 'Property',
    },
    'levy_scenario': {
        'model': LevyScenario,
        'fields': ['name', 'description'],
        'label_field': 'name',
        'id_field': 'id',
        'additional_fields': ['description', 'base_year', 'target_year'],
        'type_label': 'Levy Scenario',
    },
    'forecast': {
        'model': Forecast,
        'fields': ['name', 'description', 'model_type'],
        'label_field': 'name',
        'id_field': 'id',
        'additional_fields': ['description', 'model_type', 'base_year'],
        'type_label': 'Forecast',
    },
}


def build_search_query(model: Any, query_text: str, config: Dict[str, Any], year: Optional[int] = None) -> Tuple[Any, List[str]]:
    """
    Build a database query with all necessary filters for searching.
    
    Args:
        model: SQLAlchemy model class to query
        query_text: Text to search for
        config: Search configuration for the model
        year: Optional year filter (for models with year field)
        
    Returns:
        Tuple containing:
            - SQLAlchemy query object
            - List of field names being searched
    """
    search_fields = config['fields']
    conditions = []
    
    # Split query into words for multi-word search
    query_words = query_text.lower().split()
    
    # Build LIKE conditions for each search field and each word
    for field_name in search_fields:
        field = getattr(model, field_name)
        # For each word in the query, create a condition
        for word in query_words:
            conditions.append(func.lower(field).contains(word))
    
    # Create the base query
    base_query = model.query.filter(or_(*conditions))
    
    # Add year filter if applicable and provided
    if year is not None and hasattr(model, 'year'):
        base_query = base_query.filter(model.year == year)
    
    return base_query, search_fields


def search_entities(
    query_text: str, 
    entity_types: List[str] = None, 
    year: Optional[int] = None,
    limit: int = 10, 
    min_score: int = 60
) -> List[Dict[str, Any]]:
    """
    Search for entities across specified entity types.
    
    Args:
        query_text: Text to search for
        entity_types: List of entity types to search, or None for all
        year: Optional year filter for year-specific models
        limit: Maximum number of results per entity type
        min_score: Minimum similarity score (0-100) for fuzzy matching
        
    Returns:
        List of dictionaries containing search results
    """
    if not query_text:
        return []
    
    if not entity_types:
        entity_types = list(SEARCH_CONFIG.keys())
    
    results = []
    query_text = query_text.strip()
    
    # Search each entity type
    for entity_type in entity_types:
        if entity_type not in SEARCH_CONFIG:
            logger.warning(f"Unknown entity type requested in search: {entity_type}")
            continue
            
        config = SEARCH_CONFIG[entity_type]
        model = config['model']
        
        try:
            # Build and execute the database query
            query, search_fields = build_search_query(model, query_text, config, year)
            db_results = query.limit(limit * 3).all()  # Get more than needed for fuzzy filtering
            
            # Apply fuzzy matching to the database results
            processed_results = process_results(
                db_results, 
                query_text, 
                search_fields, 
                config, 
                min_score=min_score
            )
            
            # Take top results up to limit
            entity_results = processed_results[:limit]
            results.extend(entity_results)
            
        except Exception as e:
            logger.error(f"Error searching {entity_type}: {str(e)}")
    
    # Sort results by score (descending)
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return results


def process_results(
    db_results: List[Any], 
    query_text: str, 
    search_fields: List[str], 
    config: Dict[str, Any],
    min_score: int = 60
) -> List[Dict[str, Any]]:
    """
    Process database results with fuzzy matching to improve relevance.
    
    Args:
        db_results: List of database model instances
        query_text: Original search query text
        search_fields: List of fields that were searched
        config: Search configuration for the model
        min_score: Minimum similarity score (0-100) for fuzzy matching
        
    Returns:
        List of dictionaries containing processed search results
    """
    processed_results = []
    
    label_field = config['label_field']
    id_field = config['id_field']
    additional_fields = config.get('additional_fields', [])
    type_label = config.get('type_label', 'Item')
    
    for item in db_results:
        best_score = 0
        best_match_field = None
        
        # Check each searchable field for the best fuzzy match
        for field_name in search_fields:
            field_value = getattr(item, field_name, None)
            if field_value:
                if isinstance(field_value, (int, float)):
                    field_value = str(field_value)
                
                # Use token_set_ratio to handle partial matches well
                score = fuzz.token_set_ratio(query_text.lower(), str(field_value).lower())
                
                if score > best_score:
                    best_score = score
                    best_match_field = field_name
        
        # If the match is good enough, add to results
        if best_score >= min_score:
            result_item = {
                'id': getattr(item, id_field),
                'label': getattr(item, label_field),
                'score': best_score,
                'type': type_label,
                'matched_field': best_match_field,
                'entity_type': config['model'].__tablename__,
            }
            
            # Add additional fields if available
            for field in additional_fields:
                value = getattr(item, field, None)
                if hasattr(item, field):
                    result_item[field] = value
            
            processed_results.append(result_item)
    
    # Sort by score (descending)
    processed_results.sort(key=lambda x: x['score'], reverse=True)
    
    return processed_results


def autocomplete(
    query_prefix: str, 
    entity_type: str, 
    field: str = None, 
    year: Optional[int] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Provide autocomplete suggestions for a given prefix.
    
    Args:
        query_prefix: Beginning text to match against
        entity_type: Type of entity to search
        field: Specific field to query, or None for default fields
        year: Optional year filter for year-specific models
        limit: Maximum number of suggestions to return
        
    Returns:
        List of dictionaries containing autocomplete suggestions
    """
    if not query_prefix or entity_type not in SEARCH_CONFIG:
        return []
    
    config = SEARCH_CONFIG[entity_type]
    model = config['model']
    label_field = config['label_field']
    id_field = config['id_field']
    
    # Determine which fields to use for autocomplete
    autocomplete_fields = [field] if field and hasattr(model, field) else [label_field]
    
    # Build query conditions
    conditions = []
    for field_name in autocomplete_fields:
        field = getattr(model, field_name)
        # Use LIKE for prefix matching
        conditions.append(func.lower(field).startswith(query_prefix.lower()))
    
    # Create and execute query
    query = model.query.filter(or_(*conditions))
    
    # Add year filter if applicable
    if year is not None and hasattr(model, 'year'):
        query = query.filter(model.year == year)
    
    # Execute query and limit results
    db_results = query.limit(limit).all()
    
    # Format results
    suggestions = []
    for item in db_results:
        suggestion = {
            'id': getattr(item, id_field),
            'value': getattr(item, label_field),
            'label': getattr(item, label_field),
            'entity_type': entity_type,
        }
        
        # Add the matched field value if different from label
        for field_name in autocomplete_fields:
            if field_name != label_field:
                suggestion[field_name] = getattr(item, field_name)
        
        suggestions.append(suggestion)
    
    return suggestions