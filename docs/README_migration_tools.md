# Database Migration Tools

This directory contains tools and documentation for managing database migrations and backups in the Levy Calculation System.

## Available Migration Tools

1. **Standard Migration Tool (`migrate.py`)**

   - Basic Flask-Migrate integration
   - Handles migrations for all database types
   - Used for development environments

2. **Production PostgreSQL Migration Tool (`production_migrate.py`)**

   - Enhanced migration capabilities for PostgreSQL
   - Built-in backup and restore functionality
   - Schema comparison and reporting
   - Dry-run capability

3. **Production Setup Tool (`setup_production.py`)**

   - Full production environment setup
   - Database backup
   - Migration application
   - Directory creation and permissions
   - Application verification

4. **Database CLI Tool (`cli_tool.py`)**

   - Standalone database operations without Flask context
   - Quick database backup, verification, and information
   - Compatible with all PostgreSQL versions

5. **PostgreSQL Backup Tools**
   - Simple backup (`pg_backup_simple.py`) - Uses psycopg2, version-independent
   - Advanced backup (`pg_backup.py`) - Uses pg_dump, requires version match
   - Connection verification (`pg_verify.py`) - Tests database connectivity

## Documentation

1. [Production Migration Guide](production_migration_guide.md)

   - Step-by-step migration instructions
   - Quick reference for common tasks
   - Troubleshooting guide

2. [PostgreSQL Production Migration Guide](postgresql_production_migration.md)

   - Detailed PostgreSQL-specific considerations
   - Advanced migration strategies
   - Performance optimization techniques
   - Schema evolution patterns

3. [Database Backup and Restore Guide](database_backup_restore.md)
   - Comprehensive backup and restore procedures
   - Available tools and methods
   - Troubleshooting guide
   - Version compatibility information

## Migration Workflow Overview

### Development Environment

```
python migrate.py init     # Initialize migrations (first time only)
python migrate.py migrate  # Generate migration files
python migrate.py upgrade  # Apply migrations
```

### Production Environment

```
python production_migrate.py backup   # Create a backup
python production_migrate.py migrate  # Apply migrations with safety checks
python production_migrate.py verify   # Verify successful migration
```

### Full Production Setup

```
python setup_production.py
```

## Emergency Recovery

If migrations fail in production:

```
python production_migrate.py restore backups/pg_backup_YYYYMMDD_HHMMSS.sql
```

## Migration Commands Reference

### Standard Migration Commands

- `python migrate.py init` - Initialize migrations directory
- `python migrate.py migrate [-m "message"]` - Generate migration files
- `python migrate.py upgrade` - Apply migrations
- `python migrate.py downgrade` - Revert migrations
- `python migrate.py current` - Show current migration version
- `python migrate.py history` - Show migration history

### Production PostgreSQL Migration Commands

- `python production_migrate.py backup [--output-dir DIR]` - Backup database
- `python production_migrate.py migrate [--dry-run]` - Apply migrations
- `python production_migrate.py restore BACKUP_FILE` - Restore from backup
- `python production_migrate.py verify` - Check migration status
- `python production_migrate.py report` - Generate database report

### Database CLI Commands

- `python cli_tool.py backup` - Create a database backup
- `python cli_tool.py verify` - Verify database connectivity
- `python cli_tool.py info` - Display database information

### Direct Backup Commands

- `python pg_backup_simple.py [--output-dir DIR]` - Create psycopg2-based backup (version-independent)
- `python pg_backup.py [--output-dir DIR]` - Create pg_dump-based backup
- `python pg_verify.py` - Verify database connectivity

## Best Practices

1. **Always backup before migrating**

   ```
   python cli_tool.py backup  # Quick standalone backup
   # OR
   python production_migrate.py backup  # Backup as part of migration process
   ```

2. **Preview migrations in production**

   ```
   python production_migrate.py migrate --dry-run
   ```

3. **Generate reports before and after migrations**

   ```
   python production_migrate.py report
   ```

4. **Include descriptive messages with migrations**

   ```
   python migrate.py migrate -m "Add tax_district_type column to tax_district table"
   ```

5. **Run regular health checks after migration**

   ```
   python cli_tool.py verify  # Quick connectivity check
   # OR
   python production_migrate.py verify  # Comprehensive verification
   ```

6. **Schedule regular backups**
   ```
   # Add to crontab for daily backups at 2 AM
   0 2 * * * cd /path/to/app && python cli_tool.py backup
   ```
