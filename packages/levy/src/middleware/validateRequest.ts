/**
 * Request Validation Middleware
 * 
 * Validates request body, params, and query using Zod schemas
 */

import { Request, Response, NextFunction } from 'express';
import { z, ZodSchema } from 'zod';
import { handleError } from '../utils/handleError';

export interface ValidationOptions {
  body?: ZodSchema;
  params?: ZodSchema;
  query?: ZodSchema;
}

/**
 * Middleware factory that creates a validation middleware for different parts of the request
 * 
 * @param schemas - Object containing Zod schemas for body, params, and/or query
 */
export const validateRequest = (schemas: ValidationOptions) => {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      // Validate request body if schema provided
      if (schemas.body) {
        const validatedBody = schemas.body.parse(req.body);
        // Replace request body with validated data
        req.body = validatedBody;
      }
      
      // Validate URL parameters if schema provided
      if (schemas.params) {
        const validatedParams = schemas.params.parse(req.params);
        // Replace request params with validated data
        req.params = validatedParams;
      }
      
      // Validate query string if schema provided
      if (schemas.query) {
        const validatedQuery = schemas.query.parse(req.query);
        // Replace request query with validated data
        req.query = validatedQuery;
      }
      
      // All validations passed, proceed to next middleware/handler
      next();
    } catch (error) {
      // Handle validation errors
      handleError(error, res, 'Request validation');
    }
  };
};

/**
 * Common validation schemas that can be reused across routes
 */
export const commonValidations = {
  // Pagination params validation
  pagination: z.object({
    page: z.coerce.number().int().positive().optional().default(1),
    limit: z.coerce.number().int().positive().max(100).optional().default(20)
  }),
  
  // ID parameter validation
  idParam: z.object({
    id: z.coerce.number().int().positive()
  }),
  
  // Sorting validation
  sorting: z.object({
    sortBy: z.string().optional(),
    sortDir: z.enum(['asc', 'desc']).optional().default('asc')
  })
};

export default validateRequest;