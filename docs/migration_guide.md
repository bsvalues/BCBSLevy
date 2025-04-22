# Database Migration Guide

This guide explains how to manage database migrations for the Levy Calculation Application using Flask-Migrate.

## Overview

The Levy Calculation Application uses Flask-Migrate (built on top of Alembic) to manage database schema changes. This system allows for:

- Tracking database schema changes in version control
- Safe deployment of database changes to production environments
- Rolling back database changes if necessary
- Maintaining consistency across development, testing, and production environments

## Migration Commands

The following commands are available for managing database migrations:

### Using the Python Script Interface

```bash
# Initialize migration repository
python migrate.py init

# Generate a new migration script based on model changes
python migrate.py migrate -m "description of changes"

# Apply migrations to the database
python migrate.py upgrade

# Roll back the most recent migration
python migrate.py downgrade

# Show current migration version
python migrate.py current

# Display migration history
python migrate.py history
```

### Using Flask CLI Directly

```bash
# Initialize migration repository
flask --app migrate db init

# Generate a new migration script based on model changes
flask --app migrate db migrate -m "description of changes"

# Apply migrations to the database
flask --app migrate db upgrade

# Roll back the most recent migration
flask --app migrate db downgrade

# Show current migration version
flask --app migrate db current

# Display migration history
flask --app migrate db history
```

## Migration Workflow

### Development Process

1. Make changes to the database models in `models.py`
2. Generate a migration script:
   ```bash
   python migrate.py migrate -m "Add new field to Property table"
   ```
3. Review the generated migration script in the `migrations/versions/` directory
4. Apply the migration to your development database:
   ```bash
   python migrate.py upgrade
   ```
5. Test the changes thoroughly
6. Commit the migration script to version control

### Deployment Process

1. Pull the latest code, including migration scripts
2. Apply pending migrations to the production database:
   ```bash
   python migrate.py upgrade
   ```

## Best Practices

### Writing Migrations

- Always include a clear description with the `-m` flag
- Review generated migrations before applying them
- Test migrations on a staging environment before production
- For complex migrations, consider writing a custom migration script

### Manual Migrations

For complex changes that can't be automatically detected:

1. Create an empty migration:
   ```bash
   flask --app migrate db revision -m "Complex migration description"
   ```
2. Edit the generated file in `migrations/versions/` to include your custom upgrade and downgrade logic
3. Test thoroughly before deployment

### Rollbacks

In case of problems:

1. Roll back the most recent migration:
   ```bash
   python migrate.py downgrade
   ```
2. Fix the issues and generate a new migration

## Troubleshooting

### Migration Not Detecting Changes

If your model changes aren't being detected:

1. Ensure the models are properly imported in `app.py`
2. Check that the models inherit from `db.Model`
3. Try using the `--compare-type` flag:
   ```bash
   flask --app migrate db migrate --compare-type -m "Force detect column type changes"
   ```

### Merge Conflicts in Migration Scripts

If multiple developers create migrations simultaneously:

1. Resolve Git conflicts in the migration script files
2. Ensure the order of migrations in `migrations/versions/` is correct (check the `down_revision` values)
3. Create a new merge migration if necessary:
   ```bash
   flask --app migrate db merge heads -m "Merge multiple migration heads"
   ```

## Production Deployment Considerations

- Always back up the production database before running migrations
- Schedule migrations during off-peak hours
- Consider the impact of schema changes on application uptime
- For large tables, consider using background migrations or batching

## Environment-Specific Configuration

The migration system uses the database URL specified in the application configuration. Make sure the correct database URL is set in each environment:

- Development: Local PostgreSQL database
- Testing: Test database (possibly in-memory)
- Production: Production PostgreSQL database

Environment variables are used to ensure proper configuration for each environment.
