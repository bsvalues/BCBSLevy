/**
 * Mock error handler for testing
 */

import { Response } from 'express';
import { vi } from 'vitest';

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

export const handleError = vi.fn((error: unknown, res: Response, context: string = 'API') => {
  console.error(`Error in ${context}:`, error);
  
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
  
  return res.status(500).json({
    success: false,
    message: 'Internal server error',
    error: (error instanceof Error) ? error.message : String(error)
  });
});

export default handleError;