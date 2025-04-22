# Database Backup and Restore Guide

This guide details the available tools and methods for backing up and restoring the PostgreSQL database in the Levy Calculation System.

## Quick Reference

```bash
# Create a database backup
python cli_tool.py backup

# Verify database connection
python cli_tool.py verify

# Display database information
python cli_tool.py info
```

## Available Tools

The system provides several tools for database backup and restoration:

### 1. CLI Tool (`cli_tool.py`)

A standalone command-line tool that doesn't require the Flask application context. This is the recommended method for quick operations.

**Commands:**

- `backup`: Create a database backup
- `verify`: Verify database connectivity
- `info`: Display database information

**Usage:**

```bash
python cli_tool.py backup
```

### 2. Flask CLI Commands

These commands are integrated with Flask's command-line interface but require the Flask application context.

**Commands:**

- `flask db_utils backup`: Create a database backup
- `flask db_utils restore <backup_file>`: Restore from a backup file
- `flask db_utils health_check`: Check database connectivity
- `flask db_utils prune_logs`: Prune old database logs

**Usage:**

```bash
FLASK_APP=main flask db_utils backup
```

### 3. Direct Script Execution

For specific backup needs, you can directly execute the backup scripts:

- `pg_backup_simple.py`: Creates backups using psycopg2 (recommended)
- `pg_backup.py`: Creates backups using pg_dump (fallback)
- `pg_verify.py`: Verifies database connectivity

**Usage:**

```bash
python pg_backup_simple.py
```

## Backup Formats

The system supports two backup formats:

1. **Simple Format** (pg_backup_simple.py):

   - Uses pure SQL commands generated with psycopg2
   - Compatible across PostgreSQL versions
   - Includes schema, data, constraints, and sequences
   - Files begin with `-- Database Backup:` comment

2. **pg_dump Format** (pg_backup.py):
   - Uses the PostgreSQL pg_dump utility
   - May have version compatibility issues
   - More comprehensive for complex schemas

## Backup File Storage

Backups are stored in the `backups/` directory with filenames that include timestamps:

- Simple backups: `pg_backup_YYYYMMDD_HHMMSS.sql`
- pg_dump backups: `database_backup_YYYYMMDD_HHMMSS.sql`

## Restoration Process

To restore a database from a backup:

```bash
# Using Flask CLI
FLASK_APP=main flask db_utils restore backups/pg_backup_20250402_004811.sql

# Using psql directly
psql -h $PGHOST -U $PGUSER -d $PGDATABASE -f backups/pg_backup_20250402_004811.sql
```

The restoration process will:

1. Detect the backup format automatically
2. Use the appropriate method (psycopg2 or psql)
3. Execute the SQL commands to recreate the database structure and data

## Scheduling Regular Backups

For production environments, it's recommended to schedule regular backups using cron or a similar scheduler:

```bash
# Example cron entry for daily backups at 2 AM
0 2 * * * cd /path/to/app && python cli_tool.py backup
```

## Troubleshooting

If you encounter issues with backups or restoration:

1. Verify database connectivity: `python cli_tool.py verify`
2. Check database information: `python cli_tool.py info`
3. Inspect the logs for detailed error messages
4. Try both backup methods if one fails

## Version Compatibility

- The simple backup method (`pg_backup_simple.py`) works across PostgreSQL versions
- The pg_dump method (`pg_backup.py`) requires matching client and server versions
