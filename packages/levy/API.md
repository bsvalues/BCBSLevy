# TerraFusion Levy Management API Documentation

This document provides comprehensive documentation for the TerraFusion Levy Management API endpoints, request/response formats, and error handling.

## API Base URL

All API endpoints are relative to: `/api`

## Authentication

All API endpoints require authentication. The API uses a token-based authentication system.

### Request Headers

```
Authorization: Bearer <token>
```

> Note: In the development environment, a mock authentication middleware is used that automatically authenticates all requests.

## Response Format

All API responses follow a consistent structure:

### Success Response

```json
{
  "success": true,
  "data": <response data>,
  "pagination": {
    "page": 1,
    "limit": 20,
    "totalItems": 100,
    "totalPages": 5
  } // Only included for paginated endpoints
}
```

### Error Response

```json
{
  "success": false,
  "message": "Error message",
  "errors": [
    {
      "path": ["field"],
      "message": "Specific error message"
    }
  ] // Validation errors, if applicable
}
```

## Status Codes

- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully
- `204 No Content`: Request succeeded (no content returned)
- `400 Bad Request`: Invalid request or validation error
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Levy Endpoints

### List Levies

Retrieves a paginated list of levies with optional filtering.

- **URL**: `/levies`
- **Method**: `GET`
- **Auth Required**: Yes

#### Query Parameters

| Parameter     | Type     | Required | Description                                           |
|---------------|----------|----------|-------------------------------------------------------|
| name          | string   | No       | Filter by levy name (case-insensitive partial match)  |
| taxYear       | number   | No       | Filter by tax year                                    |
| taxDistrictId | number   | No       | Filter by tax district ID                             |
| status        | string   | No       | Filter by status (draft, submitted, approved, rejected, archived) |
| page          | number   | No       | Page number (default: 1)                              |
| limit         | number   | No       | Results per page (default: 20, max: 100)              |
| sortBy        | string   | No       | Field to sort by (default: name)                      |
| sortDir       | string   | No       | Sort direction (asc or desc, default: asc)            |

#### Sample Response

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "School District Levy 2025",
      "description": "Annual levy for school district operations",
      "taxYear": 2025,
      "taxDistrictId": 42,
      "taxCodeId": 123,
      "levyAmount": 5000000,
      "levyRate": 0.0125,
      "assessedValue": 400000000,
      "status": "approved",
      "createdAt": "2025-01-15T14:30:00Z",
      "taxDistrict": {
        "id": 42,
        "name": "Central School District"
      },
      "taxCode": {
        "id": 123,
        "code": "SD001",
        "levyRate": 0.0125
      }
    }
    // Additional results...
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "totalItems": 45,
    "totalPages": 3
  }
}
```

### Get Levy

Retrieves a specific levy by ID.

- **URL**: `/levies/:id`
- **Method**: `GET`
- **Auth Required**: Yes

#### URL Parameters

| Parameter | Type     | Required | Description  |
|-----------|----------|----------|--------------|
| id        | number   | Yes      | Levy ID      |

#### Sample Response

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "School District Levy 2025",
    "description": "Annual levy for school district operations",
    "taxYear": 2025,
    "taxDistrictId": 42,
    "taxCodeId": 123,
    "levyAmount": 5000000,
    "levyRate": 0.0125,
    "assessedValue": 400000000,
    "newConstructionValue": 15000000,
    "annexationValue": 0,
    "priorYearLevyAmount": 4850000,
    "status": "approved",
    "calculationMethod": "standard",
    "isApproved": true,
    "approvedById": 5,
    "approvedAt": "2025-03-10T09:45:00Z",
    "createdAt": "2025-01-15T14:30:00Z",
    "updatedAt": "2025-03-10T09:45:00Z",
    "createdById": 3,
    "updatedById": 5,
    "metadata": {
      "notes": "Approved by board on March 9, 2025"
    },
    "taxDistrict": {
      "id": 42,
      "name": "Central School District",
      "countyName": "Benton County",
      "stateName": "Washington",
      "districtType": "SCHOOL"
    },
    "taxCode": {
      "id": 123,
      "code": "SD001",
      "name": "School District Tax",
      "levyRate": 0.0125,
      "totalAssessedValue": 400000000
    },
    "createdBy": {
      "id": 3,
      "username": "jsmith",
      "firstName": "John",
      "lastName": "Smith"
    },
    "approvedBy": {
      "id": 5,
      "username": "mjohnson",
      "firstName": "Mary",
      "lastName": "Johnson"
    }
  }
}
```

### Create Levy

Creates a new levy.

- **URL**: `/levies`
- **Method**: `POST`
- **Auth Required**: Yes
- **Content-Type**: `application/json`

#### Request Body

```json
{
  "name": "School District Levy 2025",
  "description": "Annual levy for school district operations",
  "taxYear": 2025,
  "taxDistrictId": 42,
  "taxCodeId": 123,
  "levyAmount": 5000000,
  "levyRate": 0.0125,
  "assessedValue": 400000000,
  "newConstructionValue": 15000000,
  "annexationValue": 0,
  "priorYearLevyAmount": 4850000,
  "status": "draft",
  "calculationMethod": "standard",
  "metadata": {
    "notes": "Initial draft for board review"
  }
}
```

#### Sample Response

```json
{
  "success": true,
  "message": "Levy created successfully",
  "data": {
    "id": 1,
    "name": "School District Levy 2025",
    "description": "Annual levy for school district operations",
    "taxYear": 2025,
    "taxDistrictId": 42,
    "taxCodeId": 123,
    "levyAmount": 5000000,
    "levyRate": 0.0125,
    "assessedValue": 400000000,
    "newConstructionValue": 15000000,
    "annexationValue": 0,
    "priorYearLevyAmount": 4850000,
    "status": "draft",
    "calculationMethod": "standard",
    "isApproved": false,
    "createdAt": "2025-01-15T14:30:00Z",
    "updatedAt": "2025-01-15T14:30:00Z",
    "createdById": 3,
    "updatedById": 3,
    "metadata": {
      "notes": "Initial draft for board review"
    }
  }
}
```

### Update Levy

Updates an existing levy.

- **URL**: `/levies/:id`
- **Method**: `PUT`
- **Auth Required**: Yes
- **Content-Type**: `application/json`

#### URL Parameters

| Parameter | Type     | Required | Description  |
|-----------|----------|----------|--------------|
| id        | number   | Yes      | Levy ID      |

#### Request Body

```json
{
  "name": "Updated School District Levy 2025",
  "description": "Updated description for annual levy",
  "status": "submitted",
  "metadata": {
    "notes": "Updated for board review",
    "submittedBy": "John Smith"
  }
}
```

#### Sample Response

```json
{
  "success": true,
  "message": "Levy updated successfully",
  "data": {
    "id": 1,
    "name": "Updated School District Levy 2025",
    "description": "Updated description for annual levy",
    "taxYear": 2025,
    "taxDistrictId": 42,
    "taxCodeId": 123,
    "levyAmount": 5000000,
    "levyRate": 0.0125,
    "assessedValue": 400000000,
    "status": "submitted",
    "createdAt": "2025-01-15T14:30:00Z",
    "updatedAt": "2025-01-16T10:45:00Z",
    "metadata": {
      "notes": "Updated for board review",
      "submittedBy": "John Smith"
    }
  }
}
```

### Delete Levy

Deletes a levy. Only non-approved levies can be deleted.

- **URL**: `/levies/:id`
- **Method**: `DELETE`
- **Auth Required**: Yes

#### URL Parameters

| Parameter | Type     | Required | Description  |
|-----------|----------|----------|--------------|
| id        | number   | Yes      | Levy ID      |

#### Sample Response

Status: 204 No Content

---

## Error Examples

### Invalid Input (400 Bad Request)

```json
{
  "success": false,
  "message": "Invalid levy data",
  "errors": [
    {
      "path": ["name"],
      "message": "Name must be at least 3 characters long"
    },
    {
      "path": ["taxYear"],
      "message": "Tax year must be a positive integer"
    }
  ]
}
```

### Resource Not Found (404 Not Found)

```json
{
  "success": false,
  "message": "Levy not found"
}
```

### Permission Denied (403 Forbidden)

```json
{
  "success": false,
  "message": "Cannot delete an approved levy. Consider archiving it instead."
}
```