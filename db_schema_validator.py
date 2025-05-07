#!/usr/bin/env python
"""
Database Schema Validator

This script validates that the SQLAlchemy models match the actual database schema.
It helps identify mismatches between code and database to prevent runtime errors.

Usage:
    python db_schema_validator.py [--repair]

Options:
    --repair    Attempt to generate migration code to fix mismatches
"""

import argparse
import inspect
import logging
import sys
from importlib import import_module

from sqlalchemy import Column, inspect as sa_inspect

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_model_classes(module_name='models'):
    """Get all SQLAlchemy model classes from the specified module."""
    try:
        module = import_module(module_name)
        model_classes = []
        
        for name, obj in inspect.getmembers(module):
            # Check if it's a class and has __tablename__ attribute (SQLAlchemy model)
            if inspect.isclass(obj) and hasattr(obj, '__tablename__'):
                model_classes.append(obj)
                
        return model_classes
    except ImportError:
        logger.error(f"Could not import module '{module_name}'")
        return []

def get_db_table_info(table_name, db_engine):
    """Get table info from the database."""
    try:
        inspector = sa_inspect(db_engine)
        columns = inspector.get_columns(table_name)
        return {col['name']: col for col in columns}
    except Exception as e:
        logger.error(f"Error inspecting table '{table_name}': {str(e)}")
        return {}

def validate_model_against_db(model_class, db_engine):
    """Validate a model class against the actual database table."""
    table_name = model_class.__tablename__
    db_columns = get_db_table_info(table_name, db_engine)
    
    if not db_columns:
        logger.error(f"Table '{table_name}' does not exist in the database")
        return False, []
    
    mismatches = []
    
    # Check model columns against database columns
    for column_name, column in model_class.__table__.columns.items():
        if column_name not in db_columns:
            mismatches.append({
                'type': 'missing_in_db',
                'model_column': column_name,
                'table': table_name
            })
        # We could add more detailed type checking here
    
    # Check database columns against model columns
    for db_column_name in db_columns:
        if db_column_name not in model_class.__table__.columns:
            mismatches.append({
                'type': 'missing_in_model',
                'db_column': db_column_name,
                'table': table_name
            })
    
    return len(mismatches) == 0, mismatches

def generate_repair_code(mismatches):
    """Generate Python code to repair model mismatches."""
    code = []
    
    for mismatch in mismatches:
        if mismatch['type'] == 'missing_in_model':
            # Generate code to add column to model
            table = mismatch['table']
            db_column = mismatch['db_column']
            code.append(f"# Add missing column '{db_column}' to model for table '{table}'")
            code.append(f"# {db_column} = db.Column(db.String, nullable=True)  # Adjust type as needed")
            code.append("")
        elif mismatch['type'] == 'missing_in_db':
            # Generate migration to add column to database
            table = mismatch['table']
            model_column = mismatch['model_column']
            code.append(f"# Create migration to add column '{model_column}' to table '{table}'")
            code.append(f"# op.add_column('{table}', sa.Column('{model_column}', sa.String(), nullable=True))")
            code.append("")
    
    return "\n".join(code)

def main():
    parser = argparse.ArgumentParser(description='Validate SQLAlchemy models against database schema')
    parser.add_argument('--repair', action='store_true', help='Generate repair code for mismatches')
    args = parser.parse_args()
    
    try:
        # Import app to get the SQLAlchemy instance
        from app import app, db
        
        with app.app_context():
            model_classes = get_model_classes()
            
            if not model_classes:
                logger.error("No SQLAlchemy models found")
                return 1
            
            logger.info(f"Found {len(model_classes)} model classes")
            
            all_valid = True
            all_mismatches = []
            
            for model_class in model_classes:
                logger.info(f"Validating model '{model_class.__name__}'")
                valid, mismatches = validate_model_against_db(model_class, db.engine)
                
                if not valid:
                    all_valid = False
                    all_mismatches.extend(mismatches)
                    logger.warning(f"Model '{model_class.__name__}' has schema mismatches")
                    
                    for mismatch in mismatches:
                        if mismatch['type'] == 'missing_in_db':
                            logger.warning(f"Column '{mismatch['model_column']}' exists in model but not in database table '{mismatch['table']}'")
                        elif mismatch['type'] == 'missing_in_model':
                            logger.warning(f"Column '{mismatch['db_column']}' exists in database table '{mismatch['table']}' but not in model")
                
            if all_valid:
                logger.info("All models match database schema")
                return 0
            else:
                logger.error(f"Found {len(all_mismatches)} schema mismatches")
                
                if args.repair:
                    repair_code = generate_repair_code(all_mismatches)
                    if repair_code:
                        print("\nSuggested repair code:")
                        print("-" * 80)
                        print(repair_code)
                        print("-" * 80)
                return 1
                
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())