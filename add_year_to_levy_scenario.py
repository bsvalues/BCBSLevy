"""
Migration script to add the year column to the levy_scenario table.

This script adds the year column to the levy_scenario table.
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
    Add the year column to the levy_scenario table if it doesn't exist.
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
        
        # Add year column if it doesn't exist
        if 'year' not in columns:
            print("Adding 'year' column to levy_scenario table...")
            conn.execute(text('ALTER TABLE levy_scenario ADD COLUMN year INTEGER'))
            
            # Set a default value to match base_year for existing records
            conn.execute(text('UPDATE levy_scenario SET year = base_year WHERE base_year IS NOT NULL'))
            conn.execute(text('UPDATE levy_scenario SET year = 2025 WHERE year IS NULL'))
            
            # Create index on year column
            conn.execute(text('CREATE INDEX idx_levy_scenario_year ON levy_scenario (year)'))
            
            print("Added 'year' column to levy_scenario table.")
        
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
    print(f"Running migration to add year column to levy_scenario table...")
    run_migration()
    print(f"Migration complete.")