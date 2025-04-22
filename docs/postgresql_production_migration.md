# PostgreSQL Production Database Migration Guide

This document provides detailed instructions for managing database migrations in a production PostgreSQL environment for the Levy Calculation System.

## Overview

The Levy Calculation System uses Flask-Migrate (built on Alembic) for database schema migrations with additional PostgreSQL-specific tooling for production environments. This comprehensive approach ensures:

1. Safe, transactional migrations with validation
2. Robust backup and restore capabilities
3. Performance optimizations for large datasets
4. Detailed reporting and schema comparison
5. Dry-run capabilities to preview migrations

## PostgreSQL-Specific Considerations

PostgreSQL has specific considerations for production migrations:

- **Transactional DDL**: Unlike some databases, PostgreSQL supports transactional DDL (Data Definition Language), allowing schema changes to be rolled back if an error occurs during migration.
- **Concurrent Index Creation**: For large tables, consider using `CREATE INDEX CONCURRENTLY` to avoid table locks.
- **Connection Pooling**: Be aware of connection pools that may hold onto connections with outdated schema information.
- **Table Locks**: Some migrations (like adding a column with a default value) can lock tables for extended periods.

## Migration Workflow

### Pre-Migration Steps

1. **Environment Setup**

   - Ensure PostgreSQL credentials are properly configured in environment variables
   - Set `FLASK_ENV=production`

2. **Backup Current Database**

   ```bash
   ./production_migrate.py backup
   ```

   This creates a compressed backup using the custom format in the `backups/` directory.

3. **Generate Migration Report**

   ```bash
   ./production_migrate.py report
   ```

   This creates a comprehensive report including database size, table information, and migration status.

4. **Preview Migrations (Dry Run)**

   ```bash
   ./production_migrate.py migrate --dry-run
   ```

   This generates the SQL that would be executed without actually running it.

### Performing the Migration

1. **Schedule Migration Window**

   - For critical systems, schedule a maintenance window
   - Notify users if downtime is expected

2. **Run Migration with Verification**

   ```bash
   ./production_migrate.py migrate
   ```

   This will:

   - Backup the current database
   - Dump the pre-migration schema
   - Apply the migrations
   - Dump the post-migration schema
   - Compare schemas to identify changes
   - Generate a migration report

3. **Verify Database Integrity**

   ```bash
   ./production_migrate.py verify
   ```

   This checks the database connection and current migration status.

### Post-Migration Steps

1. **Verify Application Functionality**

   - Run automated tests if available
   - Manually test critical features
   - Monitor logs for errors

2. **Generate Post-Migration Report**

   ```bash
   ./production_migrate.py report
   ```

   This creates a comprehensive report of the current database state.

3. **Archive Migration Reports**
   - Keep migration reports for audit purposes
   - Store both pre and post-migration backups until stability is confirmed

## Recovery Procedures

### Rolling Back Migrations

If issues are detected after migration:

1. **Downgrade Database**

   ```bash
   python migrate.py downgrade
   ```

   This rolls back to the previous migration version.

2. **Restore from Backup**
   If downgrade fails or major issues occur:

   ```bash
   ./production_migrate.py restore backups/pg_backup_YYYYMMDD_HHMMSS.sql
   ```

   This completely restores the database from a backup file.

## Best Practices for PostgreSQL Migrations

### Performance Optimization

1. **Batched Migrations for Large Tables**

   - When modifying large tables, consider batching updates
   - For data migrations, use `COPY` instead of multiple `INSERT` statements

2. **Indexing Considerations**

   - Create indexes using `CREATE INDEX CONCURRENTLY` for large tables
   - Drop indexes before bulk loading data, then recreate them

3. **Connection Management**
   - Close all unnecessary connections during migration
   - Increase `statement_timeout` for complex migrations

### Schema Evolution Patterns

1. **Adding Columns**

   - Add nullable columns without defaults first
   - Update data in batches
   - Then add constraints if needed

2. **Changing Column Types**

   - Add a new column with the desired type
   - Migrate data in batches
   - Swap column names when complete

3. **Renaming Tables/Columns**
   - Use a temporary transition period with views
   - Update application code in stages

## Common Problems and Solutions

### Connection Timeouts

**Problem**: Migrations timeout or connections drop during long-running operations.

**Solution**:

- Increase `statement_timeout` in PostgreSQL configuration
- Use `keep-alive` connections
- Split complex migrations into smaller steps

### Table Locks

**Problem**: DDL operations lock tables, preventing application access.

**Solution**:

- Use `CONCURRENTLY` when possible
- Schedule migrations during low-traffic periods
- Consider zero-downtime migration techniques (temporary tables, views)

### Out of Disk Space

**Problem**: Migrations require temporary disk space that may not be available.

**Solution**:

- Check available disk space before migration
- Clean up old backups or unused data
- Monitor disk usage during migration

## Production-Specific Commands

### Database Backup

Create a full database backup:

```bash
./production_migrate.py backup
```

Options:

- `--output-dir PATH`: Specify a custom directory for backups

### Database Restore

Restore a database from backup:

```bash
./production_migrate.py restore backups/pg_backup_YYYYMMDD_HHMMSS.sql
```

This will:

1. Prompt for confirmation (data loss warning)
2. Create a backup of the current state
3. Drop and recreate the database
4. Restore from the specified backup file

### Database Report

Generate a comprehensive database report:

```bash
./production_migrate.py report
```

This creates a report including:

- Database version and size
- Table sizes and row counts
- Current migration status
- Migration history
- Available backups

### Schema Verification

The migration process automatically:

1. Dumps pre-migration schema
2. Applies migrations
3. Dumps post-migration schema
4. Compares the two schemas
5. Generates a diff report

## Security Considerations

1. **Backup Security**

   - Backup files contain all database data and should be secured
   - Consider encrypting backup files for sensitive data
   - Rotate or delete old backups according to data retention policies

2. **Connection Security**

   - Use SSL for database connections
   - Avoid storing database credentials in scripts
   - Use environment variables or a secure credential store

3. **Permission Management**
   - Run migrations with a user that has only the necessary permissions
   - Consider a separate migration user with enhanced permissions just for migrations

## Monitoring and Alerting

For critical production migrations:

1. Set up monitoring for:

   - Database locks and long-running queries
   - Table and index sizes
   - Connection counts
   - Error rates in application logs

2. Create alerts for:
   - Failed migrations
   - Excessive migration duration
   - Application errors following migration

## Conclusion

Following this guide will help ensure safe and reliable PostgreSQL database migrations in production environments. The additional tools and procedures provided are designed to minimize risk and provide quick recovery options if issues occur.
