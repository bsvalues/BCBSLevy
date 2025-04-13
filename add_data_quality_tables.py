"""
Migration script to add the Data Quality tables for data quality monitoring.

This script adds tables to store data quality metrics, validation rules,
validation results, error patterns, and data quality activities.
"""

from datetime import datetime
import os
import sys
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, ForeignKey, 
    Text, JSON, MetaData, Table, Index, create_engine, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# DB URL from environment or default to SQLite
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///levy_system.db')

# Create engine and metadata
engine = create_engine(DATABASE_URL)
Base = declarative_base()
metadata = MetaData()

def run_migration():
    """
    Create the Data Quality tables if they don't exist.
    """
    # Define tables
    data_quality_score = Table(
        'data_quality_score',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
        Column('created_by_id', Integer, ForeignKey('user.id'), nullable=True),
        Column('updated_by_id', Integer, ForeignKey('user.id'), nullable=True),
        Column('timestamp', DateTime, default=datetime.utcnow, nullable=False, index=True),
        Column('overall_score', Float, nullable=False),
        Column('completeness_score', Float, nullable=False),
        Column('accuracy_score', Float, nullable=False),
        Column('consistency_score', Float, nullable=False),
        Column('timeliness_score', Float, nullable=True),
        Column('completeness_fields_missing', Integer, nullable=True),
        Column('accuracy_errors', Integer, nullable=True),
        Column('consistency_issues', Integer, nullable=True),
        Column('year', Integer, nullable=True, index=True),
        Column('month', Integer, nullable=True),
        Column('day', Integer, nullable=True),
        Index('idx_quality_date', 'year', 'month', 'day')
    )
    
    validation_rule = Table(
        'validation_rule',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
        Column('created_by_id', Integer, ForeignKey('user.id'), nullable=True),
        Column('updated_by_id', Integer, ForeignKey('user.id'), nullable=True),
        Column('name', String(128), nullable=False),
        Column('description', Text, nullable=True),
        Column('entity_type', String(64), nullable=False, index=True),
        Column('rule_type', String(64), nullable=False, index=True),
        Column('severity', String(32), nullable=False, default='WARNING'),
        Column('rule_definition', JSON, nullable=False),
        Column('enabled', Boolean, default=True, nullable=False),
        Column('pass_rate', Float, nullable=True),
        Column('last_run', DateTime, nullable=True),
        Column('run_count', Integer, default=0, nullable=False),
        Column('fail_count', Integer, default=0, nullable=False),
        Index('idx_rule_type_entity', 'rule_type', 'entity_type')
    )
    
    validation_result = Table(
        'validation_result',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
        Column('created_by_id', Integer, ForeignKey('user.id'), nullable=True),
        Column('updated_by_id', Integer, ForeignKey('user.id'), nullable=True),
        Column('rule_id', Integer, ForeignKey('validation_rule.id'), nullable=False, index=True),
        Column('entity_id', Integer, nullable=False, index=True),
        Column('entity_type', String(64), nullable=False, index=True),
        Column('timestamp', DateTime, default=datetime.utcnow, nullable=False, index=True),
        Column('passed', Boolean, nullable=False, index=True),
        Column('error_message', Text, nullable=True),
        Column('error_details', JSON, nullable=True),
        Column('context', JSON, nullable=True),
        Index('idx_validation_entity_rule', 'entity_type', 'entity_id', 'rule_id'),
        Index('idx_validation_timestamp_passed', 'timestamp', 'passed')
    )
    
    error_pattern = Table(
        'error_pattern',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
        Column('created_by_id', Integer, ForeignKey('user.id'), nullable=True),
        Column('updated_by_id', Integer, ForeignKey('user.id'), nullable=True),
        Column('name', String(128), nullable=False),
        Column('description', Text, nullable=True),
        Column('entity_type', String(64), nullable=False, index=True),
        Column('pattern_type', String(64), nullable=False, index=True),
        Column('frequency', Integer, default=0, nullable=False),
        Column('impact', String(32), nullable=False),
        Column('impact_score', Float, nullable=True),
        Column('affected_entities', Integer, default=0, nullable=False),
        Column('affected_fields', JSON, nullable=True),
        Column('recommendation', Text, nullable=True),
        Column('auto_fixable', Boolean, default=False, nullable=False),
        Column('fix_script', Text, nullable=True),
        Column('status', String(32), default='ACTIVE', nullable=False),
        Column('resolution_notes', Text, nullable=True),
        Column('resolved_by_id', Integer, ForeignKey('user.id'), nullable=True),
        Column('resolved_at', DateTime, nullable=True),
        Column('detected_at', DateTime, default=datetime.utcnow, nullable=False, index=True),
        Column('last_occurrence', DateTime, nullable=True, index=True),
        Index('idx_pattern_status_impact', 'status', 'impact'),
        Index('idx_pattern_entity_type', 'entity_type', 'pattern_type')
    )
    
    data_quality_activity = Table(
        'data_quality_activity',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
        Column('created_by_id', Integer, ForeignKey('user.id'), nullable=True),
        Column('updated_by_id', Integer, ForeignKey('user.id'), nullable=True),
        Column('activity_type', String(64), nullable=False, index=True),
        Column('title', String(128), nullable=False),
        Column('description', Text, nullable=True),
        Column('user_id', Integer, ForeignKey('user.id'), nullable=False, index=True),
        Column('timestamp', DateTime, default=datetime.utcnow, nullable=False, index=True),
        Column('entity_type', String(64), nullable=True, index=True),
        Column('entity_id', Integer, nullable=True, index=True),
        Column('records_affected', Integer, nullable=True),
        Column('impact_summary', JSON, nullable=True),
        Column('icon', String(32), nullable=True, default='gear'),
        Column('icon_class', String(32), nullable=True, default='primary'),
        Index('idx_activity_timestamp', 'timestamp'),
        Index('idx_activity_user_type', 'user_id', 'activity_type')
    )
    
    # Create tables if they don't exist
    try:
        tables_to_create = [
            data_quality_score,
            validation_rule,
            validation_result,
            error_pattern,
            data_quality_activity
        ]
        
        conn = engine.connect()
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        for table in tables_to_create:
            if table.name not in existing_tables:
                table.create(engine)
                print(f"Created table: {table.name}")
            else:
                print(f"Table already exists: {table.name}")
        
        conn.close()
        print("Data Quality tables migration completed successfully")
        return True
    
    except Exception as e:
        print(f"Error creating Data Quality tables: {str(e)}")
        return False


if __name__ == "__main__":
    from sqlalchemy import inspect
    result = run_migration()
    sys.exit(0 if result else 1)