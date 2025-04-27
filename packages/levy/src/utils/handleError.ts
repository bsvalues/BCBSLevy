/**
 * Error Handler Utility
 * 
 * Standardizes error handling across API endpoints and provides consistent error responses.
 */

import { Response } from 'express';
import { ZodError } from 'zod';

// Define custom error types
export class NotFoundError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'NotFoundError';
  }
}

export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class AuthorizationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AuthorizationError';
  }
}

export class ConflictError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ConflictError';
  }
}

/**
 * Formats a ZodError into a more user-friendly structure
 */
const formatZodError = (error: ZodError) => {
  return error.errors.map(err => ({
    path: err.path,
    message: err.message
  }));
};

/**
 * Standardized error handler for API routes
 * 
 * @param error - The caught error
 * @param res - Express response object
 * @param context - Additional context for logging (optional)
 */
export const handleError = (error: unknown, res: Response, context: string = 'API'): Response => {
  console.error(`Error in ${context}:`, error);
  
  // Handle specific error types
  if (error instanceof NotFoundError) {
    return res.status(404).json({
      success: false,
      message: error.message
    });
  }
  
  if (error instanceof ValidationError) {
    return res.status(400).json({
      success: false,
      message: error.message
    });
  }
  
  if (error instanceof AuthorizationError) {
    return res.status(403).json({
      success: false,
      message: error.message
    });
  }
  
  if (error instanceof ConflictError) {
    return res.status(409).json({
      success: false,
      message: error.message
    });
  }
  
  // Handle Zod validation errors
  if (error instanceof ZodError) {
    return res.status(400).json({
      success: false,
      message: 'Validation error',
      errors: formatZodError(error)
    });
  }
  
  // For database or other specific errors, we could add more handlers here
  
  // Fallback for unknown errors
  return res.status(500).json({
    success: false,
    message: 'Internal server error',
    error: process.env.NODE_ENV === 'development' ? (error instanceof Error ? error.message : String(error)) : undefined
  });
};

export default handleError;