"""Add UserActionLog and LevyOverrideLog tables

Revision ID: 6e7f8g9h0i1j
Revises: 5d6e7f8g9h0i
Create Date: 2025-04-11 15:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6e7f8g9h0i1j'
down_revision = '5d6e7f8g9h0i'  # This should point to the previous migration
branch_labels = None
depends_on = None


def upgrade():
    """
    Add UserActionLog and LevyOverrideLog tables for user activity tracking.
    
    This adds two tables:
    1. UserActionLog - For tracking detailed user interactions with the system
    2. LevyOverrideLog - For tracking levy calculation overrides specifically
    """
    # Check if the tables already exist before creating them
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Create UserActionLog table if it doesn't exist
    if 'user_action_log' not in inspector.get_table_names():
        # Check if the user table exists before creating a foreign key to it
        has_user_table = 'user' in inspector.get_table_names()
        
        op.create_table(
            'user_action_log',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('timestamp', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
            sa.Column('action_type', sa.String(64), nullable=False),  # VIEW, SEARCH, EXPORT, CALCULATE, etc.
            sa.Column('module', sa.String(64), nullable=False),  # levy_calculator, reports, admin, etc.
            sa.Column('submodule', sa.String(64), nullable=True),  # Specific feature within module
            sa.Column('action_details', postgresql.JSON(astext_type=sa.Text()), nullable=True),  # Details specific to the action
            sa.Column('entity_type', sa.String(64), nullable=True),  # Type of entity being acted upon
            sa.Column('entity_id', sa.Integer(), nullable=True),  # ID of the entity being acted upon
            sa.Column('ip_address', sa.String(45), nullable=True),
            sa.Column('user_agent', sa.String(256), nullable=True),
            sa.Column('session_id', sa.String(128), nullable=True),
            sa.Column('success', sa.Boolean(), default=True, nullable=False),  # Did the action succeed?
            sa.Column('error_message', sa.Text(), nullable=True),  # Error message if action failed
            sa.Column('duration_ms', sa.Float(), nullable=True),  # How long the action took
            sa.PrimaryKeyConstraint('id'),
            *([sa.ForeignKeyConstraint(['user_id'], ['user.id'])] if has_user_table else [])
        )
        
        # Create indexes for efficient querying
        op.create_index(op.f('ix_user_action_log_user_id'), 
                       'user_action_log', ['user_id'])
        op.create_index(op.f('ix_user_action_log_timestamp'), 
                       'user_action_log', ['timestamp'])
        op.create_index(op.f('ix_user_action_log_action_type'), 
                       'user_action_log', ['action_type'])
        op.create_index(op.f('ix_user_action_log_module'), 
                       'user_action_log', ['module'])
        op.create_index(op.f('ix_user_action_log_session_id'), 
                       'user_action_log', ['session_id'])
        op.create_index(op.f('ix_user_action_log_success'), 
                       'user_action_log', ['success'])
        
        # Create composite indexes for common queries
        op.create_index('idx_user_action_type_module', 
                       'user_action_log', ['action_type', 'module'])
        op.create_index('idx_user_timestamp_action', 
                       'user_action_log', ['timestamp', 'action_type'])
        op.create_index('idx_user_entity_action', 
                       'user_action_log', ['entity_type', 'entity_id', 'action_type'])
    
    # Create LevyOverrideLog table if it doesn't exist
    if 'levy_override_log' not in inspector.get_table_names():
        # Check if the necessary tables exist before creating foreign keys
        has_user_table = 'user' in inspector.get_table_names()
        has_tax_district_table = 'tax_district' in inspector.get_table_names()
        has_tax_code_table = 'tax_code' in inspector.get_table_names()
        
        # Collect foreign key constraints based on existing tables
        fk_constraints = []
        if has_user_table:
            fk_constraints.append(sa.ForeignKeyConstraint(['user_id'], ['user.id']))
            if has_user_table:  # For approver_id
                fk_constraints.append(sa.ForeignKeyConstraint(['approver_id'], ['user.id']))
        if has_tax_district_table:
            fk_constraints.append(sa.ForeignKeyConstraint(['tax_district_id'], ['tax_district.id']))
        if has_tax_code_table:
            fk_constraints.append(sa.ForeignKeyConstraint(['tax_code_id'], ['tax_code.id']))
        
        op.create_table(
            'levy_override_log',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('timestamp', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
            sa.Column('tax_district_id', sa.Integer(), nullable=True),
            sa.Column('tax_code_id', sa.Integer(), nullable=True),
            sa.Column('year', sa.Integer(), nullable=False),
            sa.Column('field_name', sa.String(64), nullable=False),  # The field that was overridden
            sa.Column('original_value', sa.Float(), nullable=False),  # The calculated value
            sa.Column('override_value', sa.Float(), nullable=False),  # The user-provided value
            sa.Column('percent_change', sa.Float(), nullable=True),  # Percentage difference
            sa.Column('justification', sa.Text(), nullable=True),  # User's reason for override
            sa.Column('requires_approval', sa.Boolean(), default=False, nullable=True),  # Whether override requires approval
            sa.Column('approved', sa.Boolean(), nullable=True),  # NULL=pending, True=approved, False=rejected
            sa.Column('approver_id', sa.Integer(), nullable=True),
            sa.Column('approval_timestamp', sa.DateTime(), nullable=True),
            sa.Column('approval_notes', sa.Text(), nullable=True),
            sa.Column('calculation_params', postgresql.JSON(astext_type=sa.Text()), nullable=True),  # Parameters used in original calculation
            sa.PrimaryKeyConstraint('id'),
            *fk_constraints
        )
        
        # Create indexes for efficient querying
        op.create_index(op.f('ix_levy_override_log_user_id'), 
                       'levy_override_log', ['user_id'])
        op.create_index(op.f('ix_levy_override_log_timestamp'), 
                       'levy_override_log', ['timestamp'])
        op.create_index(op.f('ix_levy_override_log_tax_district_id'), 
                       'levy_override_log', ['tax_district_id'])
        op.create_index(op.f('ix_levy_override_log_tax_code_id'), 
                       'levy_override_log', ['tax_code_id'])
        op.create_index(op.f('ix_levy_override_log_year'), 
                       'levy_override_log', ['year'])
        
        # Create composite indexes for common queries
        op.create_index('idx_override_district_year', 
                       'levy_override_log', ['tax_district_id', 'year'])
        op.create_index('idx_override_approval_status', 
                       'levy_override_log', ['requires_approval', 'approved'])
        op.create_index('idx_override_user_field', 
                       'levy_override_log', ['user_id', 'field_name'])


def downgrade():
    """
    Remove the UserActionLog and LevyOverrideLog tables.
    """
    # Check if the tables exist before trying to drop them
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Drop LevyOverrideLog table and its indexes if it exists
    if 'levy_override_log' in inspector.get_table_names():
        # Drop indexes
        op.drop_index('idx_override_user_field', 'levy_override_log')
        op.drop_index('idx_override_approval_status', 'levy_override_log')
        op.drop_index('idx_override_district_year', 'levy_override_log')
        op.drop_index(op.f('ix_levy_override_log_year'), 'levy_override_log')
        op.drop_index(op.f('ix_levy_override_log_tax_code_id'), 'levy_override_log')
        op.drop_index(op.f('ix_levy_override_log_tax_district_id'), 'levy_override_log')
        op.drop_index(op.f('ix_levy_override_log_timestamp'), 'levy_override_log')
        op.drop_index(op.f('ix_levy_override_log_user_id'), 'levy_override_log')
        
        # Drop the table
        op.drop_table('levy_override_log')
    
    # Drop UserActionLog table and its indexes if it exists
    if 'user_action_log' in inspector.get_table_names():
        # Drop indexes
        op.drop_index('idx_user_entity_action', 'user_action_log')
        op.drop_index('idx_user_timestamp_action', 'user_action_log')
        op.drop_index('idx_user_action_type_module', 'user_action_log')
        op.drop_index(op.f('ix_user_action_log_success'), 'user_action_log')
        op.drop_index(op.f('ix_user_action_log_session_id'), 'user_action_log')
        op.drop_index(op.f('ix_user_action_log_module'), 'user_action_log')
        op.drop_index(op.f('ix_user_action_log_action_type'), 'user_action_log')
        op.drop_index(op.f('ix_user_action_log_timestamp'), 'user_action_log')
        op.drop_index(op.f('ix_user_action_log_user_id'), 'user_action_log')
        
        # Drop the table
        op.drop_table('user_action_log')