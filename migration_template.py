"""
Migration Template for TerraLevy

This template should be copied and modified for each database migration.
It provides a structured approach to applying changes to the database schema.

Instructions:
1. Copy this file and name it with a descriptive name (e.g., add_user_preferences.py)
2. Fill in the migration details in the MIGRATION_INFO dictionary
3. Implement the upgrade() and downgrade() functions
4. Test the migration in a development environment before applying to production

Example usage:
    python migration_template.py --check  # Validates the migration without applying
    python migration_template.py --apply  # Applies the migration
    python migration_template.py --revert # Reverts the migration
"""

import argparse
import datetime
import logging
import os
import sys
from contextlib import contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Fill in these details for your migration
MIGRATION_INFO = {
    'id': f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_migration_name",
    'description': 'Description of what this migration does',
    'author': 'Your Name',
    'dependencies': [],  # List of migration IDs that must be applied before this one
}

@contextmanager
def database_connection():
    """
    Context manager for database connection.
    Yields a database connection that can be used for executing SQL.
    """
    try:
        from app import app, db
        with app.app_context():
            yield db.session
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise

def check_migration_applied():
    """
    Check if this migration has already been applied.
    Returns True if the migration has been applied, False otherwise.
    """
    try:
        with database_connection() as session:
            # Check migration table
            result = session.execute(
                "SELECT COUNT(*) FROM migration_history WHERE migration_id = :id",
                {'id': MIGRATION_INFO['id']}
            ).scalar()
            return result > 0
    except Exception as e:
        logger.error(f"Error checking migration status: {str(e)}")
        return False

def record_migration(applied=True):
    """
    Record that this migration has been applied or reverted.
    """
    try:
        with database_connection() as session:
            if applied:
                # Record application
                session.execute(
                    """
                    INSERT INTO migration_history 
                    (migration_id, description, author, applied_at)
                    VALUES (:id, :description, :author, NOW())
                    """,
                    {
                        'id': MIGRATION_INFO['id'],
                        'description': MIGRATION_INFO['description'],
                        'author': MIGRATION_INFO['author']
                    }
                )
            else:
                # Record reversion
                session.execute(
                    "DELETE FROM migration_history WHERE migration_id = :id",
                    {'id': MIGRATION_INFO['id']}
                )
            session.commit()
    except Exception as e:
        logger.error(f"Error recording migration status: {str(e)}")
        raise

def check_dependencies():
    """
    Check if all dependencies have been applied.
    Returns True if all dependencies are satisfied, False otherwise.
    """
    if not MIGRATION_INFO['dependencies']:
        return True
        
    try:
        with database_connection() as session:
            for dep_id in MIGRATION_INFO['dependencies']:
                result = session.execute(
                    "SELECT COUNT(*) FROM migration_history WHERE migration_id = :id",
                    {'id': dep_id}
                ).scalar()
                if result == 0:
                    logger.error(f"Dependency {dep_id} has not been applied")
                    return False
            return True
    except Exception as e:
        logger.error(f"Error checking dependencies: {str(e)}")
        return False

def upgrade():
    """
    Implement the upgrade logic for this migration.
    This function should make the necessary changes to upgrade the database schema.
    """
    # TODO: Implement your upgrade logic here
    try:
        with database_connection() as session:
            # Example: Create a new table
            # session.execute("""
            #     CREATE TABLE IF NOT EXISTS new_table (
            #         id SERIAL PRIMARY KEY,
            #         name VARCHAR(255) NOT NULL,
            #         created_at TIMESTAMP DEFAULT NOW()
            #     )
            # """)
            
            # Example: Add a column to an existing table
            # session.execute("""
            #     ALTER TABLE existing_table
            #     ADD COLUMN new_column VARCHAR(255)
            # """)
            
            # Example: Update SQLAlchemy model to match
            logger.info("Upgrading database schema")
            session.commit()
            return True
    except Exception as e:
        logger.error(f"Error upgrading database: {str(e)}")
        return False

def downgrade():
    """
    Implement the downgrade logic for this migration.
    This function should revert the changes made in the upgrade function.
    """
    # TODO: Implement your downgrade logic here
    try:
        with database_connection() as session:
            # Example: Drop a newly created table
            # session.execute("DROP TABLE IF EXISTS new_table")
            
            # Example: Remove a newly added column
            # session.execute("ALTER TABLE existing_table DROP COLUMN new_column")
            
            logger.info("Downgrading database schema")
            session.commit()
            return True
    except Exception as e:
        logger.error(f"Error downgrading database: {str(e)}")
        return False

def ensure_migration_table():
    """
    Ensure the migration history table exists.
    """
    try:
        with database_connection() as session:
            session.execute("""
                CREATE TABLE IF NOT EXISTS migration_history (
                    id SERIAL PRIMARY KEY,
                    migration_id VARCHAR(255) NOT NULL UNIQUE,
                    description TEXT,
                    author VARCHAR(255),
                    applied_at TIMESTAMP DEFAULT NOW()
                )
            """)
            session.commit()
    except Exception as e:
        logger.error(f"Error creating migration history table: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Database migration script')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--check', action='store_true', help='Check if migration can be applied')
    group.add_argument('--apply', action='store_true', help='Apply the migration')
    group.add_argument('--revert', action='store_true', help='Revert the migration')
    
    args = parser.parse_args()
    
    try:
        # Ensure migration table exists
        ensure_migration_table()
        
        if args.check:
            # Check if migration can be applied
            already_applied = check_migration_applied()
            dependencies_met = check_dependencies()
            
            if already_applied:
                logger.warning(f"Migration {MIGRATION_INFO['id']} has already been applied")
                return 1
                
            if not dependencies_met:
                logger.error("Not all dependencies have been met")
                return 1
                
            logger.info("Migration can be applied")
            return 0
            
        elif args.apply:
            # Apply the migration
            already_applied = check_migration_applied()
            if already_applied:
                logger.warning(f"Migration {MIGRATION_INFO['id']} has already been applied")
                return 1
                
            if not check_dependencies():
                logger.error("Not all dependencies have been met")
                return 1
                
            logger.info(f"Applying migration {MIGRATION_INFO['id']}")
            
            if upgrade():
                record_migration(applied=True)
                logger.info("Migration applied successfully")
                return 0
            else:
                logger.error("Failed to apply migration")
                return 1
                
        elif args.revert:
            # Revert the migration
            already_applied = check_migration_applied()
            if not already_applied:
                logger.warning(f"Migration {MIGRATION_INFO['id']} has not been applied")
                return 1
                
            logger.info(f"Reverting migration {MIGRATION_INFO['id']}")
            
            if downgrade():
                record_migration(applied=False)
                logger.info("Migration reverted successfully")
                return 0
            else:
                logger.error("Failed to revert migration")
                return 1
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())