"""
Database models for the TerraLevy application.

This module defines all database models used in the TerraLevy application.
"""

from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


# Association tables for many-to-many relationships
tax_district_property = db.Table(
    'tax_district_property',
    db.Column('tax_district_id', db.Integer, db.ForeignKey('tax_district.id'), primary_key=True),
    db.Column('property_id', db.Integer, db.ForeignKey('property.id'), primary_key=True)
)


class UserRole(db.Model):
    """Model for user roles and permissions."""
    __tablename__ = 'user_role'
    
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(32), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)
    permissions = db.Column(db.JSON)  # JSON array of permission strings
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserRole {self.role_name}>'


class APICallLog(db.Model):
    """Model for tracking API calls made to external services.
    
    This model must match the table created by add_api_call_log_table.py migration.
    """
    __tablename__ = 'api_call_log'
    
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(64), nullable=False, index=True)  # e.g. "anthropic", "openai", etc.
    endpoint = db.Column(db.String(128), nullable=False, index=True)
    method = db.Column(db.String(16), nullable=False)  # HTTP method
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    duration_ms = db.Column(db.Float, nullable=True)
    status_code = db.Column(db.Integer, nullable=True)
    success = db.Column(db.Boolean, default=False, nullable=False, index=True)
    error_message = db.Column(db.Text, nullable=True)
    retry_count = db.Column(db.Integer, default=0, nullable=False)
    params = db.Column(db.JSON, nullable=True)  # Redacted parameters
    response_summary = db.Column(db.JSON, nullable=True)  # Summarized response
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    
    # Relationships
    user = db.relationship('User', backref='api_calls')
    
    __table_args__ = (
        db.Index('idx_api_call_service_success', 'service', 'success'),
        db.Index('idx_api_call_timestamp_service', 'timestamp', 'service'),
    )
    
    def __repr__(self):
        return f'<APICallLog {self.id}: {self.service} - {self.endpoint}>'


class AuditLog(db.Model):
    """General audit log for system-wide activities."""
    __tablename__ = 'audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    event_type = db.Column(db.String(64), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    resource_type = db.Column(db.String(64), nullable=True, index=True)
    resource_id = db.Column(db.Integer, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)  # Support for IPv6
    details = db.Column(db.JSON, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='audit_logs')
    
    def __repr__(self):
        return f'<AuditLog {self.id}: {self.event_type}>'


class LevyAuditRecord(db.Model):
    """Model for storing levy audit results from the Levy Audit AI Agent."""
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
    user = db.relationship('User', backref='levy_audits')
    tax_district = db.relationship('TaxDistrict', backref='levy_audits')
    tax_code = db.relationship('TaxCode', backref='levy_audits')
    
    __table_args__ = (
        db.Index('idx_audit_district_year', 'tax_district_id', 'year'),
        db.Index('idx_audit_type_status', 'audit_type', 'status'),
        db.Index('idx_audit_user_district', 'user_id', 'tax_district_id'),
    )
    
    def __repr__(self):
        return f'<LevyAuditRecord {self.id}: {self.audit_type} for {self.tax_district_id or self.tax_code_id}>'


class UserActionLog(db.Model):
    """Model for tracking user actions in the system."""
    __tablename__ = 'user_action_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    action_type = db.Column(db.String(32), nullable=False, index=True)
    action_detail = db.Column(db.Text)
    ip_address = db.Column(db.String(45))  # IPv6 support
    user_agent = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    resource_type = db.Column(db.String(32), index=True)  # e.g., district, property, tax_code
    resource_id = db.Column(db.Integer)
    success = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<UserActionLog {self.action_type} by User {self.user_id}>'


class User(UserMixin, db.Model):
    """User model for authentication and tracking actions."""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationships
    imports = db.relationship('ImportLog', foreign_keys='ImportLog.user_id', backref='user', lazy='dynamic')
    exports = db.relationship('ExportLog', foreign_keys='ExportLog.user_id', backref='user', lazy='dynamic')
    action_logs = db.relationship('UserActionLog', foreign_keys='UserActionLog.user_id', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Set password hash for user."""
        self.password_hash = generate_password_hash(password)
        self.updated_at = datetime.utcnow()
    
    def check_password(self, password):
        """Check if password matches hash."""
        return check_password_hash(self.password_hash, password)


class TaxDistrict(db.Model):
    """Model for tax districts (taxing authorities)."""
    __tablename__ = 'tax_district'
    
    id = db.Column(db.Integer, primary_key=True)
    district_name = db.Column(db.String(128), nullable=True, index=True)
    district_code = db.Column(db.String(20), nullable=True, index=True)
    tax_district_id = db.Column(db.String(20), nullable=True, index=True)  # External ID for the district
    description = db.Column(db.Text)
    district_type = db.Column(db.String(32), index=True)  # city, county, school, special
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    county = db.Column(db.String(64), index=True)
    state = db.Column(db.String(20), index=True)
    is_active = db.Column(db.Boolean, default=True)
    contact_name = db.Column(db.String(128), nullable=True)
    contact_email = db.Column(db.String(128), nullable=True)
    contact_phone = db.Column(db.String(20), nullable=True)
    levy_code = db.Column(db.String(20), nullable=True, index=True)
    linked_levy_code = db.Column(db.String(20), nullable=True, index=True)
    statutory_limit = db.Column(db.Float, nullable=True)
    year = db.Column(db.Integer, nullable=True)
    
    # Relationships
    tax_codes = db.relationship('TaxCode', foreign_keys='TaxCode.tax_district_id', backref='tax_district', lazy='dynamic')
    properties = db.relationship('Property', secondary=tax_district_property, back_populates='tax_districts')
    
    def __repr__(self):
        return f'<TaxDistrict {self.district_name}>'


class TaxCode(db.Model):
    """Model for tax codes, which group properties together for levy purposes."""
    __tablename__ = 'tax_code'
    
    id = db.Column(db.Integer, primary_key=True)
    tax_code = db.Column(db.String(20), nullable=False, index=True, unique=True)  # Renamed from 'code' to 'tax_code'
    description = db.Column(db.Text)
    tax_district_id = db.Column(db.Integer, db.ForeignKey('tax_district.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    total_assessed_value = db.Column(db.Float, default=0.0)
    levy_rate = db.Column(db.Float, default=0.0)
    levy_amount = db.Column(db.Float, default=0.0)
    total_levy_amount = db.Column(db.Float, default=0.0)
    effective_tax_rate = db.Column(db.Float, default=0.0)
    previous_year_rate = db.Column(db.Float, nullable=True)
    year = db.Column(db.Integer, nullable=True)
    
    # Relationships
    properties = db.relationship('Property', foreign_keys='Property.tax_code_id', backref='tax_code_ref', lazy='dynamic')
    historical_rates = db.relationship('TaxCodeHistoricalRate', foreign_keys='TaxCodeHistoricalRate.tax_code_id', backref='tax_code', lazy='dynamic')
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref='created_tax_codes')
    updated_by = db.relationship('User', foreign_keys=[updated_by_id], backref='updated_tax_codes')
    
    def __repr__(self):
        return f'<TaxCode {self.tax_code}>'


class LevyScenario(db.Model):
    """Model for levy calculation scenarios."""
    __tablename__ = 'levy_scenario'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    tax_district_id = db.Column(db.Integer, db.ForeignKey('tax_district.id'), nullable=False, index=True)
    base_year = db.Column(db.Integer, nullable=False)
    target_year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Calculation fields
    levy_amount = db.Column(db.Float, nullable=True)  # requested levy amount
    assessed_value_change = db.Column(db.Float, nullable=True)  # percentage change in assessed value
    new_construction_value = db.Column(db.Float, nullable=True)  # value of new construction
    annexation_value = db.Column(db.Float, nullable=True)  # value of annexed property
    result_levy_rate = db.Column(db.Float, nullable=True)  # calculated levy rate
    result_levy_amount = db.Column(db.Float, nullable=True)  # calculated total levy amount
    
    # Relationships
    tax_district = db.relationship('TaxDistrict', foreign_keys=[tax_district_id], backref='levy_scenarios')
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref='created_scenarios')
    updated_by = db.relationship('User', foreign_keys=[updated_by_id], backref='updated_scenarios')
    user = db.relationship('User', foreign_keys=[user_id], backref='owned_scenarios')
    
    def __repr__(self):
        return f'<LevyScenario {self.name} - District: {self.tax_district_id}>'


class LevyOverrideLog(db.Model):
    """Model for tracking levy rate overrides by users."""
    __tablename__ = 'levy_override_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    tax_district_id = db.Column(db.Integer, db.ForeignKey('tax_district.id'), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    original_levy_amount = db.Column(db.Float, nullable=False)
    new_levy_amount = db.Column(db.Float, nullable=False)
    original_rate = db.Column(db.Float, nullable=False)
    new_rate = db.Column(db.Float, nullable=False)
    override_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='levy_overrides')
    tax_district = db.relationship('TaxDistrict', foreign_keys=[tax_district_id], backref='levy_overrides')
    
    def __repr__(self):
        return f'<LevyOverrideLog {self.id}: {self.tax_district_id} - {self.year}>'


class LevyRate(db.Model):
    """Model for levy rates and calculations."""
    __tablename__ = 'levy_rate'
    
    id = db.Column(db.Integer, primary_key=True)
    tax_district_id = db.Column(db.Integer, db.ForeignKey('tax_district.id'), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    levy_amount = db.Column(db.Float, nullable=False)
    assessed_value = db.Column(db.Float, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_projected = db.Column(db.Boolean, default=False)
    projection_basis = db.Column(db.String(50), nullable=True)  # historical, scenario, manual
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    tax_district = db.relationship('TaxDistrict', foreign_keys=[tax_district_id], backref='levy_rates')
    
    __table_args__ = (
        db.UniqueConstraint('tax_district_id', 'year', 'is_projected', name='uix_district_year_projection'),
    )
    
    def __repr__(self):
        return f'<LevyRate {self.tax_district_id} - {self.year}: {self.rate}>'


class TaxCodeHistoricalRate(db.Model):
    """Model for storing historical tax rates for each tax code over multiple years."""
    __tablename__ = 'tax_code_historical_rate'
    
    id = db.Column(db.Integer, primary_key=True)
    tax_code_id = db.Column(db.Integer, db.ForeignKey('tax_code.id'), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    levy_rate = db.Column(db.Float, nullable=False)
    levy_amount = db.Column(db.Float, nullable=True)
    total_assessed_value = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('tax_code_id', 'year', name='uix_tax_code_year'),
    )
    
    def __repr__(self):
        return f'<TaxCodeHistoricalRate {self.tax_code_id} - {self.year}: {self.levy_rate}>'


class PropertyType(db.Model):
    """Model for property types/classifications."""
    __tablename__ = 'property_type'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, index=True, unique=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # The Property model now stores property_type as a string field, not a foreign key
    
    def __repr__(self):
        return f'<PropertyType {self.code}: {self.name}>'


class Property(db.Model):
    """Model for individual properties with assessments."""
    __tablename__ = 'property'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.String(30), nullable=True, index=True)  # Formerly parcel_number
    address = db.Column(db.String(256))
    property_address = db.Column(db.String(256))
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(20), nullable=True)
    zip_code = db.Column(db.String(20), nullable=True)
    owner_name = db.Column(db.String(256))
    tax_code_id = db.Column(db.Integer, db.ForeignKey('tax_code.id'), nullable=True, index=True)
    tax_code = db.Column(db.String(20), nullable=True)
    property_type = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    assessed_value = db.Column(db.Float, default=0.0)
    market_value = db.Column(db.Float, default=0.0)
    land_value = db.Column(db.Float, default=0.0)
    building_value = db.Column(db.Float, default=0.0)
    tax_exempt = db.Column(db.Boolean, default=False)
    exemption_amount = db.Column(db.Float, default=0.0)
    taxable_value = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    year = db.Column(db.Integer, nullable=True)
    
    # Relationships
    tax_districts = db.relationship('TaxDistrict', secondary=tax_district_property, back_populates='properties')
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref='created_properties')
    updated_by = db.relationship('User', foreign_keys=[updated_by_id], backref='updated_properties')
    
    def __repr__(self):
        return f'<Property {self.property_id}>'


class ImportType(db.Model):
    """Model for types of data imports."""
    __tablename__ = 'import_type'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, index=True, unique=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    imports = db.relationship('ImportLog', foreign_keys='ImportLog.import_type_id', backref='type', lazy='dynamic')
    
    def __repr__(self):
        return f'<ImportType {self.code}: {self.name}>'


class ImportLog(db.Model):
    """Model for tracking data imports."""
    __tablename__ = 'import_log'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256))
    import_type = db.Column(db.String(32), index=True)  # property, district, code
    import_type_id = db.Column(db.Integer, db.ForeignKey('import_type.id'), nullable=True)
    status = db.Column(db.String(20), index=True)  # pending, processing, completed, error
    records_processed = db.Column(db.Integer, default=0)
    records_successful = db.Column(db.Integer, default=0)
    records_failed = db.Column(db.Integer, default=0)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    message = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    year = db.Column(db.Integer, default=datetime.utcnow().year, index=True)
    
    def __repr__(self):
        return f'<ImportLog {self.id} ({self.status})>'


class ExportType(db.Model):
    """Model for types of data exports."""
    __tablename__ = 'export_type'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, index=True, unique=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ExportType {self.code}: {self.name}>'


class ExportLog(db.Model):
    """Model for tracking data exports."""
    __tablename__ = 'export_log'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256))
    export_type = db.Column(db.String(32), index=True)  # report, data, levy
    status = db.Column(db.String(20), index=True)  # pending, processing, completed, error
    record_count = db.Column(db.Integer, default=0)
    rows_exported = db.Column(db.Integer, default=0)
    export_date = db.Column(db.DateTime, default=datetime.utcnow)
    processing_time = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    error_details = db.Column(db.Text, nullable=True)
    export_metadata = db.Column(db.JSON, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    year = db.Column(db.Integer, default=datetime.utcnow().year, index=True)
    
    def __repr__(self):
        return f'<ExportLog {self.id} ({self.status})>'