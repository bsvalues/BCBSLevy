"""Add audit columns to import_log table

Revision ID: 3b4c5d6e7f8g
Revises: 2a3b4c5d6e7f
Create Date: 2025-04-11 15:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3b4c5d6e7f8g'
down_revision = '2a3b4c5d6e7f'  # This should point to the previous migration
branch_labels = None
depends_on = None


def upgrade():
    """
    Add audit columns to the import_log table.
    
    This adds created_at, updated_at, created_by_id, and updated_by_id columns
    to the import_log table to match the AuditMixin definition.
    """
    # Check if the table exists before trying to modify it
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'import_log' not in inspector.get_table_names():
        # Table doesn't exist, so we can't modify it
        return
    
    # Get existing columns to check which ones we need to add
    columns = [column['name'] for column in inspector.get_columns('import_log')]
    
    # Add created_at column if it doesn't exist
    if 'created_at' not in columns:
        op.add_column('import_log', 
                      sa.Column('created_at', sa.DateTime(), 
                                server_default=sa.text('NOW()'), 
                                nullable=True))
    
    # Add updated_at column if it doesn't exist
    if 'updated_at' not in columns:
        op.add_column('import_log', 
                      sa.Column('updated_at', sa.DateTime(), 
                                server_default=sa.text('NOW()'), 
                                nullable=True))
    
    # Add created_by_id column if it doesn't exist
    if 'created_by_id' not in columns:
        op.add_column('import_log', 
                      sa.Column('created_by_id', sa.Integer(), 
                                nullable=True))
        
        # Add foreign key constraint for created_by_id
        # First check if the user table exists
        if 'user' in inspector.get_table_names():
            op.create_foreign_key(
                'fk_import_log_created_by', 
                'import_log', 'user',
                ['created_by_id'], ['id']
            )
    
    # Add updated_by_id column if it doesn't exist
    if 'updated_by_id' not in columns:
        op.add_column('import_log', 
                      sa.Column('updated_by_id', sa.Integer(), 
                                nullable=True))
        
        # Add foreign key constraint for updated_by_id
        # First check if the user table exists
        if 'user' in inspector.get_table_names():
            op.create_foreign_key(
                'fk_import_log_updated_by', 
                'import_log', 'user',
                ['updated_by_id'], ['id']
            )


def downgrade():
    """
    Remove the audit columns from the import_log table.
    """
    # Check if the table exists before trying to modify it
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'import_log' not in inspector.get_table_names():
        # Table doesn't exist, so we can't modify it
        return
    
    # Drop foreign key constraints if they exist
    for fk in inspector.get_foreign_keys('import_log'):
        if fk['name'] in ['fk_import_log_created_by', 'fk_import_log_updated_by']:
            op.drop_constraint(
                fk['name'],
                'import_log',
                type_='foreignkey'
            )
    
    # Drop the columns
    op.drop_column('import_log', 'updated_by_id')
    op.drop_column('import_log', 'created_by_id')
    op.drop_column('import_log', 'updated_at')
    op.drop_column('import_log', 'created_at')