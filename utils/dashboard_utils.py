"""
Dashboard utility functions for the Levy Calculation System.

This module provides helper functions for the dashboard routes.
"""

import logging
from datetime import datetime
from sqlalchemy import func, desc, text
from app import db
from models import ImportLog, ExportLog

# Configure logger
logger = logging.getLogger(__name__)

def get_recent_imports(limit=5):
    """
    Get recent imports safely, handling any schema mismatches between code and database.
    
    Args:
        limit: Maximum number of import logs to retrieve
        
    Returns:
        List of ImportLog objects
    """
    try:
        # First try using ORM
        recent_imports = ImportLog.query.order_by(
            ImportLog.created_at.desc()
        ).limit(limit).all()
        return recent_imports
    except Exception as e:
        # If ORM fails, fall back to raw SQL with safe column selection
        logger.warning(f"Error using ORM for ImportLog query: {str(e)}")
        try:
            # Use text() for a raw SQL query with only columns we know exist
            result = db.session.execute(
                text("""
                    SELECT id, filename, import_type, status, 
                           user_id, year, created_at, notes
                    FROM import_log
                    ORDER BY created_at DESC
                    LIMIT :limit
                """),
                {"limit": limit}
            )
            
            # Create ImportLog objects manually
            imports = []
            for row in result:
                import_log = ImportLog(
                    id=row.id,
                    filename=row.filename,
                    import_type=row.import_type,
                    status=row.status,
                    user_id=row.user_id,
                    year=row.year,
                    created_at=row.created_at,
                    notes=row.notes
                )
                imports.append(import_log)
            
            return imports
        except Exception as inner_e:
            logger.error(f"Failed to get recent imports with raw SQL: {str(inner_e)}")
            return []  # Return empty list on error

def get_import_count(year=None):
    """
    Get count of import logs with schema mismatch handling.
    
    Args:
        year: Year to filter by (optional)
        
    Returns:
        Integer count of import logs
    """
    try:
        # Try ORM first
        if year:
            return ImportLog.query.filter_by(year=year).count()
        else:
            return ImportLog.query.count()
    except Exception as e:
        logger.warning(f"Error using ORM for ImportLog count: {str(e)}")
        try:
            # Fall back to raw SQL
            if year:
                result = db.session.execute(
                    text("SELECT COUNT(*) FROM import_log WHERE year = :year"),
                    {"year": year}
                )
            else:
                result = db.session.execute(text("SELECT COUNT(*) FROM import_log"))
            
            return result.scalar()
        except Exception as inner_e:
            logger.error(f"Failed to get import count with raw SQL: {str(inner_e)}")
            return 0  # Default to 0 on error

def get_import_success_count(year=None):
    """
    Get count of successful import logs with schema mismatch handling.
    
    Args:
        year: Year to filter by (optional)
        
    Returns:
        Integer count of successful import logs
    """
    try:
        # Try ORM first
        query = ImportLog.query.filter_by(status='SUCCESS')
        if year:
            query = query.filter_by(year=year)
        return query.count()
    except Exception as e:
        logger.warning(f"Error using ORM for successful ImportLog count: {str(e)}")
        try:
            # Fall back to raw SQL
            if year:
                result = db.session.execute(
                    text("SELECT COUNT(*) FROM import_log WHERE status = 'SUCCESS' AND year = :year"),
                    {"year": year}
                )
            else:
                result = db.session.execute(
                    text("SELECT COUNT(*) FROM import_log WHERE status = 'SUCCESS'")
                )
            
            return result.scalar()
        except Exception as inner_e:
            logger.error(f"Failed to get successful import count with raw SQL: {str(inner_e)}")
            return 0  # Default to 0 on error

def get_export_count(year=None):
    """
    Get count of export logs with schema mismatch handling.
    
    Args:
        year: Year to filter by (optional)
        
    Returns:
        Integer count of export logs
    """
    try:
        # Try ORM first
        if year:
            return ExportLog.query.filter_by(year=year).count()
        else:
            return ExportLog.query.count()
    except Exception as e:
        logger.warning(f"Error using ORM for ExportLog count: {str(e)}")
        try:
            # Fall back to raw SQL
            if year:
                result = db.session.execute(
                    text("SELECT COUNT(*) FROM export_log WHERE year = :year"),
                    {"year": year}
                )
            else:
                result = db.session.execute(text("SELECT COUNT(*) FROM export_log"))
            
            return result.scalar()
        except Exception as inner_e:
            logger.error(f"Failed to get export count with raw SQL: {str(inner_e)}")
            return 0  # Default to 0 on error

def get_export_success_count(year=None):
    """
    Get count of successful export logs with schema mismatch handling.
    
    Args:
        year: Year to filter by (optional)
        
    Returns:
        Integer count of successful export logs
    """
    try:
        # Try ORM first
        query = ExportLog.query.filter_by(status='SUCCESS')
        if year:
            query = query.filter_by(year=year)
        return query.count()
    except Exception as e:
        logger.warning(f"Error using ORM for successful ExportLog count: {str(e)}")
        try:
            # Fall back to raw SQL
            if year:
                result = db.session.execute(
                    text("SELECT COUNT(*) FROM export_log WHERE status = 'SUCCESS' AND year = :year"),
                    {"year": year}
                )
            else:
                result = db.session.execute(
                    text("SELECT COUNT(*) FROM export_log WHERE status = 'SUCCESS'")
                )
            
            return result.scalar()
        except Exception as inner_e:
            logger.error(f"Failed to get successful export count with raw SQL: {str(inner_e)}")
            return 0  # Default to 0 on error