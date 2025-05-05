"""
Run database migrations for the TerraLevy platform.

This script runs the migrations defined in the migration scripts to update
the database schema as needed.
"""

import logging
import importlib
from flask import Flask
from sqlalchemy import create_engine
import os
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations():
    """Run all database migrations in order."""
    try:
        # Get the DATABASE_URL from environment
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            logger.error("DATABASE_URL environment variable not set")
            return False
            
        # Verify database connection
        try:
            engine = create_engine(database_url)
            conn = engine.connect()
            conn.close()
            logger.info("Database connection successful")
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            return False
        
        # List of migration files to run
        migration_files = [
            'add_user_roles_table'
        ]
        
        success_count = 0
        for migration_file in migration_files:
            try:
                # Import the migration module
                migration_module = importlib.import_module(migration_file)
                
                # Run the migration
                logger.info(f"Running migration: {migration_file}")
                result = migration_module.run_migration()
                
                if result:
                    logger.info(f"Migration {migration_file} completed successfully")
                    success_count += 1
                else:
                    logger.error(f"Migration {migration_file} failed")
            except ImportError as e:
                logger.error(f"Failed to import migration {migration_file}: {str(e)}")
            except Exception as e:
                logger.error(f"Error running migration {migration_file}: {str(e)}")
        
        logger.info(f"Migrations completed: {success_count}/{len(migration_files)} successful")
        return success_count == len(migration_files)
    
    except Exception as e:
        logger.error(f"Unexpected error running migrations: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)