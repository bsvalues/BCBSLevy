# API Documentation

This document provides detailed information about the API endpoints available in the SaaS Levy Calculation Application.

## Core Routes

### Dashboard

- **URL**: `/`
- **Method**: `GET`
- **Description**: Renders the main dashboard with overview statistics
- **Response**: HTML page with property count, tax code count, district count, recent imports, and exports

### Import Data

- **URL**: `/import`
- **Method**: `GET`, `POST`
- **Description**: Page for importing property data via CSV file upload
- **Request Body** (POST - multipart/form-data):
  - `file`: CSV file with property data (required)
- **Response**: Redirects to dashboard on success, or displays errors

### District Import

- **URL**: `/district-import`
- **Method**: `GET`, `POST`
- **Description**: Page for importing tax district data via file upload
- **Request Body** (POST - multipart/form-data):
  - `file`: TXT, XML, or Excel file with district data (required)
- **Response**: Redirects to districts page on success, or displays errors

### Districts

- **URL**: `/districts`
- **Method**: `GET`
- **Description**: View and manage tax districts
- **Query Parameters**:
  - `page`: Page number for pagination (default: 1)
  - `year`: Filter by year (optional)
  - `district_id`: Filter by district ID (optional)
  - `levy_code`: Filter by levy code (optional)
- **Response**: HTML page with paginated districts and filter controls

### Levy Calculator

- **URL**: `/levy-calculator`
- **Method**: `GET`, `POST`
- **Description**: Calculate levy rates based on levy amounts
- **Request Body** (POST - form):
  - `levy_amount_{tax_code}`: Levy amount for each tax code (optional)
- **Response**: HTML page with calculated levy rates and AI insights

### Reports

- **URL**: `/reports`
- **Method**: `GET`, `POST`
- **Description**: Generate and download tax roll reports
- **Response** (POST): CSV file download for tax roll report

### Property Lookup

- **URL**: `/property-lookup`
- **Method**: `GET`, `POST`
- **Description**: Look up property tax details by property ID
- **Request Body** (POST - form):
  - `property_id`: Property ID to look up (required)
- **Response**: HTML page with property details, tax calculation, and AI insights

### MCP Insights

- **URL**: `/mcp-insights`
- **Method**: `GET`
- **Description**: Display Model Content Protocol (MCP) insights and AI capabilities
- **Response**: HTML page with AI analysis, statistics, and visualization

## API Endpoints

### Tax Codes

- **URL**: `/api/tax-codes`
- **Method**: `GET`
- **Description**: Get tax code information for charts and analysis
- **Response Format**: JSON
- **Response Example**:
  ```json
  {
    "tax_codes": [
      {
        "code": "00120",
        "levy_rate": 3.45,
        "total_assessed_value": 5000000,
        "property_count": 25
      },
      ...
    ]
  }
  ```

### District Summary

- **URL**: `/api/district-summary`
- **Method**: `GET`
- **Description**: Get district summary for current year
- **Response Format**: JSON
- **Response Example**:
  ```json
  {
    "districts": [
      {
        "tax_district_id": 123,
        "year": 2023,
        "levy_code": "00120",
        "linked_levy_codes": ["00121", "00122"]
      },
      ...
    ],
    "year": 2023
  }
  ```

## MCP API Endpoints

These endpoints are part of the Model Content Protocol (MCP) framework for AI integration.

### MCP Functions

- **URL**: `/api/mcp/functions`
- **Method**: `GET`
- **Description**: List all available MCP functions
- **Response Format**: JSON
- **Response Example**:
  ```json
  {
    "functions": [
      {
        "name": "analyze_tax_distribution",
        "description": "Analyze distribution of tax burden across properties",
        "parameters": []
      },
      ...
    ]
  }
  ```

### MCP Workflows

- **URL**: `/api/mcp/workflows`
- **Method**: `GET`
- **Description**: List all available MCP workflows
- **Response Format**: JSON
- **Response Example**:
  ```json
  {
    "workflows": [
      {
        "name": "tax_distribution_analysis",
        "description": "Analyze tax distribution and generate insights",
        "steps": ["analyze_tax_distribution", "generate_insights"]
      },
      ...
    ]
  }
  ```

### MCP Agents

- **URL**: `/api/mcp/agents`
- **Method**: `GET`
- **Description**: List all available MCP agents
- **Response Format**: JSON
- **Response Example**:
  ```json
  {
    "agents": [
      {
        "name": "LevyAnalysisAgent",
        "description": "Analyzes levy rates and assessed values",
        "functions": ["analyze_levy_rates", "compare_assessed_values"]
      },
      ...
    ]
  }
  ```

### Execute MCP Function

- **URL**: `/api/mcp/function/execute`
- **Method**: `POST`
- **Description**: Execute an MCP function
- **Request Body**:
  ```json
  {
    "function": "analyze_tax_distribution",
    "parameters": {}
  }
  ```
- **Response Format**: JSON
- **Response Example**:
  ```json
  {
    "result": {
      "analysis": "Tax distribution analysis complete.",
      "data": {}
    }
  }
  ```

### Execute MCP Workflow

- **URL**: `/api/mcp/workflow/execute`
- **Method**: `POST`
- **Description**: Execute an MCP workflow
- **Request Body**:
  ```json
  {
    "workflow": "tax_distribution_analysis",
    "parameters": {}
  }
  ```
- **Response Format**: JSON
- **Response Example**:
  ```json
  {
    "result": {
      "status": "completed",
      "steps": ["analyze_tax_distribution", "generate_insights"],
      "outputs": {}
    }
  }
  ```

### Send Request to MCP Agent

- **URL**: `/api/mcp/agent/request`
- **Method**: `POST`
- **Description**: Send a request to an MCP agent
- **Request Body**:
  ```json
  {
    "agent": "LevyAnalysisAgent",
    "request": "analyze_levy_rates",
    "parameters": {}
  }
  ```
- **Response Format**: JSON
- **Response Example**:
  ```json
  {
    "result": {
      "response": "Levy rate analysis complete.",
      "data": {}
    }
  }
  ```

## Error Responses

All API endpoints return standard HTTP status codes:

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include a JSON body with error details:

```json
{
  "error": "true",
  "message": "Error message description",
  "details": {}
}
```
