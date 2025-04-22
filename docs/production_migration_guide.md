# Production Database Migration Guide

This guide provides step-by-step instructions for managing database migrations in the Levy Calculation System's production environment.

## Quick Migration Steps

### 1. Set Up the Environment

Ensure your PostgreSQL connection details are properly configured:

```bash
# Required environment variables
export DATABASE_URL=postgresql://username:password@hostname:port/dbname
export FLASK_ENV=production
```

### 2. Backup the Current Database

Always create a backup before running migrations:

```bash
python production_migrate.py backup
```

This will create a compressed backup file in the `backups/` directory.

### 3. Preview Migrations (Optional)

Preview the migration SQL without applying changes:

```bash
python production_migrate.py migrate --dry-run
```

This generates the SQL that would be executed in a file named `migration_preview.sql`.

### 4. Apply Migrations

Run the migrations with safety checks:

```bash
python production_migrate.py migrate
```

This process will:

- Create a backup
- Record the pre-migration schema
- Apply migrations
- Record the post-migration schema
- Generate a comprehensive migration report

### 5. Verify the Migration

Confirm the migrations were applied correctly:

```bash
python production_migrate.py verify
```

### 6. Generate a Database Report

Create a report of the current database state:

```bash
python production_migrate.py report
```

## Recovering from Failed Migrations

### Option 1: Downgrade the Database

If the migration fails at a specific step, you can try downgrading:

```bash
python migrate.py downgrade
```

### Option 2: Restore from Backup

If downgrade is not possible, restore from a backup:

```bash
python production_migrate.py restore backups/pg_backup_YYYYMMDD_HHMMSS.sql
```

## Full Production Setup

To perform a complete production setup including migrations:

```bash
python setup_production.py
```

This will:

1. Create necessary directories (logs, backups)
2. Check database connection
3. Backup the current database
4. Apply migrations
5. Verify application functionality

## For More Information

For detailed information about PostgreSQL migration strategies and best practices, see:

- [PostgreSQL Production Database Migration Guide](postgresql_production_migration.md)
- [Flask-Migrate Documentation](https://flask-migrate.readthedocs.io/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

## Troubleshooting

### Common Issues

#### Invalid Database Connection

If you encounter connection errors:

1. Verify your PostgreSQL credentials
2. Ensure the database exists
3. Check network access to the database server

#### Migration Timeout

For large databases, migrations may time out:

1. Increase `statement_timeout` in PostgreSQL configuration
2. Use the `--sql` flag to generate SQL and run manually in batches

#### Database Locked

If the database is locked during migration:

1. Check for long-running queries
2. Terminate blocking connections
3. Schedule migrations during off-peak hours

## Need Help?

For additional assistance with database migrations, contact the Levy Calculation System support team.
