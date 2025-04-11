# Error Handling Guidelines

This document provides guidance on using the error handling framework for the LevyMaster application.

## Overview

The LevyMaster application implements a comprehensive error handling framework that provides:

- **Consistent Error Formatting**: Standardized error responses across the application
- **Custom Exception Types**: Domain-specific exception classes
- **Centralized Logging**: Unified approach to exception logging
- **Helpful Debugging**: Detailed error information in development
- **Security-Focused**: Limited error details in production

## Exception Hierarchy

The error handling framework defines a hierarchy of exception classes:

```
LevySystemException               # Base exception for all system exceptions
├── ValidationError               # Input validation errors
├── DataAccessError               # Database access errors
├── ApiError                      # External API errors
├── NotFoundError                 # Resource not found errors
└── AuthorizationError            # Permission and authorization errors
```

## How to Use the Error Handling Framework

### 1. Raising Exceptions

```python
from utils.error_handling import ValidationError, NotFoundError

# Validation error with field information
def validate_district(district_data):
    if not district_data.get('name'):
        raise ValidationError(
            message="District name is required",
            field="name"
        )

# Not found error with resource information
def get_tax_district(district_id):
    district = TaxDistrict.query.get(district_id)
    if not district:
        raise NotFoundError(
            message=f"Tax district {district_id} not found",
            resource_type="tax_district",
            resource_id=district_id
        )
    return district
```

### 2. Using Utility Functions

```python
from utils.error_handling import check_required_fields, check_resource_exists

# Check for required fields
def process_district_request(request_data):
    check_required_fields(
        request_data, 
        ['name', 'code', 'year'], 
        entity_name="tax district"
    )
    # Process valid request...

# Check if a resource exists
def update_tax_district(district_id, update_data):
    district = TaxDistrict.query.get(district_id)
    check_resource_exists(district, "tax_district", district_id)
    # Update existing district...
```

### 3. Using the Exception Handler Decorator

```python
from flask import Blueprint
from utils.error_handling import exception_handler

bp = Blueprint('tax_districts', __name__)

@bp.route('/<int:district_id>', methods=['GET'])
@exception_handler()
def get_district(district_id):
    district = TaxDistrict.query.get(district_id)
    if not district:
        raise NotFoundError(
            resource_type="tax_district",
            resource_id=district_id
        )
    return jsonify(district.to_dict())
```

### 4. Manual Exception Handling

```python
from utils.error_handling import handle_exception

@bp.route('/complex-operation', methods=['POST'])
def complex_operation():
    try:
        # Complex operation that might fail
        result = perform_complex_operation()
        return jsonify(result)
    except Exception as e:
        # Let the error handler format and return the response
        return handle_exception(e)
```

## Client Error Response Format

All error responses follow this JSON structure:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "name",
      "additional_info": "Some extra information"
    },
    "timestamp": "2025-04-11T15:30:00.000Z"
  }
}
```

## Error Codes

Common error codes used in the application:

| Error Code | Description | HTTP Status |
|------------|-------------|-------------|
| VALIDATION_ERROR | Input validation error | 400 |
| NOT_FOUND | Resource not found | 404 |
| AUTHORIZATION_ERROR | Not authorized for the operation | 403 |
| DATA_ACCESS_ERROR | Database access error | 500 |
| API_ERROR | External API error | 502 |
| SYSTEM_ERROR | General system error | 500 |
| UNEXPECTED_ERROR | Unhandled exception | 500 |

## Best Practices

### 1. Use Specific Exception Types

Choose the most specific exception type for the error condition. This helps with both error handling and client communication.

### 2. Include Helpful Error Messages

Error messages should be clear and actionable for both users and developers.

### 3. Provide Context in Details

Use the `details` field to provide additional context about the error, but be careful not to expose sensitive information.

### 4. Log Exceptions Appropriately

The framework automatically logs exceptions, but you can add additional context:

```python
from utils.error_handling import log_exception

try:
    # Complex operation
except Exception as e:
    log_exception(e, {"context": "batch_processing", "job_id": job_id})
    raise
```

### 5. Handle API Errors Gracefully

When calling external APIs, catch and wrap exceptions:

```python
from utils.error_handling import ApiError

try:
    response = requests.get("https://api.example.com/data")
    response.raise_for_status()
except requests.RequestException as e:
    raise ApiError(
        message="Failed to fetch data from external API",
        service="example_api",
        endpoint="/data",
        status_code=getattr(e.response, 'status_code', None),
        details={"original_error": str(e)}
    )
```

## Security Considerations

1. **Sanitize Error Messages**: Ensure error messages don't contain sensitive information
2. **Limit Stack Traces**: Full stack traces are only included in development mode
3. **Consistent Status Codes**: Use appropriate HTTP status codes for errors