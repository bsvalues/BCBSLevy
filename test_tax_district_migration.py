"""
Test script for tax_district migration process.

This script tests the migration process by:
1. Checking database state before migration
2. Running the migration process
3. Verifying the database state after migration
"""

import os
import sys
import unittest
import logging
from datetime import datetime
import psycopg2
from psycopg2.extras import DictCursor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable not set")
    sys.exit(1)

# Re-implement necessary functions for testing to avoid circular imports
def backup_tables_test():
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
        if 'conn' in locals() and conn:
            conn.rollback() 
        logger.error(f"Error creating backup tables: {e}")
        return False
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

def update_foreign_keys_test():
    """Update foreign key constraints from tax_district_old to tax_district."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        cursor = conn.cursor()
        
        # Check if constraints already exist on tax_district
        cursor.execute("""
        SELECT COUNT(*) FROM pg_constraint
        WHERE conname IN ('levy_rate_tax_district_id_fkey', 'forecast_tax_district_id_fkey', 'compliance_issue_tax_district_id_fkey')
          AND contype = 'f'
        """)
        existing_constraints = cursor.fetchone()[0]
        
        # If constraints already exist on tax_district, migration is already done
        if existing_constraints > 0:
            logger.info("Foreign key constraints already updated to tax_district")
            conn.commit()
            return True
        
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
        if 'conn' in locals() and conn:
            conn.rollback()
        logger.error(f"Error updating foreign key constraints: {e}")
        return False
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

def verify_migration_test():
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
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

def run_migration_test():
    """Execute the full migration process with verification."""
    logger.info("Starting tax_district reference migration")
    
    # Step 1: Backup tables
    if not backup_tables_test():
        logger.error("Migration aborted due to backup failure")
        return False
    
    # Step 2: Update foreign key constraints
    if not update_foreign_keys_test():
        logger.error("Migration aborted due to foreign key update failure")
        return False
    
    # Step 3: Verify migration
    if not verify_migration_test():
        logger.error("Migration verification failed")
        return False
    
    logger.info("Migration completed successfully")
    return True

class TaxDistrictMigrationTest(unittest.TestCase):
    """Test case for tax_district migration."""
    
    def setUp(self):
        """Set up test environment."""
        # Create connection
        self.conn = psycopg2.connect(DATABASE_URL)
        self.cursor = self.conn.cursor(cursor_factory=DictCursor)
        
        # Store initial state
        self.conn.autocommit = True
        self.get_initial_state()
    
    def tearDown(self):
        """Clean up test environment."""
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
    
    def get_initial_state(self):
        """Get initial database state before testing."""
        # Check current foreign key constraints
        self.cursor.execute("""
        SELECT t.relname AS table_name, c.conname AS constraint_name, pg_get_constraintdef(c.oid) AS constraint_definition
        FROM pg_constraint c
        JOIN pg_class t ON c.conrelid = t.oid
        WHERE c.confrelid = (SELECT oid FROM pg_class WHERE relname = 'tax_district_old')
          AND c.contype = 'f'
        """)
        self.initial_constraints = self.cursor.fetchall()
    
    def test_backup_function(self):
        """Test the backup_tables function."""
        logger.info("Testing backup_tables function")
        result = backup_tables_test()
        self.assertTrue(result, "Backup tables function should return True")
        
        # Check that backup tables were created
        self.cursor.execute("SELECT tablename FROM pg_tables WHERE tablename LIKE 'levy_rate_backup_%'")
        backup_tables = self.cursor.fetchall()
        self.assertTrue(len(backup_tables) > 0, "Backup tables should be created")
    
    def test_update_foreign_keys_function(self):
        """Test the update_foreign_keys function."""
        logger.info("Testing update_foreign_keys function")
        result = update_foreign_keys_test()
        self.assertTrue(result, "Update foreign keys function should return True")
        
        # Verify new constraints
        self.cursor.execute("""
        SELECT t.relname AS table_name, c.conname AS constraint_name
        FROM pg_constraint c
        JOIN pg_class t ON c.conrelid = t.oid
        WHERE c.confrelid = (SELECT oid FROM pg_class WHERE relname = 'tax_district')
          AND c.contype = 'f'
          AND t.relname IN ('levy_rate', 'forecast', 'compliance_issue')
        """)
        new_constraints = self.cursor.fetchall()
        self.assertEqual(len(new_constraints), 3, "Should have 3 new constraints")
    
    def test_verify_migration_function(self):
        """Test the verify_migration function."""
        logger.info("Testing verify_migration function")
        # First update the foreign keys to ensure we have something to verify
        update_foreign_keys_test()
        
        result = verify_migration_test()
        self.assertTrue(result, "Verify migration function should return True")
    
    def test_full_migration_process(self):
        """Test the full migration process."""
        logger.info("Testing full migration process")
        result = run_migration_test()
        self.assertTrue(result, "Full migration process should return True")
        
        # Verify no old constraints remain
        self.cursor.execute("""
        SELECT COUNT(*)
        FROM pg_constraint c
        JOIN pg_class t ON c.conrelid = t.oid
        WHERE c.confrelid = (SELECT oid FROM pg_class WHERE relname = 'tax_district_old')
          AND c.contype = 'f'
        """)
        old_constraints_count = self.cursor.fetchone()[0]
        self.assertEqual(old_constraints_count, 0, "No old constraints should remain")
        
        # Verify new constraints exist
        self.cursor.execute("""
        SELECT COUNT(*)
        FROM pg_constraint c
        JOIN pg_class t ON c.conrelid = t.oid
        WHERE c.confrelid = (SELECT oid FROM pg_class WHERE relname = 'tax_district')
          AND c.contype = 'f'
          AND t.relname IN ('levy_rate', 'forecast', 'compliance_issue')
        """)
        new_constraints_count = self.cursor.fetchone()[0]
        self.assertEqual(new_constraints_count, 3, "Three new constraints should exist")


if __name__ == "__main__":
    # Create migration_reports directory if it doesn't exist
    os.makedirs("migration_reports", exist_ok=True)
    
    # Run tests
    unittest.main()