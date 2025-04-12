# LevyMaster Application Structure

## Overview

The LevyMaster application is built using the Flask web framework with a modular blueprint-based architecture. This document outlines the main components and their relationships.

## Core Files

- **main.py**: Entry point for the application. Imports the Flask app instance from app.py and starts the server.
- **app.py**: Main application factory that configures Flask, registers all blueprints, and sets up middleware.
- **wsgi.py**: WSGI entry point for production deployment. Imports the app from app.py.
- **models.py**: Contains SQLAlchemy model definitions for all database tables.
- **config.py**: Configuration settings for different environments (development, testing, production).

## Blueprints

The application is organized into functional blueprints:

- **routes_home.py**: Core routes including home page, dashboard, about, and settings.
- **routes_data_management.py**: Routes for managing tax district and property data.
- **routes_levy_calculator.py**: Levy calculation functionality.
- **routes_forecasting.py**: Tax forecasting and prediction tools.
- **routes_historical_analysis.py**: Historical data analysis features.
- **routes_mcp.py**: Multi-Agent Cognitive Process (MCP) framework integration.
- **routes_levy_exports.py**: Data export functionality.
- *Additional specialized blueprints for specific features*

## Templates

Templates are organized by blueprint in the templates directory:

```
templates/
├── index.html (main landing page)
├── dashboard.html
├── base.html (base template with common layout)
├── data_management/
│   ├── index.html
│   ├── tax_districts.html
│   └── ...
├── levy_calculator/
│   ├── index.html
│   ├── calculator.html
│   └── ...
└── ...
```

## Static Files

Static files (CSS, JavaScript, images) are in the static directory:

```
static/
├── css/
│   ├── main.css
│   └── ...
├── js/
│   ├── main.js
│   ├── charts.js
│   └── ...
└── images/
    └── ...
```

## Database

The application uses PostgreSQL with SQLAlchemy ORM. Tables include:

- TaxDistrict
- TaxCode
- Property
- ImportLog
- ExportLog
- UserActionLog
- LevyAuditRecord
- APICallLog

## AI Integration

The MCP (Multi-Agent Cognitive Process) framework provides AI capabilities through:

- **utils/anthropic_utils.py**: Integration with Anthropic's Claude API
- **utils/mcp_master_prompt.py**: Core prompt engineering for AI agents
- **routes_mcp.py**: API endpoints for MCP functionality
- **routes_mcp_army.py**: Advanced multi-agent system implementation

## Additional Notes

- This application uses Flask Blueprints for modularity and maintainability.
- Authentication is handled globally through Flask-Login.
- RESTful API patterns are used for data exchange.
- JavaScript is primarily for enhancing the UI rather than core functionality.
- The template system uses Jinja2 with inheritance for consistent layouts.