"""
Routes for data management in the Levy Calculation System.

This module includes routes for:
- Importing data from various file formats
- Exporting data to different formats
- Managing tax districts, tax codes, and property records
"""

import os
import json
import logging
import tempfile
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, Response
from werkzeug.utils import secure_filename
from sqlalchemy import func, desc, or_, and_
from werkzeug.datastructures import FileStorage

from app import db
from models import (
    TaxDistrict, TaxCode, Property, ImportLog, ExportLog,
    PropertyType, ImportType, ExportType
)
from utils.import_utils import detect_file_type, read_data_from_file, process_import
from utils.district_utils import (
    import_district_text_file, import_district_xml_file, import_excel_xml_file,
    extract_districts_from_file, parse_district_data
)


# Create blueprint
data_management_bp = Blueprint("data_management", __name__, url_prefix="/data")

# Configure logging
logger = logging.getLogger(__name__)


@data_management_bp.route("/", methods=["GET"])
def data_management_index():
    """Render the data management dashboard."""
    recent_imports = ImportLog.query.order_by(desc(ImportLog.created_at)).limit(5).all()
    recent_exports = ExportLog.query.order_by(desc(ExportLog.created_at)).limit(5).all()
    
    district_count = TaxDistrict.query.count()
    tax_code_count = TaxCode.query.count()
    property_count = Property.query.count()
    
    return render_template(
        "data_management/index.html",
        recent_imports=recent_imports,
        recent_exports=recent_exports,
        district_count=district_count,
        tax_code_count=tax_code_count,
        property_count=property_count
    )


@data_management_bp.route("/import", methods=["GET", "POST"])
def import_form():
    """Render the data import form."""
    if request.method == "POST":
        # Check if this is a special Benton County import request
        if 'benton_county_import' in request.form:
            try:
                # Create import log for Benton County import
                import_log = ImportLog(
                    filename="Benton County Data Import",
                    import_type=ImportType.TAX_DISTRICT,
                    status="PROCESSING",
                    year=2025,  # Hard-coded for now, should be configurable
                    notes="Started Benton County data import process"
                )
                db.session.add(import_log)
                db.session.commit()
                
                # Redirect to the Benton County import route
                flash('Benton County data import initiated', 'success')
                return redirect(url_for('data_management.import_benton_county', log_id=import_log.id))
            except Exception as e:
                logger.error(f"Error scheduling Benton County import: {str(e)}")
                flash(f'Error scheduling import: {str(e)}', 'error')
                return redirect(url_for('data_management.import_history'))
    
    # For GET requests, display the import form
    current_year = datetime.now().year
    years = list(range(current_year - 5, current_year + 2))
    import_types = [{"id": t.value, "name": t.name.replace("_", " ").title()} 
                  for t in ImportType]
    
    return render_template(
        "data_management/import.html",
        years=years,
        current_year=current_year,
        import_types=import_types
    )


@data_management_bp.route("/import/data", methods=["POST"])
def import_data():
    """Handle data import from uploaded files."""
    if "file" not in request.files:
        flash("No file part", "error")
        return redirect(url_for("data_management.import_form"))
    
    file = request.files["file"]
    if file.filename == "":
        flash("No selected file", "error")
        return redirect(request.url)
    
    if file:
        # Save the uploaded file to a temporary location
        filename = secure_filename(file.filename)
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp_path = temp.name
            file.save(temp_path)
        
        try:
            # Get import parameters
            import_type_str = request.form.get("import_type", "other")
            year = request.form.get("year", datetime.now().year)
            notes = request.form.get("notes", "")
            
            # Determine import type
            try:
                import_type = ImportType(import_type_str)
            except ValueError:
                import_type = ImportType.OTHER
            
            # Detect file type
            file_type = detect_file_type(filename)
            if not file_type:
                file_type = "unknown"
            
            # Read data from file
            try:
                data = read_data_from_file(temp_path, file_type)
            except Exception as e:
                logger.error(f"Error reading file: {str(e)}")
                flash(f"Error reading file: {str(e)}", "error")
                os.unlink(temp_path)
                return redirect(request.url)
            
            # Process the import based on type
            try:
                result = process_import(data, import_type, year)
                
                # Create import log
                import_log = ImportLog(
                    filename=filename,
                    file_type=file_type,
                    import_type=import_type,
                    record_count=result.total_count if hasattr(result, "total_count") else len(data),
                    success_count=result.success_count if hasattr(result, "success_count") else 0,
                    error_count=result.error_count if hasattr(result, "error_count") else 0,
                    status="completed",
                    notes=notes,
                    year=year,
                    metadata={"warnings": result.warnings if hasattr(result, "warnings") else []}
                )
                
                db.session.add(import_log)
                db.session.commit()
                
                # Show success message
                flash(f"Successfully imported {import_log.success_count} records from {filename}", "success")
                
            except Exception as e:
                logger.error(f"Error processing import: {str(e)}")
                flash(f"Error processing import: {str(e)}", "error")
                db.session.rollback()
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            return redirect(url_for("data_management.import_form"))
            
        except Exception as e:
            logger.error(f"Import error: {str(e)}")
            flash(f"Import error: {str(e)}", "error")
            # Clean up temporary file
            os.unlink(temp_path)
            return redirect(request.url)
    
    return redirect(request.url)


@data_management_bp.route("/export", methods=["GET"])
def export_form():
    """Render the data export form."""
    # Get available years and export types for the form
    current_year = datetime.now().year
    years = list(range(current_year - 5, current_year + 2))
    export_types = [{"id": t.value, "name": t.name.replace("_", " ").title()} 
                  for t in ExportType]
    
    # Get tax districts for filtering
    districts = TaxDistrict.query.filter_by(is_active=True).all()
    
    return render_template(
        "data_management/export.html",
        years=years,
        current_year=current_year,
        export_types=export_types,
        districts=districts
    )


@data_management_bp.route("/export", methods=["POST"])
def export_data():
    """Handle data export requests."""
    export_type_str = request.form.get("export_type", "other")
    file_type = request.form.get("file_type", "csv")
    year = request.form.get("year", datetime.now().year)
    notes = request.form.get("notes", "")
    
    # Get filter parameters
    district_ids = request.form.getlist("district_ids")
    tax_code_ids = request.form.getlist("tax_code_ids")
    
    # Convert to integers
    try:
        year = int(year)
        district_ids = [int(id) for id in district_ids if id]
        tax_code_ids = [int(id) for id in tax_code_ids if id]
    except ValueError:
        flash("Invalid parameters", "error")
        return redirect(request.url)
    
    # Determine export type
    try:
        export_type = ExportType(export_type_str)
    except ValueError:
        export_type = ExportType.OTHER
    
    # Generate export filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{export_type.value}_{year}_{timestamp}.{file_type}"
    
    # Prepare export parameters
    parameters = {
        "year": year,
        "district_ids": district_ids,
        "tax_code_ids": tax_code_ids
    }
    
    try:
        # Query the data based on export type
        data = []
        
        if export_type == ExportType.TAX_DISTRICT:
            query = TaxDistrict.query
            if district_ids:
                query = query.filter(TaxDistrict.id.in_(district_ids))
            
            districts = query.all()
            for district in districts:
                data.append({
                    "id": district.id,
                    "name": district.name,
                    "code": district.code,
                    "district_type": district.district_type,
                    "county": district.county,
                    "state": district.state,
                    "statutory_limit": district.statutory_limit
                })
                
        elif export_type == ExportType.TAX_CODE:
            query = TaxCode.query.filter_by(year=year)
            if tax_code_ids:
                query = query.filter(TaxCode.id.in_(tax_code_ids))
            
            tax_codes = query.all()
            for tax_code in tax_codes:
                data.append({
                    "id": tax_code.id,
                    "code": tax_code.code,
                    "description": tax_code.description,
                    "county": tax_code.county,
                    "state": tax_code.state,
                    "year": tax_code.year,
                    "total_levy_rate": tax_code.total_levy_rate,
                    "total_assessed_value": tax_code.total_assessed_value,
                    "districts": [d.code for d in tax_code.tax_districts]
                })
                
        elif export_type == ExportType.PROPERTY:
            query = Property.query.filter_by(year=year)
            if tax_code_ids:
                query = query.filter(Property.tax_code_id.in_(tax_code_ids))
            
            properties = query.limit(10000).all()  # Limit to 10,000 records for performance
            for prop in properties:
                data.append({
                    "id": prop.id,
                    "parcel_id": prop.parcel_id,
                    "address": prop.address,
                    "city": prop.city,
                    "county": prop.county,
                    "state": prop.state,
                    "zip_code": prop.zip_code,
                    "property_type": prop.property_type.value,
                    "tax_code_id": prop.tax_code_id,
                    "tax_code": prop.tax_code.code if prop.tax_code else None,
                    "assessed_value": prop.assessed_value,
                    "year": prop.year,
                    "land_value": prop.land_value,
                    "improvement_value": prop.improvement_value
                })
                
        elif export_type == ExportType.LEVY_REPORT:
            # Specialized levy report format
            districts = TaxDistrict.query
            if district_ids:
                districts = districts.filter(TaxDistrict.id.in_(district_ids))
            districts = districts.all()
            
            tax_codes = TaxCode.query.filter_by(year=year)
            if tax_code_ids:
                tax_codes = tax_codes.filter(TaxCode.id.in_(tax_code_ids))
            tax_codes = tax_codes.all()
            
            # For each district, collect levy rates across tax codes
            for district in districts:
                district_data = {
                    "district_id": district.id,
                    "district_name": district.name,
                    "district_code": district.code,
                    "district_type": district.district_type,
                    "statutory_limit": district.statutory_limit,
                    "tax_codes": []
                }
                
                for tax_code in (tc for tc in tax_codes if district in tc.tax_districts):
                    # Find historical rate for this district and tax code
                    historical_rate = next((hr for hr in tax_code.historical_rates 
                                           if hr.tax_district_id == district.id and hr.year == year), None)
                    
                    tax_code_data = {
                        "tax_code_id": tax_code.id,
                        "tax_code": tax_code.code,
                        "levy_rate": historical_rate.levy_rate if historical_rate else None,
                        "levy_amount": historical_rate.levy_amount if historical_rate else None,
                        "assessed_value": historical_rate.assessed_value if historical_rate else None
                    }
                    
                    district_data["tax_codes"].append(tax_code_data)
                
                data.append(district_data)
        
        # Create export log
        export_log = ExportLog(
            filename=filename,
            file_type=file_type,
            export_type=export_type,
            record_count=len(data),
            status="completed",
            parameters=parameters,
            notes=notes,
            year=year
        )
        
        db.session.add(export_log)
        db.session.commit()
        
        # Prepare the file for download
        if file_type == "json":
            # JSON response
            response_data = json.dumps(data, indent=2, cls=DateTimeEncoder)
            mimetype = "application/json"
        elif file_type == "csv":
            # CSV response (simplified - should use pandas in production)
            import csv
            from io import StringIO
            
            output = StringIO()
            if data:
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            response_data = output.getvalue()
            mimetype = "text/csv"
        else:
            # Default to JSON
            response_data = json.dumps(data, indent=2, cls=DateTimeEncoder)
            mimetype = "application/json"
        
        # Create response
        response = Response(
            response_data,
            mimetype=mimetype,
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        flash(f"Export error: {str(e)}", "error")
        return redirect(request.url)


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for handling datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


@data_management_bp.route("/tax-districts", methods=["GET"])
def list_tax_districts():
    """List all tax districts."""
    districts = TaxDistrict.query.all()
    return render_template(
        "data_management/tax_districts.html", 
        districts=districts
    )


@data_management_bp.route("/tax-districts/<int:district_id>", methods=["GET"])
def view_tax_district(district_id):
    """View a single tax district."""
    district = TaxDistrict.query.get_or_404(district_id)
    return render_template(
        "data_management/tax_district_detail.html", 
        district=district
    )


@data_management_bp.route("/tax-codes", methods=["GET"])
def list_tax_codes():
    """List all tax codes."""
    year = request.args.get("year", datetime.now().year, type=int)
    tax_codes = TaxCode.query.filter_by(year=year).all()
    
    # Get available years for the filter
    years = db.session.query(TaxCode.year).distinct().order_by(TaxCode.year).all()
    years = [y[0] for y in years]
    
    return render_template(
        "data_management/tax_codes.html", 
        tax_codes=tax_codes,
        year=year,
        years=years
    )


@data_management_bp.route("/tax-codes/<int:tax_code_id>", methods=["GET"])
def view_tax_code(tax_code_id):
    """View a single tax code."""
    tax_code = TaxCode.query.get_or_404(tax_code_id)
    return render_template(
        "data_management/tax_code_detail.html", 
        tax_code=tax_code
    )


@data_management_bp.route("/import/benton-county/<int:log_id>", methods=["GET"])
def import_benton_county(log_id):
    """Run the Benton County data import process."""
    import_log = ImportLog.query.get_or_404(log_id)
    
    try:
        # Import the Benton County data import module
        from import_benton_county_data import (
            import_districts_from_worksheets,
            import_tax_codes_from_cert_report,
            import_levy_rates,
            import_preliminary_values
        )
        
        # Update the import log status
        import_log.status = "RUNNING"
        import_log.notes = "Running Benton County data import process"
        db.session.commit()
        
        # Run the import steps
        success_messages = []
        
        # Step 1: Import tax districts from levy worksheets
        try:
            import_districts_from_worksheets()
            success_messages.append("Successfully imported tax districts")
        except Exception as e:
            logger.error(f"Error importing tax districts: {str(e)}")
            import_log.status = "FAILED"
            import_log.notes = f"Error importing tax districts: {str(e)}"
            db.session.commit()
            flash(f"Error importing tax districts: {str(e)}", "error")
            return render_template("data_management/import_status.html", import_log=import_log)
        
        # Step 2: Import tax codes from certification report
        try:
            import_tax_codes_from_cert_report()
            success_messages.append("Successfully imported tax codes")
        except Exception as e:
            logger.error(f"Error importing tax codes: {str(e)}")
            import_log.status = "FAILED"
            import_log.notes = f"Error importing tax codes: {str(e)}"
            db.session.commit()
            flash(f"Error importing tax codes: {str(e)}", "error")
            return render_template("data_management/import_status.html", import_log=import_log)
        
        # Step 3: Import levy rates
        try:
            import_levy_rates()
            success_messages.append("Successfully imported levy rates")
        except Exception as e:
            logger.error(f"Error importing levy rates: {str(e)}")
            import_log.status = "FAILED"
            import_log.notes = f"Error importing levy rates: {str(e)}"
            db.session.commit()
            flash(f"Error importing levy rates: {str(e)}", "error")
            return render_template("data_management/import_status.html", import_log=import_log)
        
        # Step 4: Import preliminary assessed values
        try:
            import_preliminary_values()
            success_messages.append("Successfully imported preliminary values")
        except Exception as e:
            logger.error(f"Error importing preliminary values: {str(e)}")
            import_log.status = "FAILED"
            import_log.notes = f"Error importing preliminary values: {str(e)}"
            db.session.commit()
            flash(f"Error importing preliminary values: {str(e)}", "error")
            return render_template("data_management/import_status.html", import_log=import_log)
        
        # Update the import log with success status
        import_log.status = "COMPLETED"
        import_log.notes = "Benton County data import completed successfully"
        db.session.commit()
        
        # Show success messages
        for message in success_messages:
            flash(message, "success")
        
        return render_template("data_management/import_status.html", import_log=import_log)
        
    except Exception as e:
        logger.error(f"Error in Benton County import process: {str(e)}")
        import_log.status = "FAILED"
        import_log.notes = f"Error in Benton County import process: {str(e)}"
        db.session.commit()
        flash(f"Error in Benton County import process: {str(e)}", "error")
        return render_template("data_management/import_status.html", import_log=import_log)


@data_management_bp.route("/import/district", methods=["GET", "POST"])
def import_district():
    """Handle import of tax district data."""
    if request.method == "GET":
        # Render the district import form with preview functionality
        current_year = datetime.now().year
        years = list(range(current_year - 5, current_year + 2))
        
        return render_template(
            "data_management/district_import.html",
            years=years,
            current_year=current_year
        )
    
    # Process the file upload (POST method)
    if "file" not in request.files:
        flash("No file part", "error")
        return redirect(request.url)
    
    file = request.files["file"]
    if file.filename == "":
        flash("No selected file", "error")
        return redirect(request.url)
    
    if file:
        # Save the uploaded file to a temporary location
        filename = secure_filename(file.filename)
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp_path = temp.name
            file.save(temp_path)
        
        try:
            # Determine file type and import
            result = None
            extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else None
            
            # Get the year from the form if provided, otherwise use current year
            year = request.form.get("year", datetime.now().year)
            try:
                year = int(year)
            except ValueError:
                year = datetime.now().year
                
            if extension == 'txt':
                result = import_district_text_file(temp_path)
            elif extension == 'xml':
                result = import_district_xml_file(temp_path)
            elif extension in ['xls', 'xlsx', 'xlsm']:
                # For Excel files, we need to load the file with openpyxl or xlrd and pass to import function
                # This is a placeholder; you would need to implement this based on how your Excel parser works
                from openpyxl import load_workbook
                wb = load_workbook(temp_path)
                result = import_excel_xml_file(wb.active)
            else:
                flash(f"Unsupported file format: {extension}", "error")
                os.unlink(temp_path)
                return redirect(request.url)
                
            # Check the result
            if result and result.get('success', False):
                flash(f"Successfully imported {result.get('imported', 0)} tax district records. "
                      f"Skipped {result.get('skipped', 0)} records.", "success")
                
                # Create import log
                import_log = ImportLog(
                    filename=filename,
                    import_type=ImportType.TAX_DISTRICT,
                    record_count=result.get('imported', 0) + result.get('skipped', 0),
                    success_count=result.get('imported', 0),
                    error_count=result.get('skipped', 0),
                    status="completed",
                    year=year,
                    import_metadata={"warnings": result.get('warnings', [])}
                )
                
                db.session.add(import_log)
                db.session.commit()
            else:
                warnings = result.get('warnings', []) if result else ["Unknown error"]
                flash(f"Error importing tax district data: {'; '.join(warnings[:3])}", "error")
                
            # Clean up temporary file
            os.unlink(temp_path)
            
            return redirect(url_for("data_management.list_tax_districts"))
                
        except Exception as e:
            logger.error(f"District import error: {str(e)}")
            flash(f"District import error: {str(e)}", "error")
            # Clean up temporary file
            os.unlink(temp_path)
            return redirect(request.url)

@data_management_bp.route("/properties", methods=["GET"])
def list_properties():
    """List properties with filtering options."""
    # Get filter parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 25, type=int)
    year = request.args.get("year", datetime.now().year, type=int)
    tax_code_id = request.args.get("tax_code_id", None, type=int)
    property_type = request.args.get("property_type", None)
    search = request.args.get("search", "")
    
    # Build query
    query = Property.query.filter_by(year=year)
    
    if tax_code_id:
        query = query.filter_by(tax_code_id=tax_code_id)
    
    if property_type:
        try:
            prop_type_enum = PropertyType(property_type)
            query = query.filter_by(property_type=prop_type_enum)
        except ValueError:
            pass
    
    if search:
        query = query.filter(
            or_(
                Property.parcel_id.ilike(f"%{search}%"),
                Property.address.ilike(f"%{search}%")
            )
        )
    
    # Paginate results
    properties = query.paginate(page=page, per_page=per_page)
    
    # Get available years for the filter
    years = db.session.query(Property.year).distinct().order_by(Property.year).all()
    years = [y[0] for y in years]
    
    # Get tax codes for filter
    tax_codes = TaxCode.query.filter_by(year=year).all()
    
    # Property types for filter
    property_types = [{"id": pt.value, "name": pt.name.title()} for pt in PropertyType]
    
    return render_template(
        "data_management/properties.html",
        properties=properties,
        year=year,
        years=years,
        tax_codes=tax_codes,
        selected_tax_code_id=tax_code_id,
        property_types=property_types,
        selected_property_type=property_type,
        search=search
    )


@data_management_bp.route("/properties/<int:property_id>", methods=["GET"])
def view_property(property_id):
    """View a single property record."""
    property = Property.query.get_or_404(property_id)
    return render_template(
        "data_management/property_detail.html", 
        property=property
    )


@data_management_bp.route("/import-history", methods=["GET"])
def import_history():
    """View import history and logs."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 25, type=int)
    
    imports = ImportLog.query.order_by(desc(ImportLog.created_at)).paginate(page=page, per_page=per_page)
    
    return render_template(
        "data_management/import_history.html",
        imports=imports
    )


@data_management_bp.route("/export-history", methods=["GET"])
def export_history():
    """View export history and logs."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 25, type=int)
    
    exports = ExportLog.query.order_by(desc(ExportLog.created_at)).paginate(page=page, per_page=per_page)
    
    return render_template(
        "data_management/export_history.html",
        exports=exports
    )
@data_management_bp.route("/api/preview-district-import", methods=["POST"])
def preview_district_import():
    """
    API endpoint to preview district data import without committing to the database.
    Returns JSON response with preview data.
    """
    if "file" not in request.files:
        return jsonify({
            "success": False,
            "message": "No file provided"
        })
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({
            "success": False,
            "message": "No file selected"
        })
    
    try:
        # Save the uploaded file to a temporary location
        filename = secure_filename(file.filename)
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp_path = temp.name
            file.save(temp_path)
        
        # Extract year override if provided
        year_override = request.form.get("year")
        if year_override:
            try:
                year_override = int(year_override)
            except ValueError:
                year_override = None
        
        # Detect file type
        file_type = detect_file_type(filename)
        if not file_type:
            file_type = "unknown"
        
        # Extract districts from the file for preview
        result = extract_districts_from_file(temp_path, file_type, year_override)
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        # Get a sample of districts for preview (limit to 15 for performance)
        sample_size = min(15, len(result.get('districts', [])))
        sample_districts = result.get('districts', [])[:sample_size]
        
        # Return JSON response
        response = {
            "success": result.get('success', False),
            "message": "District data preview generated successfully",
            "districts": sample_districts,
            "total_count": result.get('count', 0),
            "sample_count": sample_size,
            "file_type": file_type
        }
        
        if not result.get('success', False):
            response["message"] = result.get('error', "Failed to preview district data")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error generating preview: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error generating preview: {str(e)}"
        })
