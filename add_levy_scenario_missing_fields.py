"""
Migration script to add missing calculation fields to the levy_scenario table.

This migration adds the target_year, levy_amount, assessed_value_change,
new_construction_value, annexation_value, result_levy_rate, and result_levy_amount
columns to the levy_scenario table.
"""

import os
import sys
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy import create_engine, MetaData, Table, inspect, text
from sqlalchemy.ext.declarative import declarative_base

# Get the database URL from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable not set")
    sys.exit(1)

# Create SQLAlchemy engine and metadata
engine = create_engine(DATABASE_URL)
metadata = MetaData()
Base = declarative_base()

def run_migration():
    """
    Add missing calculation fields to the levy_scenario table if they don't exist.
    """
    inspector = inspect(engine)
    conn = engine.connect()
    trans = conn.begin()
    
    try:
        # Check if the levy_scenario table exists
        if not inspector.has_table('levy_scenario'):
            print("Table 'levy_scenario' does not exist. Migration not needed.")
            return
        
        # Get existing columns
        columns = [column['name'] for column in inspector.get_columns('levy_scenario')]
        print(f"Existing columns in levy_scenario: {columns}")
        
        # Add target_year column if it doesn't exist
        if 'target_year' not in columns:
            print("Adding 'target_year' column to levy_scenario table...")
            conn.execute(text('ALTER TABLE levy_scenario ADD COLUMN target_year INTEGER'))
            
            # Set a default value (base_year for existing rows)
            conn.execute(text('UPDATE levy_scenario SET target_year = base_year + 1'))
            
            print("Added 'target_year' column to levy_scenario table.")
        
        # Add levy_amount column if it doesn't exist
        if 'levy_amount' not in columns:
            print("Adding 'levy_amount' column to levy_scenario table...")
            conn.execute(text('ALTER TABLE levy_scenario ADD COLUMN levy_amount FLOAT'))
            print("Added 'levy_amount' column to levy_scenario table.")
        
        # Add assessed_value_change column if it doesn't exist
        if 'assessed_value_change' not in columns:
            print("Adding 'assessed_value_change' column to levy_scenario table...")
            conn.execute(text('ALTER TABLE levy_scenario ADD COLUMN assessed_value_change FLOAT DEFAULT 0.0'))
            print("Added 'assessed_value_change' column to levy_scenario table.")
        
        # Add new_construction_value column if it doesn't exist
        if 'new_construction_value' not in columns:
            print("Adding 'new_construction_value' column to levy_scenario table...")
            conn.execute(text('ALTER TABLE levy_scenario ADD COLUMN new_construction_value FLOAT DEFAULT 0.0'))
            print("Added 'new_construction_value' column to levy_scenario table.")
        
        # Add annexation_value column if it doesn't exist
        if 'annexation_value' not in columns:
            print("Adding 'annexation_value' column to levy_scenario table...")
            conn.execute(text('ALTER TABLE levy_scenario ADD COLUMN annexation_value FLOAT DEFAULT 0.0'))
            print("Added 'annexation_value' column to levy_scenario table.")
        
        # Add result_levy_rate column if it doesn't exist
        if 'result_levy_rate' not in columns:
            print("Adding 'result_levy_rate' column to levy_scenario table...")
            conn.execute(text('ALTER TABLE levy_scenario ADD COLUMN result_levy_rate FLOAT'))
            print("Added 'result_levy_rate' column to levy_scenario table.")
        
        # Add result_levy_amount column if it doesn't exist
        if 'result_levy_amount' not in columns:
            print("Adding 'result_levy_amount' column to levy_scenario table...")
            conn.execute(text('ALTER TABLE levy_scenario ADD COLUMN result_levy_amount FLOAT'))
            print("Added 'result_levy_amount' column to levy_scenario table.")
        
        # Add tax_district_id column if it doesn't exist
        if 'tax_district_id' not in columns:
            print("Adding 'tax_district_id' column to levy_scenario table...")
            conn.execute(text('ALTER TABLE levy_scenario ADD COLUMN tax_district_id INTEGER'))
            
            # Add foreign key constraint
            conn.execute(text('ALTER TABLE levy_scenario ADD CONSTRAINT fk_levy_scenario_tax_district FOREIGN KEY (tax_district_id) REFERENCES tax_district (id)'))
            
            print("Added 'tax_district_id' column to levy_scenario table.")
        
        # Commit the transaction
        trans.commit()
        print("Migration completed successfully.")
        
    except Exception as e:
        # Rollback the transaction
        trans.rollback()
        print(f"Error during migration: {str(e)}")
        conn.close()
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    print(f"Running migration to add missing calculation fields to levy_scenario table...")
    run_migration()
    print(f"Migration complete.")