# Deployment Guide

This guide explains how to deploy the Levy Calculation Application to production using Replit.

## Prerequisites

Before deploying, make sure you have:

1. Applied all database migrations to your production database
2. Set all required environment variables
3. Tested the application in development mode

## Environment Configuration

The following environment variables should be set for production:

- `FLASK_ENV=production`: Sets the application to run in production mode
- `SESSION_SECRET`: A secure random string for session encryption
- `DATABASE_URL`: PostgreSQL connection string for the production database
- `ANTHROPIC_API_KEY`: API key for Anthropic Claude AI services

## Deployment Steps

### 1. Update Workflow Configuration

Update your Replit configuration to use the production WSGI entry point:

1. In the `.replit` file, update the deployment run command:

   ```
   [deployment]
   deploymentTarget = "autoscale"
   run = ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
   ```

2. Set the production environment variable:

   ```
   [env]
   FLASK_ENV = "production"
   ```

3. Add database migration workflows:

   ```
   [[workflows.workflow]]
   name = "DB Migration Init"
   author = "agent"

   [[workflows.workflow.tasks]]
   task = "shell.exec"
   args = "python migrate.py init"

   [[workflows.workflow]]
   name = "DB Migration Generate"
   author = "agent"

   [[workflows.workflow.tasks]]
   task = "shell.exec"
   args = "python migrate.py migrate"

   [[workflows.workflow]]
   name = "DB Migration Apply"
   author = "agent"

   [[workflows.workflow.tasks]]
   task = "shell.exec"
   args = "python migrate.py upgrade"
   ```

### 2. Apply Database Migrations

Before deploying, ensure all database migrations are applied:

```bash
python migrate.py upgrade
```

### 3. Deploy the Application

Use the Replit deployment interface to deploy the application:

1. Click the "Deploy" button in the Replit interface
2. Select "Deploy to Production" in the deployment dialog
3. Wait for the deployment to complete
4. Once deployed, your application will be available at your Replit domain

## Post-Deployment Verification

After deployment, verify that:

1. The application is accessible at your production URL
2. All features are working as expected
3. Database connections are properly established
4. Logging is correctly configured

## Rollback Procedure

If issues are discovered after deployment:

1. Identify the nature of the issue
2. If it's a database migration issue:
   ```bash
   python migrate.py downgrade
   ```
3. If it's a code issue:
   - Fix the issue in development
   - Test thoroughly
   - Re-deploy

## Production Maintenance

### Database Backups

Regularly back up your production database:

```bash
pg_dump -Fc $DATABASE_URL > backup-$(date +%Y-%m-%d).dump
```

### Log Monitoring

Monitor your application logs for errors and unusual activity:

```bash
python tools/log_analyzer.py
```

### Performance Monitoring

Regularly check the application's performance metrics and optimize as needed.

## Scaling Considerations

The application is designed to scale horizontally. When traffic increases:

1. Increase the number of worker processes in Gunicorn:

   ```
   gunicorn --bind 0.0.0.0:5000 --workers=4 wsgi:app
   ```

2. Consider implementing a caching layer for frequently accessed data

3. Optimize database queries for high load scenarios
