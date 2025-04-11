"""Add LevyAuditRecord table for audit tracking

Revision ID: 5d6e7f8g9h0i
Revises: 4c5d6e7f8g9h
Create Date: 2025-04-11 15:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5d6e7f8g9h0i'
down_revision = '4c5d6e7f8g9h'  # This should point to the previous migration
branch_labels = None
depends_on = None


def upgrade():
    """
    Create the LevyAuditRecord table for storing levy audit results.
    
    This table stores audit records from the Levy Audit AI Agent,
    providing historical tracking of levy audits, compliance checks, and recommendations.
    """
    # Check if the table already exists before creating it
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'levy_audit_record' in inspector.get_table_names():
        return
    
    # Check if the necessary tables exist before creating foreign keys to them
    required_tables = ['user', 'tax_district', 'tax_code']
    for table in required_tables:
        if table not in inspector.get_table_names():
            raise Exception(f"{table} table does not exist, cannot create foreign key")
    
    # Create the levy_audit_record table
    op.create_table(
        'levy_audit_record',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tax_district_id', sa.Integer(), nullable=True),
        sa.Column('tax_code_id', sa.Integer(), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('audit_type', sa.String(32), nullable=False),  # COMPLIANCE, RECOMMENDATION, VERIFICATION, QUERY
        sa.Column('full_audit', sa.Boolean(), default=False, nullable=True),
        sa.Column('compliance_score', sa.Float(), nullable=True),
        sa.Column('query', sa.Text(), nullable=True),
        sa.Column('results', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(32), default='PENDING', nullable=False),  # PENDING, COMPLETED, FAILED
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('error_details', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['tax_district_id'], ['tax_district.id'], ),
        sa.ForeignKeyConstraint(['tax_code_id'], ['tax_code.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for efficient querying
    op.create_index(op.f('ix_levy_audit_record_user_id'), 
                   'levy_audit_record', ['user_id'])
    op.create_index(op.f('ix_levy_audit_record_tax_district_id'), 
                   'levy_audit_record', ['tax_district_id'])
    op.create_index(op.f('ix_levy_audit_record_tax_code_id'), 
                   'levy_audit_record', ['tax_code_id'])
    op.create_index(op.f('ix_levy_audit_record_year'), 
                   'levy_audit_record', ['year'])
    op.create_index(op.f('ix_levy_audit_record_audit_type'), 
                   'levy_audit_record', ['audit_type'])
    
    # Create composite indexes for common queries
    op.create_index('idx_audit_district_year', 
                   'levy_audit_record', ['tax_district_id', 'year'])
    op.create_index('idx_audit_type_status', 
                   'levy_audit_record', ['audit_type', 'status'])
    op.create_index('idx_audit_user_district', 
                   'levy_audit_record', ['user_id', 'tax_district_id'])


def downgrade():
    """
    Remove the LevyAuditRecord table.
    """
    # Check if the table exists before trying to drop it
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'levy_audit_record' not in inspector.get_table_names():
        return
    
    # Drop indexes
    op.drop_index('idx_audit_user_district', 'levy_audit_record')
    op.drop_index('idx_audit_type_status', 'levy_audit_record')
    op.drop_index('idx_audit_district_year', 'levy_audit_record')
    op.drop_index(op.f('ix_levy_audit_record_audit_type'), 'levy_audit_record')
    op.drop_index(op.f('ix_levy_audit_record_year'), 'levy_audit_record')
    op.drop_index(op.f('ix_levy_audit_record_tax_code_id'), 'levy_audit_record')
    op.drop_index(op.f('ix_levy_audit_record_tax_district_id'), 'levy_audit_record')
    op.drop_index(op.f('ix_levy_audit_record_user_id'), 'levy_audit_record')
    
    # Drop the table
    op.drop_table('levy_audit_record')