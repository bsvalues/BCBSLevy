# Database Migration Guidelines

This document provides guidance on using the Alembic-based migration system for the LevyMaster application.

## Overview

The LevyMaster application uses Alembic via Flask-Migrate to manage database schema changes in a structured, versioned way. This approach offers several advantages:

- **Version Control**: All schema changes are tracked and can be applied or reverted
- **Dependency Management**: Migrations can depend on previous migrations
- **Bidirectional Changes**: Support for both upgrading and downgrading
- **Automated Generation**: Ability to generate migrations from model changes

## Migration Workflow

### Creating a New Migration

1. Make changes to your SQLAlchemy models in `models.py`
2. Generate a migration script:
   ```
   python migrate.py migrate -m "Description of your changes"
   ```
3. Review the generated migration script in `migrations/versions/`
4. Edit the script if necessary to handle complex changes or data migrations
5. Apply the migration:
   ```
   python migrate.py upgrade
   ```

### Reverting a Migration

To revert the most recent migration:
```
python migrate.py downgrade
```

To revert to a specific migration version:
```
flask --app migrate db downgrade <revision_id>
```

### Checking Migration Status

To see the current migration version:
```
python migrate.py current
```

To view migration history:
```
python migrate.py history
```

## Best Practices

### 1. Make Migrations Idempotent

Always check if tables or columns exist before trying to create or modify them. Example:

```python
def upgrade():
    # Check if the table exists before trying to modify it
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'my_table' not in inspector.get_table_names():
        # Table doesn't exist, so create it
        # ...
```

### 2. Include Both Upgrade and Downgrade Functions

Always implement both `upgrade()` and `downgrade()` functions to ensure migrations can be reversed if needed.

### 3. Handle Data Migrations

When changing column types or constraints that require data transformation:

```python
def upgrade():
    # Create a temporary column
    op.add_column('my_table', sa.Column('new_column', sa.String(50)))
    
    # Copy and transform data
    conn = op.get_bind()
    conn.execute(
        """
        UPDATE my_table 
        SET new_column = CAST(old_column AS VARCHAR(50))
        """
    )
    
    # Drop the old column and rename the new one
    op.drop_column('my_table', 'old_column')
    op.alter_column('my_table', 'new_column', new_column_name='old_column')
```

### 4. Use Transactions

For data-changing operations, consider using transactions to ensure atomicity:

```python
def upgrade():
    connection = op.get_bind()
    transaction = connection.begin()
    try:
        # Migration operations
        transaction.commit()
    except:
        transaction.rollback()
        raise
```

### 5. Test Migrations in Development First

Always test migrations in a development environment before applying them to production.

## Common Migration Operations

### Adding a Table

```python
op.create_table(
    'my_table',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(50), nullable=False),
    sa.PrimaryKeyConstraint('id')
)
```

### Adding a Column

```python
op.add_column('my_table', sa.Column('new_column', sa.String(50)))
```

### Adding an Index

```python
op.create_index(op.f('ix_my_table_name'), 'my_table', ['name'])
```

### Adding a Foreign Key

```python
op.create_foreign_key(
    'fk_my_table_other_table', 
    'my_table', 'other_table',
    ['other_id'], ['id']
)
```

## Troubleshooting

### Migration Conflicts

If you get conflicts between migrations:

1. Check that your `down_revision` in your migration script points to the correct previous migration
2. Use `flask --app migrate db branches` to see if there are multiple migration branches
3. Consider using `flask --app migrate db merge` to merge branches

### Failed Migrations

If a migration fails:

1. Check the error message carefully
2. Downgrade to the previous working version
3. Fix the migration script
4. Try upgrading again

## For More Information

- [Flask-Migrate Documentation](https://flask-migrate.readthedocs.io/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)