"""
Migration script to add the audit columns to the import_log table.

This script adds created_at, updated_at, created_by_id, and updated_by_id columns
to the import_log table to match the AuditMixin definition.
"""

import os
import sys
import logging
import psycopg2
from psycopg2 import sql
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_migration():
    """
    Add audit columns to the import_log table if they don't exist.
    """
    # Get database connection details from environment
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        logger.error("DATABASE_URL environment variable is not set")
        return False

    try:
        # Connect directly to the database
        logger.info("Connecting to the database")
        conn = psycopg2.connect(db_url)
        conn.autocommit = False  # Use transactions
        cursor = conn.cursor()
        
        logger.info("Starting migration to add audit columns to import_log table")
        
        # Check if columns already exist
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'import_log' 
            AND column_name IN ('created_at', 'updated_at', 'created_by_id', 'updated_by_id')
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        # Also check for import_date column
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'import_log' 
            AND column_name = 'import_date'
        """)
        has_import_date = len(cursor.fetchall()) > 0
        
        # Determine which columns need to be added
        columns_to_add = []
        if 'created_at' not in existing_columns:
            columns_to_add.append(('created_at', 'TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()'))
        
        if 'updated_at' not in existing_columns:
            columns_to_add.append(('updated_at', 'TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()'))
        
        if 'created_by_id' not in existing_columns:
            columns_to_add.append(('created_by_id', 'INTEGER'))
        
        if 'updated_by_id' not in existing_columns:
            columns_to_add.append(('updated_by_id', 'INTEGER'))
        
        # Add the missing columns
        if columns_to_add:
            logger.info(f"Adding {len(columns_to_add)} audit columns to import_log table")
            
            for column_name, column_type in columns_to_add:
                logger.info(f"Adding column {column_name} to import_log table")
                query = sql.SQL("ALTER TABLE import_log ADD COLUMN IF NOT EXISTS {} {}").format(
                    sql.Identifier(column_name),
                    sql.SQL(column_type)
                )
                cursor.execute(query)
            
            # Create foreign key constraints for user references if they don't exist
            if 'created_by_id' in [c[0] for c in columns_to_add]:
                # First check if the constraint already exists
                cursor.execute("""
                    SELECT constraint_name 
                    FROM information_schema.table_constraints 
                    WHERE table_name = 'import_log' 
                    AND constraint_name = 'fk_import_log_created_by'
                """)
                if not cursor.fetchone():
                    logger.info("Adding foreign key constraint for created_by_id")
                    cursor.execute("""
                        ALTER TABLE import_log
                        ADD CONSTRAINT fk_import_log_created_by
                        FOREIGN KEY (created_by_id) REFERENCES "user" (id)
                    """)
            
            if 'updated_by_id' in [c[0] for c in columns_to_add]:
                # First check if the constraint already exists
                cursor.execute("""
                    SELECT constraint_name 
                    FROM information_schema.table_constraints 
                    WHERE table_name = 'import_log' 
                    AND constraint_name = 'fk_import_log_updated_by'
                """)
                if not cursor.fetchone():
                    logger.info("Adding foreign key constraint for updated_by_id")
                    cursor.execute("""
                        ALTER TABLE import_log
                        ADD CONSTRAINT fk_import_log_updated_by
                        FOREIGN KEY (updated_by_id) REFERENCES "user" (id)
                    """)
            
            # If there's an import_date column, copy values to created_at
            if has_import_date and 'created_at' in [c[0] for c in columns_to_add]:
                logger.info("Copying import_date values to created_at column")
                cursor.execute("""
                    UPDATE import_log
                    SET created_at = import_date
                    WHERE created_at IS NULL AND import_date IS NOT NULL
                """)
            
            conn.commit()
            logger.info(f"Successfully added audit columns to import_log table")
        else:
            logger.info("Audit columns already exist in import_log table")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        if 'conn' in locals() and conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)