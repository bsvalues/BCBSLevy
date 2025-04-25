"""
Database verification script.
This script checks database relationships and constraints.
"""
import os
import sys
import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the database connection and models
from main import app, db
from models import *  # This imports all models

def get_all_models():
    """Get all SQLAlchemy models from the application."""
    models = []
    for attr_name in dir(sys.modules['models']):
        attr = getattr(sys.modules['models'], attr_name)
        if isinstance(attr, type) and hasattr(attr, '__tablename__'):
            models.append(attr)
    return models

def check_table_exists(model):
    """Check if the table for the given model exists in the database."""
    table_name = model.__tablename__
    try:
        with db.engine.connect() as conn:
            result = conn.execute(sa.text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{table_name}'
                );
            """))
            exists = result.scalar()
            return exists
    except SQLAlchemyError as e:
        print(f"Error checking if table {table_name} exists: {str(e)}")
        return False

def count_records(model):
    """Count the number of records in the table for the given model."""
    try:
        return db.session.query(model).count()
    except SQLAlchemyError as e:
        print(f"Error counting records for {model.__name__}: {str(e)}")
        return -1

def check_foreign_keys(model):
    """Check foreign key relationships for the given model."""
    issues = []
    table_name = model.__tablename__
    inspector = inspect(db.engine)
    
    try:
        foreign_keys = inspector.get_foreign_keys(table_name)
        for fk in foreign_keys:
            referred_table = fk['referred_table']
            referred_columns = fk['referred_columns']
            constrained_columns = fk['constrained_columns']
            
            # Check for NULL values in FK columns that shouldn't be NULL
            for column in constrained_columns:
                query = f"""
                    SELECT COUNT(*) FROM {table_name}
                    WHERE {column} IS NULL
                """
                result = db.session.execute(sa.text(query)).scalar()
                if result > 0:
                    issues.append(f"Found {result} NULL values in foreign key column {column}")
            
            # Check for orphaned references (FK values that don't exist in parent table)
            for i, column in enumerate(constrained_columns):
                ref_column = referred_columns[i]
                query = f"""
                    SELECT COUNT(*) FROM {table_name} t
                    LEFT JOIN {referred_table} r ON t.{column} = r.{ref_column}
                    WHERE t.{column} IS NOT NULL AND r.{ref_column} IS NULL
                """
                result = db.session.execute(sa.text(query)).scalar()
                if result > 0:
                    issues.append(f"Found {result} orphaned references in {column} to {referred_table}.{ref_column}")
    
    except SQLAlchemyError as e:
        issues.append(f"Error checking foreign keys: {str(e)}")
    
    return issues

def check_unique_constraints(model):
    """Check unique constraints for the given model."""
    issues = []
    inspector = inspect(db.engine)
    table_name = model.__tablename__
    
    try:
        # Get unique constraints
        unique_constraints = inspector.get_unique_constraints(table_name)
        indexes = inspector.get_indexes(table_name)
        
        # Add unique indexes to constraints
        for idx in indexes:
            if idx.get('unique', False):
                constraint = {
                    'name': idx['name'],
                    'column_names': idx['column_names']
                }
                unique_constraints.append(constraint)
        
        # Check for duplicates violating unique constraints
        for constraint in unique_constraints:
            columns = constraint['column_names']
            if not columns:
                continue
                
            columns_str = ', '.join(columns)
            query = f"""
                SELECT {columns_str}, COUNT(*)
                FROM {table_name}
                GROUP BY {columns_str}
                HAVING COUNT(*) > 1
            """
            
            try:
                result = db.session.execute(sa.text(query)).fetchall()
                if result:
                    issues.append(f"Found {len(result)} violations of unique constraint on {columns_str}")
            except SQLAlchemyError as e:
                issues.append(f"Error checking unique constraint {constraint['name']}: {str(e)}")
    
    except SQLAlchemyError as e:
        issues.append(f"Error checking unique constraints: {str(e)}")
    
    return issues

def main():
    """Main function to check database integrity."""
    with app.app_context():
        print("Checking database integrity...")
        models = get_all_models()
        print(f"Found {len(models)} models")
        
        all_issues = []
        
        for model in models:
            print(f"\nChecking {model.__name__}...")
            
            # Check if table exists
            if not check_table_exists(model):
                print(f"❌ Table {model.__tablename__} does not exist!")
                all_issues.append(f"Table {model.__tablename__} does not exist")
                continue
                
            # Count records
            record_count = count_records(model)
            if record_count >= 0:
                print(f"✅ Table {model.__tablename__} exists with {record_count} records")
            else:
                print(f"❌ Error counting records in {model.__tablename__}")
                all_issues.append(f"Error counting records in {model.__tablename__}")
            
            # Check foreign key relationships
            fk_issues = check_foreign_keys(model)
            if fk_issues:
                for issue in fk_issues:
                    print(f"❌ {issue}")
                    all_issues.append(f"{model.__name__}: {issue}")
            else:
                print(f"✅ Foreign key relationships for {model.__name__} are valid")
            
            # Check unique constraints
            unique_issues = check_unique_constraints(model)
            if unique_issues:
                for issue in unique_issues:
                    print(f"❌ {issue}")
                    all_issues.append(f"{model.__name__}: {issue}")
            else:
                print(f"✅ Unique constraints for {model.__name__} are valid")
        
        # Report summary
        print("\n--- Database Integrity Check Summary ---")
        if all_issues:
            print(f"Found {len(all_issues)} issues:")
            for issue in all_issues:
                print(f"  - {issue}")
            return 1
        else:
            print("No issues found. Database integrity looks good!")
            return 0

if __name__ == "__main__":
    sys.exit(main())