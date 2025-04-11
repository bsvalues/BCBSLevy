"""Add API Call Log Table

Revision ID: 2a3b4c5d6e7f
Revises: 1a2b3c4d5e6f
Create Date: 2025-04-11 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2a3b4c5d6e7f'
down_revision = '1a2b3c4d5e6f'  # This should match the revision ID of the last migration
branch_labels = None
depends_on = None


def upgrade():
    """
    Create the APICallLog table for API call tracking.
    
    This table stores historical API call records for monitoring
    and analytics purposes, providing data for:
    - API usage statistics and trends
    - Performance monitoring and troubleshooting
    - Error rate tracking
    - Service dependency analysis
    """
    # Create the api_call_log table
    op.create_table(
        'api_call_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('service', sa.String(64), nullable=False),  # e.g. "anthropic", "openai", etc.
        sa.Column('endpoint', sa.String(128), nullable=False),
        sa.Column('method', sa.String(16), nullable=False),  # HTTP method
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('duration_ms', sa.Float(), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False, default=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, default=0),
        sa.Column('params', postgresql.JSON(astext_type=sa.Text()), nullable=True),  # Redacted parameters
        sa.Column('response_summary', postgresql.JSON(astext_type=sa.Text()), nullable=True),  # Summarized response
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for efficient querying
    op.create_index('idx_api_call_service_success', 'api_call_log', ['service', 'success'])
    op.create_index('idx_api_call_timestamp_service', 'api_call_log', ['timestamp', 'service'])
    op.create_index(op.f('ix_api_call_log_endpoint'), 'api_call_log', ['endpoint'])
    op.create_index(op.f('ix_api_call_log_service'), 'api_call_log', ['service'])
    op.create_index(op.f('ix_api_call_log_success'), 'api_call_log', ['success'])
    op.create_index(op.f('ix_api_call_log_timestamp'), 'api_call_log', ['timestamp'])
    op.create_index(op.f('ix_api_call_log_user_id'), 'api_call_log', ['user_id'])


def downgrade():
    """
    Remove the APICallLog table.
    """
    # Drop indexes
    op.drop_index(op.f('ix_api_call_log_user_id'), 'api_call_log')
    op.drop_index(op.f('ix_api_call_log_timestamp'), 'api_call_log')
    op.drop_index(op.f('ix_api_call_log_success'), 'api_call_log')
    op.drop_index(op.f('ix_api_call_log_service'), 'api_call_log')
    op.drop_index(op.f('ix_api_call_log_endpoint'), 'api_call_log')
    op.drop_index('idx_api_call_timestamp_service', 'api_call_log')
    op.drop_index('idx_api_call_service_success', 'api_call_log')
    
    # Drop the table
    op.drop_table('api_call_log')