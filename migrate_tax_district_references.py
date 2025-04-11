"""
Migration script to update foreign key references from tax_district_old to tax_district.

This script performs a safe migration of foreign key constraints from the legacy
tax_district_old table to the current tax_district table. It follows these steps:
1. Creates temporary backup tables
2. Drops existing foreign key constraints
3. Creates new foreign key constraints to tax_district
4. Verifies the migration was successful
"""

import os
import sys
import logging
from datetime import datetime
import psycopg2
from psycopg2.extras import DictCursor
from sqlalchemy import create_engine, text

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"migration_reports/tax_district_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable not set")
    sys.exit(1)


def backup_tables():
    """Create backup tables for levy_rate, forecast, and compliance_issue."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        cursor = conn.cursor()
        
        logger.info("Creating backup tables...")
        
        # Create backup tables with timestamp suffix
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        tables_to_backup = ['levy_rate', 'forecast', 'compliance_issue']
        for table in tables_to_backup:
            backup_table = f"{table}_backup_{timestamp}"
            cursor.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM {table}")
            logger.info(f"Created backup table: {backup_table}")
        
        conn.commit()
        logger.info("Backup tables created successfully")
        return True
    except Exception as e:
        conn.rollback() if 'conn' in locals() else None
        logger.error(f"Error creating backup tables: {e}")
        return False
    finally:
        cursor.close() if 'cursor' in locals() else None
        conn.close() if 'conn' in locals() else None


def update_foreign_keys():
    """
    Update foreign key constraints from tax_district_old to tax_district.
    """
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        cursor = conn.cursor()
        
        # Get the constraint names
        cursor.execute("""
        SELECT t.relname AS table_name, c.conname AS constraint_name
        FROM pg_constraint c
        JOIN pg_class t ON c.conrelid = t.oid
        WHERE c.confrelid = (SELECT oid FROM pg_class WHERE relname = 'tax_district_old')
          AND c.contype = 'f'
        """)
        constraints = cursor.fetchall()
        
        # Drop existing constraints
        logger.info("Dropping existing foreign key constraints...")
        for table_name, constraint_name in constraints:
            cursor.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT {constraint_name}")
            logger.info(f"Dropped constraint {constraint_name} from {table_name}")
        
        # Create new constraints to tax_district
        logger.info("Creating new foreign key constraints to tax_district...")
        
        # For levy_rate
        cursor.execute("""
        ALTER TABLE levy_rate
        ADD CONSTRAINT levy_rate_tax_district_id_fkey
        FOREIGN KEY (tax_district_id)
        REFERENCES tax_district(id)
        """)
        
        # For forecast
        cursor.execute("""
        ALTER TABLE forecast
        ADD CONSTRAINT forecast_tax_district_id_fkey
        FOREIGN KEY (tax_district_id)
        REFERENCES tax_district(id)
        """)
        
        # For compliance_issue
        cursor.execute("""
        ALTER TABLE compliance_issue
        ADD CONSTRAINT compliance_issue_tax_district_id_fkey
        FOREIGN KEY (tax_district_id)
        REFERENCES tax_district(id)
        """)
        
        conn.commit()
        logger.info("Foreign key constraints updated successfully")
        return True
    except Exception as e:
        conn.rollback() if 'conn' in locals() else None
        logger.error(f"Error updating foreign key constraints: {e}")
        return False
    finally:
        cursor.close() if 'cursor' in locals() else None
        conn.close() if 'conn' in locals() else None


def verify_migration():
    """Verify that the migration was successful."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        # Check that the new constraints exist
        cursor.execute("""
        SELECT t.relname AS table_name, c.conname AS constraint_name, pg_get_constraintdef(c.oid) AS constraint_definition
        FROM pg_constraint c
        JOIN pg_class t ON c.conrelid = t.oid
        WHERE c.confrelid = (SELECT oid FROM pg_class WHERE relname = 'tax_district')
          AND c.contype = 'f'
          AND t.relname IN ('levy_rate', 'forecast', 'compliance_issue')
        """)
        
        new_constraints = cursor.fetchall()
        if len(new_constraints) != 3:
            logger.error(f"Expected 3 new constraints, found {len(new_constraints)}")
            return False
        
        # Verify each constraint
        for constraint in new_constraints:
            logger.info(f"Verified constraint: {constraint['constraint_name']} on {constraint['table_name']}")
            logger.info(f"Definition: {constraint['constraint_definition']}")
        
        # Check that no constraints to tax_district_old remain
        cursor.execute("""
        SELECT COUNT(*)
        FROM pg_constraint c
        JOIN pg_class t ON c.conrelid = t.oid
        WHERE c.confrelid = (SELECT oid FROM pg_class WHERE relname = 'tax_district_old')
          AND c.contype = 'f'
        """)
        
        old_constraints_count = cursor.fetchone()[0]
        if old_constraints_count > 0:
            logger.error(f"Found {old_constraints_count} remaining constraints to tax_district_old")
            return False
        
        logger.info("Migration verification successful - all foreign keys updated correctly")
        return True
    except Exception as e:
        logger.error(f"Error verifying migration: {e}")
        return False
    finally:
        cursor.close() if 'cursor' in locals() else None
        conn.close() if 'conn' in locals() else None


def run_migration():
    """Execute the full migration process with verification."""
    logger.info("Starting tax_district reference migration")
    
    # Step 1: Backup tables
    if not backup_tables():
        logger.error("Migration aborted due to backup failure")
        return False
    
    # Step 2: Update foreign key constraints
    if not update_foreign_keys():
        logger.error("Migration aborted due to foreign key update failure")
        return False
    
    # Step 3: Verify migration
    if not verify_migration():
        logger.error("Migration verification failed")
        return False
    
    logger.info("Migration completed successfully")
    return True


if __name__ == "__main__":
    # Create migration_reports directory if it doesn't exist
    os.makedirs("migration_reports", exist_ok=True)
    
    if run_migration():
        sys.exit(0)
    else:
        sys.exit(1)