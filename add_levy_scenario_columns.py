"""
Migration script to add missing columns to the levy_scenario table.

This migration adds the user_id, created_by_id, updated_by_id columns to
the levy_scenario table.
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
    Add missing columns to the levy_scenario table if they don't exist.
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
        
        # Add user_id column if it doesn't exist
        if 'user_id' not in columns:
            print("Adding 'user_id' column to levy_scenario table...")
            conn.execute(text('ALTER TABLE levy_scenario ADD COLUMN user_id INTEGER'))
            
            # Set a default value (1 for existing rows)
            conn.execute(text('UPDATE levy_scenario SET user_id = 1'))
            
            # Add foreign key constraint
            conn.execute(text('ALTER TABLE levy_scenario ADD CONSTRAINT fk_levy_scenario_user FOREIGN KEY (user_id) REFERENCES "user" (id)'))
            
            # Make column NOT NULL
            conn.execute(text('ALTER TABLE levy_scenario ALTER COLUMN user_id SET NOT NULL'))
            
            print("Added 'user_id' column to levy_scenario table.")
        
        # Add created_by_id column if it doesn't exist
        if 'created_by_id' not in columns:
            print("Adding 'created_by_id' column to levy_scenario table...")
            conn.execute(text('ALTER TABLE levy_scenario ADD COLUMN created_by_id INTEGER'))
            
            # Set a default value (1 for existing rows)
            conn.execute(text('UPDATE levy_scenario SET created_by_id = 1'))
            
            # Add foreign key constraint
            conn.execute(text('ALTER TABLE levy_scenario ADD CONSTRAINT fk_levy_scenario_created_by FOREIGN KEY (created_by_id) REFERENCES "user" (id)'))
            
            print("Added 'created_by_id' column to levy_scenario table.")
        
        # Add updated_by_id column if it doesn't exist
        if 'updated_by_id' not in columns:
            print("Adding 'updated_by_id' column to levy_scenario table...")
            conn.execute(text('ALTER TABLE levy_scenario ADD COLUMN updated_by_id INTEGER'))
            
            # Set a default value (1 for existing rows)
            conn.execute(text('UPDATE levy_scenario SET updated_by_id = 1'))
            
            # Add foreign key constraint
            conn.execute(text('ALTER TABLE levy_scenario ADD CONSTRAINT fk_levy_scenario_updated_by FOREIGN KEY (updated_by_id) REFERENCES "user" (id)'))
            
            print("Added 'updated_by_id' column to levy_scenario table.")
            
        # Add created_at column if it doesn't exist
        if 'created_at' not in columns:
            print("Adding 'created_at' column to levy_scenario table...")
            conn.execute(text('ALTER TABLE levy_scenario ADD COLUMN created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP'))
            print("Added 'created_at' column to levy_scenario table.")
            
        # Add updated_at column if it doesn't exist
        if 'updated_at' not in columns:
            print("Adding 'updated_at' column to levy_scenario table...")
            conn.execute(text('ALTER TABLE levy_scenario ADD COLUMN updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP'))
            print("Added 'updated_at' column to levy_scenario table.")
            
        # Add is_public column if it doesn't exist
        if 'is_public' not in columns:
            print("Adding 'is_public' column to levy_scenario table...")
            conn.execute(text('ALTER TABLE levy_scenario ADD COLUMN is_public BOOLEAN DEFAULT FALSE'))
            print("Added 'is_public' column to levy_scenario table.")
            
        # Add status column if it doesn't exist
        if 'status' not in columns:
            print("Adding 'status' column to levy_scenario table...")
            conn.execute(text('ALTER TABLE levy_scenario ADD COLUMN status VARCHAR(32) DEFAULT \'DRAFT\''))
            print("Added 'status' column to levy_scenario table.")
        
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
    print(f"Running migration to add missing columns to levy_scenario table...")
    run_migration()
    print(f"Migration complete.")