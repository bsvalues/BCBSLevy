"""
Migration script to add the user_roles table for role-based access control.

This script adds a table to store user roles for the TerraLevy platform, providing
the foundation for role-based access control (RBAC) for clerks, deputies, and assessors.
"""

import logging
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a base class for declarative models
Base = declarative_base()

class UserRole(Base):
    """
    Model for storing user roles for role-based access control.
    
    This table associates users with specific roles (clerk, deputy, assessor)
    to implement the multi-stage certification workflow described in the
    product requirements.
    """
    __tablename__ = 'user_role'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    role = Column(String(32), nullable=False, index=True)  # clerk, deputy, assessor
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    
    __table_args__ = (
        UniqueConstraint('user_id', 'role', name='uix_user_role'),
        Index('idx_user_role', 'user_id', 'role'),
    )


def run_migration():
    """
    Create the UserRole table if it doesn't exist.
    """
    try:
        # Get database URL from environment
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            logger.error("DATABASE_URL environment variable not set")
            return False
        
        # Create database engine
        engine = create_engine(database_url)
        
        from sqlalchemy import inspect
        
        # Check if table already exists
        inspector = inspect(engine)
        if not inspector.has_table('user_role'):
            # Create the table
            Base.metadata.create_all(engine, tables=[UserRole.__table__])
            logger.info("Created user_role table")
            
            # Add default roles
            from sqlalchemy.orm import sessionmaker
            Session = sessionmaker(bind=engine)
            
            # Only try to add default roles if user table exists and has users
            if inspector.has_table('user'):
                session = Session()
                try:
                    # Check if any users exist
                    user_count = session.execute("SELECT COUNT(*) FROM \"user\"").scalar()
                    
                    if user_count > 0:
                        # Add default assessor role to admin users
                        session.execute(
                            "INSERT INTO user_role (user_id, role, created_at) "
                            "SELECT id, 'assessor', now() FROM \"user\" WHERE is_admin = true "
                            "ON CONFLICT DO NOTHING"
                        )
                        
                        # Commit changes
                        session.commit()
                        logger.info("Added default assessor roles to admin users")
                except Exception as e:
                    session.rollback()
                    logger.error(f"Error adding default roles: {str(e)}")
                finally:
                    session.close()
            
            return True
        else:
            logger.info("user_role table already exists")
            return True
            
    except SQLAlchemyError as e:
        logger.error(f"Database error during migration: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during migration: {str(e)}")
        return False


if __name__ == "__main__":
    run_migration()