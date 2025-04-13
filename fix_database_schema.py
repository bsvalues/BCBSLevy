"""
Migration script to fix database schema inconsistencies.

This script adds missing columns to the property and export_log tables
to align them with the models.py definitions.
"""

import os
import sys
import logging
from datetime import datetime
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable not set")
    sys.exit(1)

# SQL for property table updates
property_update_sql = """
-- Add tax_code_id column to property table using existing tax_code column
ALTER TABLE property ADD COLUMN IF NOT EXISTS tax_code_id INTEGER;

-- Update tax_code_id from tax_code by joining with tax_code table
UPDATE property p
SET tax_code_id = tc.id
FROM tax_code tc
WHERE p.tax_code = tc.tax_code;

-- Add missing columns to property table
ALTER TABLE property ADD COLUMN IF NOT EXISTS property_address VARCHAR(256);
ALTER TABLE property ADD COLUMN IF NOT EXISTS city VARCHAR(64);
ALTER TABLE property ADD COLUMN IF NOT EXISTS state VARCHAR(2);
ALTER TABLE property ADD COLUMN IF NOT EXISTS zip_code VARCHAR(10);
ALTER TABLE property ADD COLUMN IF NOT EXISTS market_value FLOAT;
ALTER TABLE property ADD COLUMN IF NOT EXISTS land_value FLOAT;
ALTER TABLE property ADD COLUMN IF NOT EXISTS building_value FLOAT;
ALTER TABLE property ADD COLUMN IF NOT EXISTS tax_exempt BOOLEAN DEFAULT FALSE;
ALTER TABLE property ADD COLUMN IF NOT EXISTS exemption_amount FLOAT DEFAULT 0.0;
ALTER TABLE property ADD COLUMN IF NOT EXISTS taxable_value FLOAT DEFAULT 0.0;
ALTER TABLE property ADD COLUMN IF NOT EXISTS tax_amount FLOAT DEFAULT 0.0;
ALTER TABLE property ADD COLUMN IF NOT EXISTS longitude FLOAT;
ALTER TABLE property ADD COLUMN IF NOT EXISTS latitude FLOAT;
ALTER TABLE property ADD COLUMN IF NOT EXISTS created_by_id INTEGER;
ALTER TABLE property ADD COLUMN IF NOT EXISTS updated_by_id INTEGER;

-- Create index for tax_code_id if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'property' AND indexname = 'idx_property_tax_code_id'
    ) THEN
        CREATE INDEX idx_property_tax_code_id ON property(tax_code_id);
    END IF;
END $$;

-- Add foreign key constraint if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_property_tax_code' 
        AND table_name = 'property'
    ) THEN
        ALTER TABLE property 
        ADD CONSTRAINT fk_property_tax_code 
        FOREIGN KEY (tax_code_id) 
        REFERENCES tax_code(id);
    END IF;
EXCEPTION
    WHEN others THEN
        -- If there are NULL values or other issues, log the error
        RAISE NOTICE 'Could not add foreign key constraint: %', SQLERRM;
END $$;
"""

# SQL for export_log table updates
export_log_update_sql = """
-- Add missing columns to export_log table
ALTER TABLE export_log ADD COLUMN IF NOT EXISTS user_id INTEGER;
ALTER TABLE export_log ADD COLUMN IF NOT EXISTS record_count INTEGER DEFAULT 0;
ALTER TABLE export_log ADD COLUMN IF NOT EXISTS error_details TEXT;
ALTER TABLE export_log ADD COLUMN IF NOT EXISTS processing_time FLOAT;
ALTER TABLE export_log ADD COLUMN IF NOT EXISTS year INTEGER;
ALTER TABLE export_log ADD COLUMN IF NOT EXISTS export_metadata JSONB;
ALTER TABLE export_log ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();
ALTER TABLE export_log ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();
ALTER TABLE export_log ADD COLUMN IF NOT EXISTS created_by_id INTEGER;
ALTER TABLE export_log ADD COLUMN IF NOT EXISTS updated_by_id INTEGER;

-- Set user_id to 1 (admin user) for existing records
UPDATE export_log SET user_id = 1 WHERE user_id IS NULL;

-- Make user_id non-nullable after setting values
ALTER TABLE export_log ALTER COLUMN user_id SET NOT NULL;

-- Set year to current year for existing records if NULL
UPDATE export_log SET year = EXTRACT(YEAR FROM CURRENT_DATE) WHERE year IS NULL;

-- Make year non-nullable after setting values
ALTER TABLE export_log ALTER COLUMN year SET NOT NULL;

-- Create indexes for new columns
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'export_log' AND indexname = 'idx_export_log_user_id'
    ) THEN
        CREATE INDEX idx_export_log_user_id ON export_log(user_id);
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'export_log' AND indexname = 'idx_export_log_year'
    ) THEN
        CREATE INDEX idx_export_log_year ON export_log(year);
    END IF;
END $$;

-- Add foreign key constraint if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_export_log_user' 
        AND table_name = 'export_log'
    ) THEN
        ALTER TABLE export_log 
        ADD CONSTRAINT fk_export_log_user 
        FOREIGN KEY (user_id) 
        REFERENCES "user"(id);
    END IF;
EXCEPTION
    WHEN others THEN
        -- If there are issues, log the error
        RAISE NOTICE 'Could not add foreign key constraint: %', SQLERRM;
END $$;
"""

# Run migrations
def run_migration():
    """Fix database schema inconsistencies."""
    try:
        logger.info("Starting schema migration")
        
        # Connect to the database
        logger.info(f"Connecting to database: {DATABASE_URL}")
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cursor:
            # Update property table
            logger.info("Updating property table schema")
            cursor.execute(property_update_sql)
            
            # Update export_log table
            logger.info("Updating export_log table schema")
            cursor.execute(export_log_update_sql)
            
        logger.info("Schema migration completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error updating database schema: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_migration()