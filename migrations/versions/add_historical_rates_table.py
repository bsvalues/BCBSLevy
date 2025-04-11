"""Add TaxCodeHistoricalRate table for multi-year support

Revision ID: 4c5d6e7f8g9h
Revises: 3b4c5d6e7f8g
Create Date: 2025-04-11 15:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c5d6e7f8g9h'
down_revision = '3b4c5d6e7f8g'  # This should point to the previous migration
branch_labels = None
depends_on = None


def upgrade():
    """
    Create the TaxCodeHistoricalRate table for multi-year support.
    
    This table stores historical tax rates for each tax code over multiple years.
    """
    # Check if the table already exists before creating it
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'tax_code_historical_rate' in inspector.get_table_names():
        return
    
    # Check if the tax_code table exists before creating a foreign key to it
    if 'tax_code' not in inspector.get_table_names():
        # We can't create a foreign key to a non-existent table
        # Consider creating just the table without the foreign key
        # or raising an exception
        raise Exception("tax_code table does not exist, cannot create foreign key")
    
    # Create the tax_code_historical_rate table
    op.create_table(
        'tax_code_historical_rate',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tax_code_id', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('levy_rate', sa.Float(), nullable=False),
        sa.Column('levy_amount', sa.Float(), nullable=True),
        sa.Column('total_assessed_value', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=True),
        sa.ForeignKeyConstraint(['tax_code_id'], ['tax_code.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tax_code_id', 'year', name='uix_tax_code_year')
    )
    
    # Create indexes for efficient querying
    op.create_index(op.f('ix_tax_code_historical_rate_tax_code_id'), 
                   'tax_code_historical_rate', ['tax_code_id'])
    op.create_index(op.f('ix_tax_code_historical_rate_year'), 
                   'tax_code_historical_rate', ['year'])


def downgrade():
    """
    Remove the TaxCodeHistoricalRate table.
    """
    # Check if the table exists before trying to drop it
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'tax_code_historical_rate' not in inspector.get_table_names():
        return
    
    # Drop indexes
    op.drop_index(op.f('ix_tax_code_historical_rate_year'), 
                 'tax_code_historical_rate')
    op.drop_index(op.f('ix_tax_code_historical_rate_tax_code_id'), 
                 'tax_code_historical_rate')
    
    # Drop the table
    op.drop_table('tax_code_historical_rate')