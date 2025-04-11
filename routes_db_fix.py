"""
Routes for database fixes and maintenance.

This module provides routes for database maintenance tasks like fixing enum values.
"""

import logging
from flask import Blueprint, jsonify, render_template
from sqlalchemy import text

from app import db
from models import ImportType, ExportType

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
db_fix_bp = Blueprint("db_fix", __name__, url_prefix="/db-fix")


@db_fix_bp.route("/")
def index():
    """Main page for database fix tools."""
    return render_template("db_fix/fix_form.html")


@db_fix_bp.route("/fix-import-log-enums")
def fix_import_log_enums():
    """Fix inconsistent enum values in the import_log table."""
    try:
        # Get all distinct import_type values from the database
        result = db.session.execute(text(
            "SELECT DISTINCT import_type FROM import_log"
        ))
        
        values = [row[0] for row in result if row[0]]
        
        # Valid values from the ImportType enum
        valid_values = [e.value for e in ImportType]
        
        # Identify invalid values
        invalid_values = [v for v in values if v not in valid_values]
        
        fixes_applied = []
        for invalid_value in invalid_values:
            # For 'property', map to 'PROPERTY'
            if invalid_value.lower() == 'property':
                new_value = 'PROPERTY'
            else:
                new_value = 'OTHER'  # Default to OTHER
                
            # Update records with this invalid value
            db.session.execute(text(
                f"UPDATE import_log SET import_type = '{new_value}' "
                f"WHERE import_type = '{invalid_value}'"
            ))
            
            fixes_applied.append({
                "old_value": invalid_value,
                "new_value": new_value
            })
        
        # Commit the changes
        db.session.commit()
        
        logger.info(f"Fixed {len(fixes_applied)} invalid import_type values")
        return render_template(
            "db_fix/results.html",
            success=True,
            invalid_values_found=len(invalid_values),
            fixes_applied=fixes_applied
        )
    
    except Exception as e:
        logger.error(f"Error fixing import_log enums: {str(e)}")
        db.session.rollback()
        return render_template(
            "db_fix/results.html",
            success=False,
            error=str(e)
        )


@db_fix_bp.route("/fix-export-log-enums")
def fix_export_log_enums():
    """Fix inconsistent enum values in the export_log table."""
    try:
        # Get all distinct export_type values from the database
        result = db.session.execute(text(
            "SELECT DISTINCT export_type FROM export_log"
        ))
        
        values = [row[0] for row in result if row[0]]
        
        # Valid values from the ExportType enum
        valid_values = [e.value for e in ExportType]
        
        # Identify invalid values
        invalid_values = [v for v in values if v not in valid_values]
        
        fixes_applied = []
        for invalid_value in invalid_values:
            # Map based on similarity to existing enum values
            if 'levy' in invalid_value.lower() and 'report' in invalid_value.lower():
                new_value = 'LEVY_REPORT'
            elif 'levy' in invalid_value.lower():
                new_value = 'LEVY'
            elif 'report' in invalid_value.lower():
                new_value = 'REPORT'
            elif 'district' in invalid_value.lower():
                new_value = 'TAX_DISTRICT'
            elif 'code' in invalid_value.lower():
                new_value = 'TAX_CODE'
            elif 'property' in invalid_value.lower():
                new_value = 'PROPERTY'
            elif 'rate' in invalid_value.lower():
                new_value = 'RATE'
            elif 'analysis' in invalid_value.lower():
                new_value = 'ANALYSIS'
            else:
                new_value = 'OTHER'
                
            # Update records with this invalid value
            db.session.execute(text(
                f"UPDATE export_log SET export_type = '{new_value}' "
                f"WHERE export_type = '{invalid_value}'"
            ))
            
            fixes_applied.append({
                "old_value": invalid_value,
                "new_value": new_value
            })
        
        # Commit the changes
        db.session.commit()
        
        logger.info(f"Fixed {len(fixes_applied)} invalid export_type values")
        return render_template(
            "db_fix/results.html",
            success=True,
            invalid_values_found=len(invalid_values),
            fixes_applied=fixes_applied
        )
    
    except Exception as e:
        logger.error(f"Error fixing export_log enums: {str(e)}")
        db.session.rollback()
        return render_template(
            "db_fix/results.html",
            success=False,
            error=str(e)
        )


@db_fix_bp.route("/api/fix-import-log-enums")
def api_fix_import_log_enums():
    """API route to fix inconsistent enum values in the import_log table."""
    try:
        # Get all distinct import_type values from the database
        result = db.session.execute(text(
            "SELECT DISTINCT import_type FROM import_log"
        ))
        
        values = [row[0] for row in result if row[0]]
        
        # Valid values from the ImportType enum
        valid_values = [e.value for e in ImportType]
        
        # Identify invalid values
        invalid_values = [v for v in values if v not in valid_values]
        
        fixes_applied = []
        for invalid_value in invalid_values:
            # For 'property', map to 'PROPERTY'
            if invalid_value.lower() == 'property':
                new_value = 'PROPERTY'
            else:
                new_value = 'OTHER'  # Default to OTHER
                
            # Update records with this invalid value
            db.session.execute(text(
                f"UPDATE import_log SET import_type = '{new_value}' "
                f"WHERE import_type = '{invalid_value}'"
            ))
            
            fixes_applied.append({
                "old_value": invalid_value,
                "new_value": new_value
            })
        
        # Commit the changes
        db.session.commit()
        
        return jsonify({
            "success": True,
            "invalid_values_found": len(invalid_values),
            "fixes_applied": fixes_applied
        })
    
    except Exception as e:
        logger.error(f"Error fixing import_log enums: {str(e)}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500