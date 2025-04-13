"""
Database models for the Levy Calculation System.

This module defines the database models representing the core entities
of the levy calculation system, including tax districts, tax codes,
properties, rates, and user information.
"""

from datetime import datetime
from enum import Enum, auto
from typing import List, Optional, Dict, Any, Union

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, ForeignKey, 
    Text, UniqueConstraint, Index, JSON, Enum as SQLEnum, CheckConstraint
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship, backref
from flask_login import UserMixin

from app import db


# Enums for model constraints
class PropertyType(Enum):
    """Property types for classification."""
    RESIDENTIAL = auto()
    COMMERCIAL = auto()
    INDUSTRIAL = auto()
    AGRICULTURAL = auto()
    PUBLIC = auto()
    OTHER = auto()


class ImportType(Enum):
    """Types of data imports."""
    TAX_DISTRICT = "TAX_DISTRICT"
    TAX_CODE = "TAX_CODE"
    PROPERTY = "PROPERTY"
    RATE = "RATE"
    LEVY = "LEVY"
    OTHER = "OTHER"


class ExportType(Enum):
    """Types of data exports."""
    TAX_DISTRICT = "TAX_DISTRICT"
    TAX_CODE = "TAX_CODE"
    PROPERTY = "PROPERTY"
    RATE = "RATE"
    LEVY = "LEVY"
    REPORT = "REPORT"
    LEVY_REPORT = "LEVY_REPORT"
    ANALYSIS = "ANALYSIS"
    OTHER = "OTHER"


class AuditMixin:
    """Mixin to add audit timestamps to models."""
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    @declared_attr
    def created_by_id(cls):
        return Column(Integer, ForeignKey('user.id'), nullable=True)
    
    @declared_attr
    def updated_by_id(cls):
        return Column(Integer, ForeignKey('user.id'), nullable=True)
    
    @declared_attr
    def created_by(cls):
        """Create relationship with User model for created_by."""
        return relationship('User', foreign_keys=[cls.created_by_id])
    
    @declared_attr
    def updated_by(cls):
        """Create relationship with User model for updated_by."""
        return relationship('User', foreign_keys=[cls.updated_by_id])


class YearMixin:
    """Mixin to add tax year to models."""
    
    year = Column(Integer, nullable=False, index=True)


class User(UserMixin, db.Model):
    """
    User model for authentication and authorization.
    """
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    first_name = Column(String(64))
    last_name = Column(String(64))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Non-audit fields use modified constructor
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def full_name(self):
        """Return the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username


class TaxDistrict(AuditMixin, YearMixin, db.Model):
    """
    Tax district model representing a levy authority (e.g., school district, fire district).
    """
    __tablename__ = 'tax_district'
    
    id = Column(Integer, primary_key=True)
    district_name = Column(String(128), nullable=False)
    district_code = Column(String(16), nullable=False)
    district_type = Column(String(64))  # e.g., school, fire, county, city
    county = Column(String(64))
    state = Column(String(2))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    contact_name = Column(String(128))
    contact_email = Column(String(128))
    contact_phone = Column(String(20))
    statutory_limit = Column(Float)  # Maximum levy rate allowed by law
    tax_district_id = Column(Integer)  # For district import through district_utils
    levy_code = Column(String(16))  # For district import through district_utils
    linked_levy_code = Column(String(16))  # For district import through district_utils
    
    # Relationships
    tax_codes = relationship('TaxCode', back_populates='tax_district')
    levy_rates = relationship('LevyRate', back_populates='tax_district')
    
    # Ensure district_code is unique per year
    __table_args__ = (
        UniqueConstraint('district_code', 'year', name='uix_district_code_year'),
    )
    
    def __repr__(self):
        return f'<TaxDistrict {self.district_name} ({self.district_code})>'


class TaxCode(AuditMixin, YearMixin, db.Model):
    """
    Tax code model representing a specific tax code area.
    """
    __tablename__ = 'tax_code'
    
    id = Column(Integer, primary_key=True)
    tax_code = Column(String(16), nullable=False, index=True)
    tax_district_id = Column(Integer, ForeignKey('tax_district.id'), nullable=False, index=True)
    description = Column(Text)
    total_assessed_value = Column(Float, default=0.0)
    total_levy_amount = Column(Float, default=0.0)
    effective_tax_rate = Column(Float, default=0.0)  # Per $1,000 of assessed value
    
    # Relationships
    tax_district = relationship('TaxDistrict', back_populates='tax_codes')
    properties = relationship('Property', back_populates='tax_code')
    historical_rates = relationship('TaxCodeHistoricalRate', back_populates='tax_code')
    
    # Ensure tax_code is unique per tax_district_id and year
    __table_args__ = (
        UniqueConstraint('tax_code', 'tax_district_id', 'year', name='uix_tax_code_district_year'),
    )
    
    def __repr__(self):
        return f'<TaxCode {self.tax_code}>'


class TaxCodeHistoricalRate(AuditMixin, db.Model):
    """
    Historical tax rates for each tax code by year.
    """
    __tablename__ = 'tax_code_historical_rate'
    
    id = Column(Integer, primary_key=True)
    tax_code_id = Column(Integer, ForeignKey('tax_code.id'), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    levy_rate = Column(Float, nullable=False)
    levy_amount = Column(Float, nullable=True)
    total_assessed_value = Column(Float, nullable=True)
    
    # Relationships
    tax_code = relationship('TaxCode', back_populates='historical_rates')
    
    # Ensure one record per tax_code_id and year
    __table_args__ = (
        UniqueConstraint('tax_code_id', 'year', name='uix_tax_code_year'),
    )
    
    def __repr__(self):
        return f'<TaxCodeHistoricalRate {self.tax_code_id} Y:{self.year} R:{self.levy_rate}>'


class Property(AuditMixin, YearMixin, db.Model):
    """
    Property model representing individual taxable properties.
    """
    __tablename__ = 'property'
    
    id = Column(Integer, primary_key=True)
    property_id = Column(String(64), nullable=False, index=True)
    tax_code_id = Column(Integer, ForeignKey('tax_code.id'), nullable=False, index=True)
    owner_name = Column(String(128))
    property_address = Column(String(256))
    city = Column(String(64))
    state = Column(String(2))
    zip_code = Column(String(10))
    property_type = Column(SQLEnum(PropertyType))
    assessed_value = Column(Float, default=0.0)
    market_value = Column(Float)
    land_value = Column(Float)
    building_value = Column(Float)
    tax_exempt = Column(Boolean, default=False)
    exemption_amount = Column(Float, default=0.0)
    taxable_value = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    longitude = Column(Float)
    latitude = Column(Float)
    
    # Relationships
    tax_code = relationship('TaxCode', back_populates='properties')
    
    # Ensure property_id is unique per year
    __table_args__ = (
        UniqueConstraint('property_id', 'year', name='uix_property_year'),
        Index('idx_property_location', 'longitude', 'latitude'),
    )
    
    def __repr__(self):
        return f'<Property {self.property_id}>'


class LevyRate(AuditMixin, YearMixin, db.Model):
    """
    Levy rate model for setting and tracking tax rates by district.
    """
    __tablename__ = 'levy_rate'
    
    id = Column(Integer, primary_key=True)
    tax_district_id = Column(Integer, ForeignKey('tax_district.id'), nullable=False, index=True)
    levy_rate = Column(Float, nullable=False)  # Per $1,000 of assessed value
    levy_amount = Column(Float, nullable=False)  # Total levy amount requested
    assessed_value_basis = Column(Float, nullable=False)  # Total assessed value used for calculation
    is_final = Column(Boolean, default=False)
    notes = Column(Text)
    
    # Relationships
    tax_district = relationship('TaxDistrict', back_populates='levy_rates')
    
    # Ensure one final rate per tax_district_id and year
    __table_args__ = (
        UniqueConstraint('tax_district_id', 'year', 'is_final', name='uix_district_year_final',
                       sqlite_on_conflict='REPLACE'),
        CheckConstraint('levy_rate >= 0', name='check_levy_rate_positive'),
        CheckConstraint('levy_amount >= 0', name='check_levy_amount_positive'),
        CheckConstraint('assessed_value_basis > 0', name='check_assessed_value_positive'),
    )
    
    def __repr__(self):
        return f'<LevyRate {self.tax_district_id} Y:{self.year} R:{self.levy_rate}>'


class ImportLog(AuditMixin, db.Model):
    """
    Log of data imports for tracking and auditing.
    """
    __tablename__ = 'import_log'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', name='fk_import_log_user'), nullable=True, index=True)
    filename = Column(String(256), nullable=False)
    import_type = Column(SQLEnum(ImportType), nullable=True)  # Make nullable for backward compatibility
    record_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    status = Column(String(32), default='PENDING')
    error_details = Column(Text)
    processing_time = Column(Float)  # Time in seconds
    year = Column(Integer, nullable=False, index=True)
    import_metadata = Column(JSON)  # Renamed from metadata (reserved name)
    
    # Relationship
    user = relationship('User', foreign_keys=[user_id], backref=backref('imports', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ImportLog {self.filename} {self.status}>'


class ExportLog(AuditMixin, db.Model):
    """
    Log of data exports for tracking and auditing.
    """
    __tablename__ = 'export_log'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    filename = Column(String(256), nullable=False)
    export_type = Column(SQLEnum(ExportType), nullable=False)
    record_count = Column(Integer, default=0)
    status = Column(String(32), default='PENDING')
    error_details = Column(Text)
    processing_time = Column(Float)  # Time in seconds
    year = Column(Integer, nullable=False, index=True)
    export_metadata = Column(JSON)  # Renamed from metadata (reserved name)
    
    # Relationship
    user = relationship('User', foreign_keys=[user_id], backref=backref('exports', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ExportLog {self.filename} {self.status}>'


class AuditLog(db.Model):
    """
    Audit trail for tracking all significant data changes.
    """
    __tablename__ = 'audit_log'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    table_name = Column(String(64), nullable=False, index=True)
    record_id = Column(Integer, nullable=False)
    action = Column(String(16), nullable=False)  # CREATE, UPDATE, DELETE
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(256))
    
    # Relationship
    user = relationship('User', foreign_keys=[user_id], backref=backref('audit_logs', lazy='dynamic'))
    
    def __repr__(self):
        return f'<AuditLog {self.table_name} {self.action} {self.record_id}>'


class LevyScenario(AuditMixin, YearMixin, db.Model):
    """
    Levy calculation scenarios for analysis and forecasting.
    """
    __tablename__ = 'levy_scenario'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    tax_district_id = Column(Integer, ForeignKey('tax_district.id'), nullable=False)
    base_year = Column(Integer, nullable=False)
    target_year = Column(Integer, nullable=False)
    levy_amount = Column(Float)
    assessed_value_change = Column(Float, default=0.0)  # Percentage change 
    new_construction_value = Column(Float, default=0.0)
    annexation_value = Column(Float, default=0.0)
    is_public = Column(Boolean, default=False)
    result_levy_rate = Column(Float)
    result_levy_amount = Column(Float)
    status = Column(String(32), default='DRAFT')
    
    # Relationships
    user = relationship('User', foreign_keys=[user_id], backref=backref('levy_scenarios', lazy='dynamic'))
    tax_district = relationship('TaxDistrict')
    
    def __repr__(self):
        return f'<LevyScenario {self.name} {self.tax_district_id}>'


class Forecast(AuditMixin, db.Model):
    """
    Model forecasts for future levy rates and amounts.
    """
    __tablename__ = 'forecast'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    tax_district_id = Column(Integer, ForeignKey('tax_district.id'), nullable=True)
    tax_code_id = Column(Integer, ForeignKey('tax_code.id'), nullable=True)
    base_year = Column(Integer, nullable=False)
    forecast_years = Column(Integer, default=5)  # Number of years to forecast
    model_type = Column(String(64), nullable=False)  # LINEAR, EXPONENTIAL, ARIMA, ENSEMBLE
    model_parameters = Column(JSON)
    forecast_data = Column(JSON)  # Serialized forecast results
    accuracy_metrics = Column(JSON)  # RMSE, MAE, etc.
    confidence_intervals = Column(JSON)  # Upper and lower bounds
    is_public = Column(Boolean, default=False)
    
    # Relationships
    user = relationship('User', foreign_keys=[user_id], backref=backref('forecasts', lazy='dynamic'))
    tax_district = relationship('TaxDistrict')
    tax_code = relationship('TaxCode')
    
    # Ensure either tax_district_id or tax_code_id is set, but not both
    __table_args__ = (
        CheckConstraint('(tax_district_id IS NULL AND tax_code_id IS NOT NULL) OR '
                       '(tax_district_id IS NOT NULL AND tax_code_id IS NULL)',
                       name='check_forecast_target'),
    )
    
    def __repr__(self):
        return f'<Forecast {self.name} {self.model_type}>'


class ComplianceIssue(AuditMixin, YearMixin, db.Model):
    """
    Tracking of statutory compliance issues with levy calculations.
    """
    __tablename__ = 'compliance_issue'
    
    id = Column(Integer, primary_key=True)
    tax_district_id = Column(Integer, ForeignKey('tax_district.id'), nullable=False)
    issue_type = Column(String(64), nullable=False)  # OVER_LIMIT, INCORRECT_FORMULA, etc.
    severity = Column(String(32), nullable=False)  # HIGH, MEDIUM, LOW
    description = Column(Text, nullable=False)
    impact_amount = Column(Float)  # Financial impact of the issue
    resolution_status = Column(String(32), default='OPEN')
    resolution_notes = Column(Text)
    resolved_at = Column(DateTime)
    resolved_by_id = Column(Integer, ForeignKey('user.id'))
    
    # Relationships
    tax_district = relationship('TaxDistrict')
    resolved_by = relationship('User', foreign_keys=[resolved_by_id])
    
    def __repr__(self):
        return f'<ComplianceIssue {self.tax_district_id} {self.issue_type} {self.resolution_status}>'


class GlossaryTerm(AuditMixin, db.Model):
    """
    Glossary of tax-related terms and definitions.
    """
    __tablename__ = 'glossary_term'
    
    id = Column(Integer, primary_key=True)
    term = Column(String(128), nullable=False, unique=True)
    definition = Column(Text, nullable=False)
    example = Column(Text)
    related_terms = Column(Text)  # Comma-separated list of related terms
    category = Column(String(64))
    source = Column(String(256))
    
    def __repr__(self):
        return f'<GlossaryTerm {self.term}>'


class ScheduledReport(AuditMixin, db.Model):
    """
    Configuration for scheduled report generation.
    """
    __tablename__ = 'scheduled_report'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    report_type = Column(String(64), nullable=False)
    parameters = Column(JSON, nullable=False)
    schedule_type = Column(String(32), nullable=False)  # DAILY, WEEKLY, MONTHLY, QUARTERLY, YEARLY
    schedule_config = Column(JSON, nullable=False)  # Specific scheduling parameters
    recipients = Column(Text)  # Comma-separated email addresses
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    
    # Relationships
    user = relationship('User', foreign_keys=[user_id], backref=backref('scheduled_reports', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ScheduledReport {self.name} {self.report_type} {self.schedule_type}>'


class ReportTemplate(AuditMixin, db.Model):
    """
    Templates for custom report generation.
    """
    __tablename__ = 'report_template'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    template_type = Column(String(64), nullable=False)
    content = Column(Text, nullable=False)  # HTML, Markdown, or template format
    parameters = Column(JSON)  # Required parameters
    is_public = Column(Boolean, default=False)
    
    # Relationships
    user = relationship('User', foreign_keys=[user_id], backref=backref('report_templates', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ReportTemplate {self.name} {self.template_type}>'


class AnalysisResult(AuditMixin, db.Model):
    """
    Stored results of complex analyses for reuse and sharing.
    """
    __tablename__ = 'analysis_result'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    analysis_type = Column(String(64), nullable=False)
    parameters = Column(JSON, nullable=False)
    results = Column(JSON, nullable=False)
    visualization_data = Column(JSON)
    start_year = Column(Integer, nullable=False)
    end_year = Column(Integer, nullable=False)
    is_public = Column(Boolean, default=False)
    
    # Relationships
    user = relationship('User', foreign_keys=[user_id], backref=backref('analyses', lazy='dynamic'))
    
    def __repr__(self):
        return f'<AnalysisResult {self.name} {self.analysis_type}>'


class SystemSetting(db.Model):
    """
    System-wide configuration settings.
    """
    __tablename__ = 'system_setting'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(128), nullable=False, unique=True)
    value = Column(Text)
    value_type = Column(String(32), default='string')  # string, int, float, boolean, json
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_id = Column(Integer, ForeignKey('user.id'))
    
    # Relationships
    updated_by = relationship('User', foreign_keys=[updated_by_id])
    
    def __repr__(self):
        return f'<SystemSetting {self.key}>'
    
    @property
    def typed_value(self):
        """Return the value converted to its proper type."""
        if self.value is None:
            return None
        
        if self.value_type == 'int':
            return int(self.value)
        elif self.value_type == 'float':
            return float(self.value)
        elif self.value_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes')
        elif self.value_type == 'json':
            import json
            return json.loads(self.value)
        else:  # Default to string
            return self.value


class AIAnalysisRequest(AuditMixin, db.Model):
    """
    Requests for AI-based analysis and their results.
    """
    __tablename__ = 'ai_analysis_request'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    request_type = Column(String(64), nullable=False)
    prompt = Column(Text, nullable=False)
    parameters = Column(JSON)
    response = Column(Text)
    ai_response_metadata = Column(JSON)  # Renamed from response_metadata (reserved name)
    processing_time = Column(Float)  # Time in seconds
    status = Column(String(32), default='PENDING')
    error_details = Column(Text)
    
    # Relationships
    user = relationship('User', foreign_keys=[user_id], backref=backref('ai_requests', lazy='dynamic'))
    
    def __repr__(self):
        return f'<AIAnalysisRequest {self.id} {self.request_type} {self.status}>'


class APICallLog(db.Model):
    """
    Model for logging historical API calls for monitoring and analytics.
    Stores permanent record of API calls for trend analysis and auditing.
    """
    __tablename__ = 'api_call_log'
    
    id = Column(Integer, primary_key=True)
    service = Column(String(64), nullable=False, index=True)  # e.g. "anthropic", "openai", etc.
    endpoint = Column(String(128), nullable=False, index=True)
    method = Column(String(16), nullable=False)  # HTTP method
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    duration_ms = Column(Float, nullable=True)
    status_code = Column(Integer, nullable=True)
    success = Column(Boolean, default=False, nullable=False, index=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    params = Column(JSON, nullable=True)  # Redacted parameters
    response_summary = Column(JSON, nullable=True)  # Summarized response
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True, index=True)
    
    # Relationships
    user = relationship('User', foreign_keys=[user_id], backref=backref('api_calls', lazy='dynamic'))
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_api_call_service_success', 'service', 'success'),
        Index('idx_api_call_timestamp_service', 'timestamp', 'service'),
    )
    
    def __repr__(self):
        return f'<APICallLog {self.id} {self.service}.{self.endpoint} success={self.success}>'


class LevyAuditRecord(db.Model):
    """
    Model for storing levy audit records from the Levy Audit AI Agent.
    
    This table tracks all interactions with the Levy Audit Agent,
    including compliance audits, recommendations, and calculation verifications.
    """
    __tablename__ = 'levy_audit_record'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    tax_district_id = db.Column(db.Integer, db.ForeignKey('tax_district.id'), nullable=True, index=True)
    tax_code_id = db.Column(db.Integer, db.ForeignKey('tax_code.id'), nullable=True, index=True)
    year = db.Column(db.Integer, nullable=True, index=True)
    audit_type = db.Column(db.String(32), nullable=False, index=True)  # COMPLIANCE, RECOMMENDATION, VERIFICATION, QUERY
    full_audit = db.Column(db.Boolean, default=False)
    compliance_score = db.Column(db.Float, nullable=True)
    query = db.Column(db.Text, nullable=True)
    results = db.Column(db.JSON, nullable=True)
    status = db.Column(db.String(32), default='PENDING', nullable=False)  # PENDING, COMPLETED, FAILED
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    error_details = db.Column(db.Text, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('levy_audit_records', lazy='dynamic'))
    tax_district = db.relationship('TaxDistrict', backref=db.backref('levy_audit_records', lazy='dynamic'))
    tax_code = db.relationship('TaxCode', backref=db.backref('levy_audit_records', lazy='dynamic'))
    
    # Add indexes for common queries
    __table_args__ = (
        db.Index('idx_audit_district_year', 'tax_district_id', 'year'),
        db.Index('idx_audit_type_status', 'audit_type', 'status'),
        db.Index('idx_audit_user_district', 'user_id', 'tax_district_id'),
    )
    
    def __repr__(self):
        return f'<LevyAuditRecord {self.id} type={self.audit_type} status={self.status}>'


class UserActionLog(db.Model):
    """
    Model for tracking detailed user interactions with the system.
    
    This table provides comprehensive logging of user activities including:
    - Page views and navigation
    - Feature usage
    - Form submissions
    - Data exports
    - System settings changes
    
    It complements the existing AuditLog table which focuses on data changes,
    while this focuses on user behaviors and interactions.
    """
    __tablename__ = 'user_action_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    action_type = db.Column(db.String(64), nullable=False, index=True)  # VIEW, SEARCH, EXPORT, CALCULATE, etc.
    module = db.Column(db.String(64), nullable=False, index=True)  # levy_calculator, reports, admin, etc.
    submodule = db.Column(db.String(64), nullable=True)  # Specific feature within module
    action_details = db.Column(db.JSON, nullable=True)  # Details specific to the action
    entity_type = db.Column(db.String(64), nullable=True)  # Type of entity being acted upon (tax_district, property, etc.)
    entity_id = db.Column(db.Integer, nullable=True)  # ID of the entity being acted upon
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(256), nullable=True)
    session_id = db.Column(db.String(128), nullable=True, index=True)
    success = db.Column(db.Boolean, default=True, nullable=False, index=True)  # Did the action succeed?
    error_message = db.Column(db.Text, nullable=True)  # Error message if action failed
    duration_ms = db.Column(db.Float, nullable=True)  # How long the action took
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('user_actions', lazy='dynamic'))
    
    __table_args__ = (
        db.Index('idx_user_action_type_module', 'action_type', 'module'),
        db.Index('idx_user_timestamp_action', 'timestamp', 'action_type'),
        db.Index('idx_user_entity_action', 'entity_type', 'entity_id', 'action_type'),
    )
    
    def __repr__(self):
        return f'<UserActionLog {self.id} {self.action_type} {self.module}>'





class LevyOverrideLog(db.Model):
    """
    Model for tracking levy calculation overrides.
    
    This table specifically tracks instances where users override
    calculated levy values, providing an audit trail for compliance
    and training purposes.
    """
    __tablename__ = 'levy_override_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    tax_district_id = db.Column(db.Integer, db.ForeignKey('tax_district.id'), nullable=True, index=True)
    tax_code_id = db.Column(db.Integer, db.ForeignKey('tax_code.id'), nullable=True, index=True) 
    year = db.Column(db.Integer, nullable=False, index=True)
    
    # Fields that can be overridden
    field_name = db.Column(db.String(64), nullable=False)  # The field that was overridden
    original_value = db.Column(db.Float, nullable=False)  # The calculated value
    override_value = db.Column(db.Float, nullable=False)  # The user-provided value
    percent_change = db.Column(db.Float, nullable=True)  # Percentage difference
    
    # Approval information
    justification = db.Column(db.Text, nullable=True)  # User's reason for override
    requires_approval = db.Column(db.Boolean, default=False)  # Whether override requires approval
    approved = db.Column(db.Boolean, nullable=True)  # NULL=pending, True=approved, False=rejected
    approver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approval_timestamp = db.Column(db.DateTime, nullable=True)
    approval_notes = db.Column(db.Text, nullable=True)
    
    # Related data
    calculation_params = db.Column(db.JSON, nullable=True)  # Parameters used in original calculation
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('levy_overrides', lazy='dynamic'))
    approver = db.relationship('User', foreign_keys=[approver_id], backref=db.backref('approved_overrides', lazy='dynamic'))
    tax_district = db.relationship('TaxDistrict', backref=db.backref('levy_overrides', lazy='dynamic'))
    tax_code = db.relationship('TaxCode', backref=db.backref('levy_overrides', lazy='dynamic'))
    
    __table_args__ = (
        db.Index('idx_override_district_year', 'tax_district_id', 'year'),
        db.Index('idx_override_approval_status', 'requires_approval', 'approved'),
        db.Index('idx_override_user_field', 'user_id', 'field_name'),
    )
    
    def __repr__(self):
        return f'<LevyOverrideLog {self.id} field={self.field_name} approved={self.approved}>'


# Data Quality Models

class DataQualityScore(AuditMixin, db.Model):
    """
    Model for storing data quality metrics over time.
    
    This table tracks overall data quality scores as well as specific
    dimension scores (completeness, accuracy, consistency) to monitor
    data quality trends over time.
    """
    __tablename__ = 'data_quality_score'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    overall_score = db.Column(db.Float, nullable=False)
    completeness_score = db.Column(db.Float, nullable=False)
    accuracy_score = db.Column(db.Float, nullable=False)
    consistency_score = db.Column(db.Float, nullable=False)
    timeliness_score = db.Column(db.Float, nullable=True)
    
    # Detailed metrics
    completeness_fields_missing = db.Column(db.Integer, nullable=True)
    accuracy_errors = db.Column(db.Integer, nullable=True)
    consistency_issues = db.Column(db.Integer, nullable=True)
    
    # Report period
    year = db.Column(db.Integer, nullable=True, index=True)
    month = db.Column(db.Integer, nullable=True)
    day = db.Column(db.Integer, nullable=True)
    
    __table_args__ = (
        db.Index('idx_quality_date', 'year', 'month', 'day'),
    )
    
    def __repr__(self):
        return f'<DataQualityScore {self.id} overall={self.overall_score:.1f}%>'


class ValidationRule(AuditMixin, db.Model):
    """
    Model for storing validation rules used in data quality assessment.
    
    These rules define the expected data quality standards and are used
    to validate incoming data and assess overall data quality.
    """
    __tablename__ = 'validation_rule'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    entity_type = db.Column(db.String(64), nullable=False, index=True)  # Property, TaxDistrict, etc.
    rule_type = db.Column(db.String(64), nullable=False, index=True)  # Format, Range, Uniqueness, Relationship, etc.
    severity = db.Column(db.String(32), nullable=False, default='WARNING')  # ERROR, WARNING, INFO
    
    # Rule definition (stored as JSON for flexibility)
    rule_definition = db.Column(db.JSON, nullable=False)
    
    # Rule performance metrics
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    pass_rate = db.Column(db.Float, nullable=True)
    last_run = db.Column(db.DateTime, nullable=True)
    run_count = db.Column(db.Integer, default=0, nullable=False)
    fail_count = db.Column(db.Integer, default=0, nullable=False)
    
    __table_args__ = (
        db.Index('idx_rule_type_entity', 'rule_type', 'entity_type'),
    )
    
    def __repr__(self):
        return f'<ValidationRule {self.name} type={self.rule_type}>'


class ValidationResult(AuditMixin, db.Model):
    """
    Model for storing results of validation rule executions.
    
    This table tracks each validation rule execution result, providing
    a detailed history of data quality validations and their outcomes.
    """
    __tablename__ = 'validation_result'
    
    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey('validation_rule.id'), nullable=False, index=True)
    entity_id = db.Column(db.Integer, nullable=False, index=True)
    entity_type = db.Column(db.String(64), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    passed = db.Column(db.Boolean, nullable=False, index=True)
    error_message = db.Column(db.Text, nullable=True)
    error_details = db.Column(db.JSON, nullable=True)
    
    # Context information
    context = db.Column(db.JSON, nullable=True)  # Import batch ID, user ID, etc.
    
    rule = db.relationship('ValidationRule', backref='results')
    
    __table_args__ = (
        db.Index('idx_validation_entity_rule', 'entity_type', 'entity_id', 'rule_id'),
        db.Index('idx_validation_timestamp_passed', 'timestamp', 'passed'),
    )
    
    def __repr__(self):
        return f'<ValidationResult rule_id={self.rule_id} passed={self.passed}>'


class ErrorPattern(AuditMixin, db.Model):
    """
    Model for storing detected error patterns from validation results.
    
    This table stores automatically identified patterns of validation errors,
    allowing for more efficient data quality improvement efforts by targeting
    systemic issues.
    """
    __tablename__ = 'error_pattern'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    entity_type = db.Column(db.String(64), nullable=False, index=True)
    pattern_type = db.Column(db.String(64), nullable=False, index=True)  # Format, Value, Missing, etc.
    
    # Pattern metrics
    frequency = db.Column(db.Integer, default=0, nullable=False)
    impact = db.Column(db.String(32), nullable=False)  # HIGH, MEDIUM, LOW
    impact_score = db.Column(db.Float, nullable=True)  # Numeric impact score
    
    # Related entities
    affected_entities = db.Column(db.Integer, default=0, nullable=False)  # Count of affected entities
    affected_fields = db.Column(db.JSON, nullable=True)  # List of affected fields
    
    # AI-generated recommendation
    recommendation = db.Column(db.Text, nullable=True)
    auto_fixable = db.Column(db.Boolean, default=False, nullable=False)
    fix_script = db.Column(db.Text, nullable=True)
    
    # Status tracking
    status = db.Column(db.String(32), default='ACTIVE', nullable=False)  # ACTIVE, FIXED, IGNORED
    resolution_notes = db.Column(db.Text, nullable=True)
    resolved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # Additional tracking
    detected_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    last_occurrence = db.Column(db.DateTime, nullable=True, index=True)
    
    __table_args__ = (
        db.Index('idx_pattern_status_impact', 'status', 'impact'),
        db.Index('idx_pattern_entity_type', 'entity_type', 'pattern_type'),
    )
    
    def __repr__(self):
        return f'<ErrorPattern {self.name} impact={self.impact} status={self.status}>'


class DataQualityActivity(AuditMixin, db.Model):
    """
    Model for tracking data quality improvement activities.
    
    This table logs all actions taken to improve data quality, including
    rule changes, data corrections, and system enhancements.
    """
    __tablename__ = 'data_quality_activity'
    
    id = db.Column(db.Integer, primary_key=True)
    activity_type = db.Column(db.String(64), nullable=False, index=True)  # RULE_ADDED, DATA_FIXED, IMPORT, etc.
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Activity details
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Related entity information
    entity_type = db.Column(db.String(64), nullable=True, index=True)  # Rule, ErrorPattern, etc.
    entity_id = db.Column(db.Integer, nullable=True, index=True)
    
    # Impact metrics
    records_affected = db.Column(db.Integer, nullable=True)
    impact_summary = db.Column(db.JSON, nullable=True)
    
    # Additional metadata
    icon = db.Column(db.String(32), nullable=True, default='gear')
    icon_class = db.Column(db.String(32), nullable=True, default='primary')
    
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('data_quality_activities', lazy='dynamic'))
    
    __table_args__ = (
        db.Index('idx_activity_timestamp', 'timestamp'),
        db.Index('idx_activity_user_type', 'user_id', 'activity_type'),
    )
    
    def __repr__(self):
        return f'<DataQualityActivity {self.activity_type} {self.title}>'