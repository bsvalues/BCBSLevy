/**
 * OpenAPI Documentation Generator
 * 
 * Generates OpenAPI specification for the API endpoints.
 */

import { Express } from 'express';
import { OpenAPIObject, PathItemObject } from 'openapi3-ts';
import * as packageJson from '../../package.json';

/**
 * Basic OpenAPI configuration
 */
interface OpenApiConfig {
  title: string;
  description: string;
  version: string;
  baseUrl: string;
}

/**
 * Generates an OpenAPI specification for the API
 * 
 * @param app - Express application
 * @param config - OpenAPI configuration
 * @returns OpenAPI specification object
 */
export const generateOpenApi = (app: Express, config: OpenApiConfig): OpenAPIObject => {
  const defaultConfig: OpenApiConfig = {
    title: 'TerraFusion Levy Management API',
    description: 'API for managing tax levies, tax districts, and properties',
    version: packageJson.version || '1.0.0',
    baseUrl: '/api'
  };
  
  const mergedConfig = { ...defaultConfig, ...config };
  
  // Create base OpenAPI specification
  const openApiSpec: OpenAPIObject = {
    openapi: '3.0.3',
    info: {
      title: mergedConfig.title,
      description: mergedConfig.description,
      version: mergedConfig.version,
      contact: {
        name: 'TerraFusion Support',
        url: 'https://terrafusion.io/support',
        email: 'support@terrafusion.io'
      },
      license: {
        name: 'MIT',
        url: 'https://opensource.org/licenses/MIT'
      }
    },
    servers: [
      {
        url: mergedConfig.baseUrl,
        description: 'API Server'
      }
    ],
    paths: {},
    components: {
      schemas: {
        // Common response models
        SuccessResponse: {
          type: 'object',
          required: ['success', 'data'],
          properties: {
            success: {
              type: 'boolean',
              example: true
            },
            data: {
              type: 'object'
            },
            message: {
              type: 'string',
              example: 'Operation successful'
            }
          }
        },
        ErrorResponse: {
          type: 'object',
          required: ['success', 'message'],
          properties: {
            success: {
              type: 'boolean',
              example: false
            },
            message: {
              type: 'string',
              example: 'An error occurred'
            },
            errors: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  path: {
                    type: 'array',
                    items: {
                      type: 'string'
                    }
                  },
                  message: {
                    type: 'string'
                  }
                }
              }
            }
          }
        },
        PaginationMetadata: {
          type: 'object',
          required: ['page', 'limit', 'totalItems', 'totalPages'],
          properties: {
            page: {
              type: 'integer',
              example: 1
            },
            limit: {
              type: 'integer',
              example: 20
            },
            totalItems: {
              type: 'integer',
              example: 100
            },
            totalPages: {
              type: 'integer',
              example: 5
            }
          }
        },
        PaginatedResponse: {
          type: 'object',
          required: ['success', 'data', 'pagination'],
          properties: {
            success: {
              type: 'boolean',
              example: true
            },
            data: {
              type: 'array',
              items: {
                type: 'object'
              }
            },
            message: {
              type: 'string',
              example: 'Items retrieved successfully'
            },
            pagination: {
              $ref: '#/components/schemas/PaginationMetadata'
            }
          }
        },
        
        // Domain models
        Levy: {
          type: 'object',
          properties: {
            id: {
              type: 'integer',
              example: 1
            },
            name: {
              type: 'string',
              example: 'School District Levy 2025'
            },
            description: {
              type: 'string',
              example: 'Annual levy for school district operations'
            },
            taxYear: {
              type: 'integer',
              example: 2025
            },
            taxDistrictId: {
              type: 'integer',
              example: 42
            },
            taxCodeId: {
              type: 'integer',
              example: 123
            },
            levyAmount: {
              type: 'number',
              format: 'double',
              example: 5000000
            },
            levyRate: {
              type: 'number',
              format: 'double',
              example: 0.0125
            },
            status: {
              type: 'string',
              enum: ['draft', 'submitted', 'approved', 'rejected', 'archived'],
              example: 'approved'
            },
            createdAt: {
              type: 'string',
              format: 'date-time'
            },
            updatedAt: {
              type: 'string',
              format: 'date-time'
            }
          }
        },
        TaxDistrict: {
          type: 'object',
          properties: {
            id: {
              type: 'integer',
              example: 1
            },
            name: {
              type: 'string',
              example: 'Central School District'
            },
            districtType: {
              type: 'string',
              example: 'SCHOOL'
            },
            countyName: {
              type: 'string',
              example: 'Benton County'
            },
            stateName: {
              type: 'string',
              example: 'Washington'
            },
            isActive: {
              type: 'boolean',
              example: true
            }
          }
        },
        TaxCode: {
          type: 'object',
          properties: {
            id: {
              type: 'integer',
              example: 1
            },
            code: {
              type: 'string',
              example: 'SD001'
            },
            name: {
              type: 'string',
              example: 'School District Tax'
            },
            levyRate: {
              type: 'number',
              format: 'double',
              example: 0.0125
            },
            totalAssessedValue: {
              type: 'number',
              format: 'double',
              example: 400000000
            },
            isActive: {
              type: 'boolean',
              example: true
            }
          }
        },
        Property: {
          type: 'object',
          properties: {
            id: {
              type: 'integer',
              example: 1
            },
            parcelNumber: {
              type: 'string',
              example: '12345678900'
            },
            address: {
              type: 'string',
              example: '123 Main St, Richland, WA 99352'
            },
            ownerName: {
              type: 'string',
              example: 'John Doe'
            },
            assessedValue: {
              type: 'number',
              format: 'double',
              example: 250000
            },
            taxCodeId: {
              type: 'integer',
              example: 123
            }
          }
        },
        User: {
          type: 'object',
          properties: {
            id: {
              type: 'integer',
              example: 1
            },
            username: {
              type: 'string',
              example: 'jsmith'
            },
            email: {
              type: 'string',
              format: 'email',
              example: 'jsmith@example.com'
            },
            firstName: {
              type: 'string',
              example: 'John'
            },
            lastName: {
              type: 'string',
              example: 'Smith'
            },
            isAdmin: {
              type: 'boolean',
              example: false
            },
            isActive: {
              type: 'boolean',
              example: true
            }
          }
        }
      },
      securitySchemes: {
        BearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT'
        }
      }
    },
    security: [
      {
        BearerAuth: []
      }
    ]
  };
  
  // Build the API paths
  const paths: Record<string, PathItemObject> = {
    '/levies': {
      get: {
        summary: 'Get all levies',
        description: 'Retrieves a paginated list of levies with optional filtering.',
        tags: ['Levies'],
        parameters: [
          {
            name: 'page',
            in: 'query',
            schema: {
              type: 'integer',
              default: 1,
              minimum: 1
            },
            description: 'Page number'
          },
          {
            name: 'limit',
            in: 'query',
            schema: {
              type: 'integer',
              default: 20,
              minimum: 1,
              maximum: 100
            },
            description: 'Number of items per page'
          },
          {
            name: 'sortBy',
            in: 'query',
            schema: {
              type: 'string',
              default: 'taxYear',
              enum: ['name', 'taxYear', 'levyAmount', 'levyRate', 'status', 'createdAt']
            },
            description: 'Field to sort by'
          },
          {
            name: 'sortDir',
            in: 'query',
            schema: {
              type: 'string',
              default: 'desc',
              enum: ['asc', 'desc']
            },
            description: 'Sort direction'
          },
          {
            name: 'name',
            in: 'query',
            schema: {
              type: 'string'
            },
            description: 'Filter by levy name (case-insensitive partial match)'
          },
          {
            name: 'taxYear',
            in: 'query',
            schema: {
              type: 'integer'
            },
            description: 'Filter by tax year'
          },
          {
            name: 'status',
            in: 'query',
            schema: {
              type: 'string',
              enum: ['draft', 'submitted', 'approved', 'rejected', 'archived']
            },
            description: 'Filter by status'
          }
        ],
        responses: {
          '200': {
            description: 'Successful operation',
            content: {
              'application/json': {
                schema: {
                  allOf: [
                    { $ref: '#/components/schemas/PaginatedResponse' },
                    {
                      properties: {
                        data: {
                          type: 'array',
                          items: {
                            $ref: '#/components/schemas/Levy'
                          }
                        }
                      }
                    }
                  ]
                }
              }
            }
          },
          '400': {
            description: 'Bad request',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/ErrorResponse'
                }
              }
            }
          },
          '401': {
            description: 'Unauthorized',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/ErrorResponse'
                }
              }
            }
          },
          '500': {
            description: 'Internal server error',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/ErrorResponse'
                }
              }
            }
          }
        }
      },
      post: {
        summary: 'Create a new levy',
        description: 'Creates a new levy record.',
        tags: ['Levies'],
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/Levy'
              }
            }
          }
        },
        responses: {
          '201': {
            description: 'Levy created successfully',
            content: {
              'application/json': {
                schema: {
                  allOf: [
                    { $ref: '#/components/schemas/SuccessResponse' },
                    {
                      properties: {
                        data: {
                          $ref: '#/components/schemas/Levy'
                        }
                      }
                    }
                  ]
                }
              }
            }
          },
          '400': {
            description: 'Bad request',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/ErrorResponse'
                }
              }
            }
          },
          '401': {
            description: 'Unauthorized',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/ErrorResponse'
                }
              }
            }
          },
          '500': {
            description: 'Internal server error',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/ErrorResponse'
                }
              }
            }
          }
        }
      }
    },
    '/levies/{id}': {
      get: {
        summary: 'Get levy by ID',
        description: 'Retrieves a specific levy by its ID.',
        tags: ['Levies'],
        parameters: [
          {
            name: 'id',
            in: 'path',
            required: true,
            schema: {
              type: 'integer',
              format: 'int64'
            },
            description: 'Levy ID'
          }
        ],
        responses: {
          '200': {
            description: 'Successful operation',
            content: {
              'application/json': {
                schema: {
                  allOf: [
                    { $ref: '#/components/schemas/SuccessResponse' },
                    {
                      properties: {
                        data: {
                          $ref: '#/components/schemas/Levy'
                        }
                      }
                    }
                  ]
                }
              }
            }
          },
          '404': {
            description: 'Levy not found',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/ErrorResponse'
                }
              }
            }
          }
        }
      },
      put: {
        summary: 'Update levy',
        description: 'Updates an existing levy.',
        tags: ['Levies'],
        parameters: [
          {
            name: 'id',
            in: 'path',
            required: true,
            schema: {
              type: 'integer',
              format: 'int64'
            },
            description: 'Levy ID'
          }
        ],
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/Levy'
              }
            }
          }
        },
        responses: {
          '200': {
            description: 'Levy updated successfully',
            content: {
              'application/json': {
                schema: {
                  allOf: [
                    { $ref: '#/components/schemas/SuccessResponse' },
                    {
                      properties: {
                        data: {
                          $ref: '#/components/schemas/Levy'
                        }
                      }
                    }
                  ]
                }
              }
            }
          },
          '400': {
            description: 'Bad request',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/ErrorResponse'
                }
              }
            }
          },
          '401': {
            description: 'Unauthorized',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/ErrorResponse'
                }
              }
            }
          },
          '403': {
            description: 'Forbidden',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/ErrorResponse'
                }
              }
            }
          },
          '404': {
            description: 'Levy not found',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/ErrorResponse'
                }
              }
            }
          }
        }
      },
      delete: {
        summary: 'Delete levy',
        description: 'Deletes a levy. Only non-approved levies can be deleted.',
        tags: ['Levies'],
        parameters: [
          {
            name: 'id',
            in: 'path',
            required: true,
            schema: {
              type: 'integer',
              format: 'int64'
            },
            description: 'Levy ID'
          }
        ],
        responses: {
          '204': {
            description: 'Levy deleted successfully'
          },
          '401': {
            description: 'Unauthorized',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/ErrorResponse'
                }
              }
            }
          },
          '403': {
            description: 'Forbidden',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/ErrorResponse'
                }
              }
            }
          },
          '404': {
            description: 'Levy not found',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/ErrorResponse'
                }
              }
            }
          }
        }
      }
    }
  };
  
  // Add API paths to the specification
  openApiSpec.paths = paths;
  
  return openApiSpec;
};

export default generateOpenApi;