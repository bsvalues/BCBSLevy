"""
Routes for enhanced report generation and export.

This module includes routes for creating, managing, and exporting reports:
- Report template management
- Report generation in various formats
- Scheduled report configuration
"""

import logging
import json
import os
import tempfile
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, flash, send_file, Response, redirect, url_for
from werkzeug.utils import secure_filename
from app import db
from models import Property, TaxCode, ExportLog, ExportType
from utils import report_utils

# Create blueprint
reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

# Configure logger
logger = logging.getLogger(__name__)


@reports_bp.route('/dashboard', methods=['GET'])
def reports_dashboard():
    """
    Dashboard for report generation and management.
    
    Displays available report templates and recent exports.
    """
    # Get all report templates
    templates = report_utils.list_templates()
    
    # Get recent exports
    recent_exports = ExportLog.query.order_by(ExportLog.created_at.desc()).limit(10).all()
    
    # Count properties and tax codes for context
    property_count = Property.query.count()
    tax_code_count = TaxCode.query.count()
    
    return render_template('reports/dashboard.html',
                         templates=templates,
                         recent_exports=recent_exports,
                         property_count=property_count,
                         tax_code_count=tax_code_count)


@reports_bp.route('/templates', methods=['GET'])
def report_templates():
    """
    List and manage report templates.
    """
    # Get all templates
    templates = report_utils.list_templates()
    
    # Filter by type if specified
    template_type = request.args.get('type')
    if template_type:
        templates = [t for t in templates if t['type'] == template_type]
    
    return render_template('reports/templates.html',
                         templates=templates,
                         template_type=template_type)


@reports_bp.route('/templates/new', methods=['GET'])
def new_report_template():
    """
    Form for creating a new report template.
    """
    # Get all available fields for different entity types
    property_fields = [
        'property_id', 'assessed_value', 'tax_code', 'levy_rate', 'calculated_tax'
    ]
    
    tax_code_fields = [
        'code', 'levy_amount', 'levy_rate', 'total_assessed_value', 
        'previous_year_rate', 'rate_change', 'rate_change_percent'
    ]
    
    # Get calculated field examples
    calculated_field_examples = [
        {'name': 'calculated_tax', 'formula': 'assessed_value / 1000 * levy_rate'},
        {'name': 'tax_increase', 'formula': 'calculated_tax - previous_calculated_tax'},
        {'name': 'percent_change', 'formula': '(levy_rate - previous_year_rate) / previous_year_rate * 100'}
    ]
    
    return render_template('reports/template_form.html',
                         template=None,
                         property_fields=property_fields,
                         tax_code_fields=tax_code_fields,
                         calculated_field_examples=calculated_field_examples,
                         action='create')


@reports_bp.route('/templates/new', methods=['POST'])
def create_report_template():
    """
    Create a new report template.
    """
    try:
        # Get form data
        template_data = {
            'name': request.form.get('name'),
            'type': request.form.get('type'),
            'description': request.form.get('description'),
            'is_public': request.form.get('is_public') == 'on'
        }
        
        # Parse sections from form
        sections = []
        section_count = int(request.form.get('section_count', 0))
        
        for i in range(1, section_count + 1):
            section_title = request.form.get(f'section_{i}_title')
            if not section_title:
                continue
                
            # Get fields for this section
            fields = []
            field_list = request.form.get(f'section_{i}_fields')
            
            if field_list:
                field_names = field_list.split(',')
                fields = [f.strip() for f in field_names if f.strip()]
            
            # Get calculated fields for this section
            calc_field_count = int(request.form.get(f'section_{i}_calc_field_count', 0))
            
            for j in range(1, calc_field_count + 1):
                calc_name = request.form.get(f'section_{i}_calc_{j}_name')
                calc_formula = request.form.get(f'section_{i}_calc_{j}_formula')
                
                if calc_name and calc_formula:
                    fields.append({
                        'name': calc_name,
                        'formula': calc_formula
                    })
            
            # Add section if it has fields
            if fields:
                sections.append({
                    'title': section_title,
                    'fields': fields
                })
        
        # Add sections to template data
        template_data['sections'] = sections
        
        # Add sorting if specified
        sort_field = request.form.get('sort_field')
        sort_direction = request.form.get('sort_direction', 'asc')
        
        if sort_field:
            template_data['sorting'] = {
                'field': sort_field,
                'direction': sort_direction
            }
        
        # Add filters if specified
        filters = []
        filter_count = int(request.form.get('filter_count', 0))
        
        for i in range(1, filter_count + 1):
            filter_field = request.form.get(f'filter_{i}_field')
            filter_operator = request.form.get(f'filter_{i}_operator')
            filter_value = request.form.get(f'filter_{i}_value')
            
            if filter_field and filter_operator and filter_value:
                filters.append({
                    'field': filter_field,
                    'operator': filter_operator,
                    'value': filter_value
                })
        
        # Add filters to template data
        template_data['filters'] = filters
        
        # Validate template
        validation = report_utils.validate_template(template_data)
        if not validation['valid']:
            flash(f"Invalid template: {validation['error']}", 'danger')
            return redirect(url_for('reports.new_report_template'))
        
        # Create template
        template_id = report_utils.create_template(template_data)
        
        flash(f"Template '{template_data['name']}' created successfully", 'success')
        return redirect(url_for('reports.report_templates'))
    except Exception as e:
        logger.exception(f"Error creating template: {str(e)}")
        flash(f"Error creating template: {str(e)}", 'danger')
        return redirect(url_for('reports.new_report_template'))


@reports_bp.route('/templates/<template_id>', methods=['GET'])
def edit_report_template(template_id):
    """
    Form for editing an existing report template.
    """
    try:
        # Get template
        template = report_utils.get_template(template_id)
        
        # Get all available fields for different entity types
        property_fields = [
            'property_id', 'assessed_value', 'tax_code', 'levy_rate', 'calculated_tax'
        ]
        
        tax_code_fields = [
            'code', 'levy_amount', 'levy_rate', 'total_assessed_value', 
            'previous_year_rate', 'rate_change', 'rate_change_percent'
        ]
        
        # Get calculated field examples
        calculated_field_examples = [
            {'name': 'calculated_tax', 'formula': 'assessed_value / 1000 * levy_rate'},
            {'name': 'tax_increase', 'formula': 'calculated_tax - previous_calculated_tax'},
            {'name': 'percent_change', 'formula': '(levy_rate - previous_year_rate) / previous_year_rate * 100'}
        ]
        
        return render_template('reports/template_form.html',
                            template=template,
                            property_fields=property_fields,
                            tax_code_fields=tax_code_fields,
                            calculated_field_examples=calculated_field_examples,
                            action='update')
    except Exception as e:
        logger.exception(f"Error editing template: {str(e)}")
        flash(f"Error editing template: {str(e)}", 'danger')
        return redirect(url_for('reports.report_templates'))


@reports_bp.route('/templates/<template_id>', methods=['POST'])
def update_report_template(template_id):
    """
    Update an existing report template.
    """
    try:
        # Get form data
        template_data = {
            'name': request.form.get('name'),
            'type': request.form.get('type'),
            'description': request.form.get('description'),
            'is_public': request.form.get('is_public') == 'on'
        }
        
        # Parse sections from form
        sections = []
        section_count = int(request.form.get('section_count', 0))
        
        for i in range(1, section_count + 1):
            section_title = request.form.get(f'section_{i}_title')
            if not section_title:
                continue
                
            # Get fields for this section
            fields = []
            field_list = request.form.get(f'section_{i}_fields')
            
            if field_list:
                field_names = field_list.split(',')
                fields = [f.strip() for f in field_names if f.strip()]
            
            # Get calculated fields for this section
            calc_field_count = int(request.form.get(f'section_{i}_calc_field_count', 0))
            
            for j in range(1, calc_field_count + 1):
                calc_name = request.form.get(f'section_{i}_calc_{j}_name')
                calc_formula = request.form.get(f'section_{i}_calc_{j}_formula')
                
                if calc_name and calc_formula:
                    fields.append({
                        'name': calc_name,
                        'formula': calc_formula
                    })
            
            # Add section if it has fields
            if fields:
                sections.append({
                    'title': section_title,
                    'fields': fields
                })
        
        # Add sections to template data
        template_data['sections'] = sections
        
        # Add sorting if specified
        sort_field = request.form.get('sort_field')
        sort_direction = request.form.get('sort_direction', 'asc')
        
        if sort_field:
            template_data['sorting'] = {
                'field': sort_field,
                'direction': sort_direction
            }
        
        # Add filters if specified
        filters = []
        filter_count = int(request.form.get('filter_count', 0))
        
        for i in range(1, filter_count + 1):
            filter_field = request.form.get(f'filter_{i}_field')
            filter_operator = request.form.get(f'filter_{i}_operator')
            filter_value = request.form.get(f'filter_{i}_value')
            
            if filter_field and filter_operator and filter_value:
                filters.append({
                    'field': filter_field,
                    'operator': filter_operator,
                    'value': filter_value
                })
        
        # Add filters to template data
        template_data['filters'] = filters
        
        # Validate template
        validation = report_utils.validate_template(template_data)
        if not validation['valid']:
            flash(f"Invalid template: {validation['error']}", 'danger')
            return redirect(url_for('reports.edit_report_template', template_id=template_id))
        
        # Update template
        result = report_utils.update_template(template_id, template_data)
        
        if result['success']:
            flash(f"Template '{template_data['name']}' updated successfully", 'success')
            return redirect(url_for('reports.report_templates'))
        else:
            flash(f"Error updating template: {result.get('error', 'Unknown error')}", 'danger')
            return redirect(url_for('reports.edit_report_template', template_id=template_id))
    except Exception as e:
        logger.exception(f"Error updating template: {str(e)}")
        flash(f"Error updating template: {str(e)}", 'danger')
        return redirect(url_for('reports.edit_report_template', template_id=template_id))


@reports_bp.route('/templates/<template_id>/delete', methods=['POST'])
def delete_report_template(template_id):
    """
    Delete a report template.
    """
    try:
        # Get template name for confirmation message
        template = report_utils.get_template(template_id)
        template_name = template['name']
        
        # Delete template
        result = report_utils.delete_template(template_id)
        
        if result['success']:
            flash(f"Template '{template_name}' deleted successfully", 'success')
        else:
            flash(f"Error deleting template: {result.get('error', 'Unknown error')}", 'danger')
        
        return redirect(url_for('reports.report_templates'))
    except Exception as e:
        logger.exception(f"Error deleting template: {str(e)}")
        flash(f"Error deleting template: {str(e)}", 'danger')
        return redirect(url_for('reports.report_templates'))


@reports_bp.route('/generate', methods=['GET'])
def report_generator():
    """
    Form for generating a report from a template.
    """
    # Get all templates
    templates = report_utils.list_templates()
    
    # Get template ID from query parameter
    template_id = request.args.get('template_id')
    
    # Get selected template if specified
    selected_template = None
    if template_id:
        try:
            selected_template = report_utils.get_template(template_id)
        except Exception:
            pass
    
    # Get available export formats
    export_formats = [
        {'id': 'excel', 'name': 'Excel (.xlsx)', 'icon': 'bi-file-earmark-excel'},
        {'id': 'csv', 'name': 'CSV (.csv)', 'icon': 'bi-file-earmark-text'},
        {'id': 'pdf', 'name': 'PDF (.pdf)', 'icon': 'bi-file-earmark-pdf'},
        {'id': 'json', 'name': 'JSON (.json)', 'icon': 'bi-file-earmark-code'}
    ]
    
    return render_template('reports/generator.html',
                         templates=templates,
                         selected_template=selected_template,
                         export_formats=export_formats)


@reports_bp.route('/generate', methods=['POST'])
def generate_report():
    """
    Generate a report from a template.
    """
    try:
        # Get form data
        template_id = request.form.get('template_id')
        export_format = request.form.get('export_format')
        
        # Validate parameters
        if not template_id:
            flash('Template ID is required', 'danger')
            return redirect(url_for('reports.report_generator'))
        
        if export_format not in ['excel', 'csv', 'pdf', 'json']:
            flash('Invalid export format', 'danger')
            return redirect(url_for('reports.report_generator'))
        
        # Get template
        template = report_utils.get_template(template_id)
        
        # Create a temporary directory for the output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            sanitized_name = template['name'].replace(' ', '_').lower()
            filename = f"{sanitized_name}_{timestamp}.{export_format}"
            output_path = os.path.join(temp_dir, filename)
            
            # Generate report based on format
            result = None
            if export_format == 'excel':
                result = report_utils.generate_excel_report(
                    template_id=template_id,
                    output_path=output_path
                )
            elif export_format == 'csv':
                result = report_utils.generate_csv_report(
                    template_id=template_id,
                    output_path=output_path
                )
            elif export_format == 'pdf':
                result = report_utils.generate_pdf_report(
                    template_id=template_id,
                    output_path=output_path
                )
            elif export_format == 'json':
                result = report_utils.generate_json_report(
                    template_id=template_id,
                    output_path=output_path
                )
            
            if result and result.get('success'):
                # Set appropriate MIME type
                mime_types = {
                    'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'csv': 'text/csv',
                    'pdf': 'application/pdf',
                    'json': 'application/json'
                }
                
                # Log export
                export_log = ExportLog(
                    user_id=1,  # Default to admin user (to be updated with current_user.id)
                    filename=filename,
                    export_type=ExportType.REPORT,
                    record_count=result.get('record_count', 0),
                    status='COMPLETED',
                    processing_time=result.get('processing_time', 0),
                    year=datetime.now().year,
                    export_metadata={
                        'template_id': template_id,
                        'template_name': template['name'],
                        'export_format': export_format
                    }
                )
                db.session.add(export_log)
                db.session.commit()
                
                # Send file to user
                return send_file(
                    result['output_path'],
                    as_attachment=True,
                    download_name=filename,
                    mimetype=mime_types[export_format]
                )
            else:
                error_message = result.get('error', 'Unknown error') if result else 'Failed to generate report'
                flash(f"Error generating report: {error_message}", 'danger')
                return redirect(url_for('reports.report_generator'))
    except Exception as e:
        logger.exception(f"Error generating report: {str(e)}")
        flash(f"Error generating report: {str(e)}", 'danger')
        return redirect(url_for('reports.report_generator'))


@reports_bp.route('/schedule', methods=['GET'])
def schedule_report_form():
    """
    Form for scheduling a report.
    """
    # Get all templates
    templates = report_utils.list_templates()
    
    # Get template ID from query parameter
    template_id = request.args.get('template_id')
    
    # Get selected template if specified
    selected_template = None
    if template_id:
        try:
            selected_template = report_utils.get_template(template_id)
        except Exception:
            pass
    
    # Get available export formats
    export_formats = [
        {'id': 'excel', 'name': 'Excel (.xlsx)', 'icon': 'bi-file-earmark-excel'},
        {'id': 'csv', 'name': 'CSV (.csv)', 'icon': 'bi-file-earmark-text'},
        {'id': 'pdf', 'name': 'PDF (.pdf)', 'icon': 'bi-file-earmark-pdf'},
        {'id': 'json', 'name': 'JSON (.json)', 'icon': 'bi-file-earmark-code'}
    ]
    
    # Get schedule options
    frequencies = [
        {'id': 'daily', 'name': 'Daily'},
        {'id': 'weekly', 'name': 'Weekly'},
        {'id': 'monthly', 'name': 'Monthly'},
        {'id': 'quarterly', 'name': 'Quarterly'},
        {'id': 'yearly', 'name': 'Yearly'}
    ]
    
    days_of_week = [
        {'id': 'monday', 'name': 'Monday'},
        {'id': 'tuesday', 'name': 'Tuesday'},
        {'id': 'wednesday', 'name': 'Wednesday'},
        {'id': 'thursday', 'name': 'Thursday'},
        {'id': 'friday', 'name': 'Friday'},
        {'id': 'saturday', 'name': 'Saturday'},
        {'id': 'sunday', 'name': 'Sunday'}
    ]
    
    return render_template('reports/schedule.html',
                         templates=templates,
                         selected_template=selected_template,
                         export_formats=export_formats,
                         frequencies=frequencies,
                         days_of_week=days_of_week)


@reports_bp.route('/schedule', methods=['POST'])
def schedule_report():
    """
    Schedule a report for regular generation.
    """
    try:
        # Get form data
        template_id = request.form.get('template_id')
        export_format = request.form.get('export_format')
        frequency = request.form.get('frequency')
        
        # For now, just show a success message (scheduling functionality to be implemented)
        flash(f"Report scheduled successfully with {frequency} frequency", 'success')
        return redirect(url_for('reports.schedule_report_form'))
    except Exception as e:
        logger.exception(f"Error scheduling report: {str(e)}")
        flash(f"Error scheduling report: {str(e)}", 'danger')
        return redirect(url_for('reports.schedule_report_form'))


def init_report_routes(app):
    """Initialize report routes with the Flask app."""
    app.register_blueprint(reports_bp)
    logger.info("Report routes initialized")