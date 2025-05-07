# Database Model Guidelines for TerraLevy

This document outlines the best practices and standards for creating and modifying database models in the TerraLevy application. Following these guidelines will help maintain consistency, reduce errors, and improve the maintainability of the application.

## General Principles

1. **Database-First Approach**: Always validate your model changes against the actual database schema.
2. **Consistent Naming**: Use clear, consistent naming conventions for models, tables, and columns.
3. **Documentation**: All models should include proper documentation.
4. **Validation**: Include proper validation and constraints in models.

## Model Creation Best Practices

### Model Definition

```python
class ExampleModel(db.Model):
    """
    Descriptive comment about what this model represents.
    
    This model handles [business purpose]. It is related to [other models]
    and is used in [specific features/functionality].
    """
    __tablename__ = 'example_table'
    
    # Primary key and identifiers
    id = db.Column(db.Integer, primary_key=True)
    
    # Core data fields with descriptive comments
    name = db.Column(db.String(128), nullable=False, index=True, 
                     doc="The user-friendly name visible in the UI")
    code = db.Column(db.String(20), nullable=False, unique=True, 
                     doc="Unique identifier code used in API and exports")
    
    # Foreign keys
    parent_id = db.Column(db.Integer, db.ForeignKey('parent_table.id'), 
                          nullable=True, index=True,
                          doc="Reference to parent entity")
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                           onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), 
                             nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), 
                             nullable=True)
    
    # Boolean flags
    is_active = db.Column(db.Boolean, default=True, 
                         doc="Controls whether this item is active in the system")
    
    # Relationships (explicit foreign_keys for clarity)
    parent = db.relationship('ParentModel', foreign_keys=[parent_id], 
                            backref='children')
    created_by = db.relationship('User', foreign_keys=[created_by_id], 
                                backref='created_examples')
    updated_by = db.relationship('User', foreign_keys=[updated_by_id], 
                                backref='updated_examples')
    
    def __repr__(self):
        """Provide a readable representation of this instance."""
        return f'<ExampleModel {self.name} ({self.code})>'
```

### Field Naming Conventions

* Use snake_case for column names (e.g., `first_name`, `tax_district_id`)
* Use descriptive names that reflect the business meaning
* Include prefixes for foreign keys (e.g., `user_id`, `tax_district_id`)
* Be consistent with column types and constraints

### Relationship Definitions

Always specify `foreign_keys` in relationship definitions when there could be ambiguity:

```python
# Good - explicitly identifies which column to use for the relationship
created_by = db.relationship('User', foreign_keys=[created_by_id], 
                            backref='created_items')

# Bad - ambiguous when multiple foreign keys reference the same table
created_by = db.relationship('User', backref='created_items')  
```

## Model Modification Process

When modifying existing models, follow these steps:

1. **Validate Current Schema**:
   ```bash
   python db_schema_validator.py
   ```

2. **Create Migration Script**:
   ```bash
   cp migration_template.py migrations/YYYYMMDD_descriptive_name.py
   # Edit the new file to implement the specific changes
   ```

3. **Test Migration**:
   ```bash
   python migrations/YYYYMMDD_descriptive_name.py --check
   ```

4. **Apply Migration**:
   ```bash
   python migrations/YYYYMMDD_descriptive_name.py --apply
   ```

5. **Update Models**:
   - Modify the SQLAlchemy model to match the database changes
   - Ensure all relationships are updated accordingly
   - Update any affected controllers or services

6. **Verify Changes**:
   ```bash
   python db_schema_validator.py
   ```

## Common Pitfalls to Avoid

1. **Implicit Column Types**: Always specify column types explicitly instead of relying on SQLAlchemy defaults.

2. **Missing Indexes**: Add indexes for columns frequently used in WHERE clauses or joins.

3. **Inconsistent Foreign Keys**: Ensure foreign key names match the convention (e.g., `table_id`).

4. **Ambiguous Relationships**: Always specify `foreign_keys` in relationship definitions.

5. **Missing Nullable Constraints**: Explicitly set `nullable=True/False` based on business requirements.

6. **Forgetting Audit Fields**: Include created/updated timestamps and user references.

7. **Circular Imports**: Structure your models to avoid circular import dependencies.

## Additional Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/en/14/)
- [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/en/2.x/)
- [TerraLevy SQL Coding Standards](./sql_coding_standards.md)