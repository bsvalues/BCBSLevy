"""
Core routes for the Levy Calculation Application.

This module provides the main routes for the application including
the dashboard, home page, and user settings.
"""
from flask import Blueprint, render_template, request, jsonify, current_app, session, redirect, url_for

from app2 import db
from models import TaxCode, Property, TaxDistrict

# Create a blueprint for the home routes
home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    """Render the home/landing page."""
    return render_template('index.html', page_title="Levy Calculation System")

@home_bp.route('/dashboard')
def dashboard():
    """Render the main dashboard."""
    # Summary statistics
    tax_code_count = TaxCode.query.distinct(TaxCode.code).count()
    property_count = Property.query.count()
    district_count = TaxDistrict.query.distinct(TaxDistrict.tax_district_id).count()
    
    # Recent tax codes
    recent_tax_codes = TaxCode.query.order_by(TaxCode.updated_at.desc()).limit(5).all()
    
    return render_template(
        'dashboard.html',
        page_title="Dashboard",
        tax_code_count=tax_code_count,
        property_count=property_count,
        district_count=district_count,
        recent_tax_codes=recent_tax_codes
    )

@home_bp.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html', page_title="About")

@home_bp.route('/settings')
def settings():
    """Render the settings page."""
    return render_template('settings.html', page_title="Settings")

@home_bp.route('/help')
def help_page():
    """Render the help page."""
    return render_template('help.html', page_title="Help & Documentation")