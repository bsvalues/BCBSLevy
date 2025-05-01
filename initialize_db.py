"""
Simple database initialization script for TerraFusion Levy System.

This script initializes the database schema and creates a default admin user.
Run this once before running any import scripts.
"""

import os
import logging
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash

from app import db, create_app
from models import User

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_tables():
    """Create all database tables."""
    logger.info("Creating database tables...")
    db.create_all()
    logger.info("Database tables created successfully")

def create_admin_user():
    """Create a default admin user if none exists."""
    # Check if any admin user exists
    admin = User.query.filter_by(is_administrator=True).first()
    
    if admin:
        logger.info(f"Admin user already exists: {admin.username}")
        return admin
    
    # Create admin user
    admin = User(
        username="admin",
        email="admin@terralevy.com",
        password_hash=generate_password_hash("admin"),  # Default password, should be changed
        first_name="Admin",
        last_name="User",
        is_active=True,
        is_administrator=True
    )
    
    db.session.add(admin)
    db.session.commit()
    
    logger.info(f"Created admin user: {admin.username}")
    return admin

def main():
    """Main initialization function."""
    logger.info("Starting database initialization")
    
    # Create Flask application context
    app = create_app()
    
    with app.app_context():
        try:
            # Create tables
            create_tables()
            
            # Create admin user
            create_admin_user()
            
            logger.info("Database initialization completed successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    main()