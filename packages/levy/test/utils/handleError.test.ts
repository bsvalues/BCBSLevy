import { describe, it, expect, vi, beforeEach } from 'vitest';
import { 
  handleError, 
  NotFoundError, 
  ValidationError, 
  AuthorizationError, 
  ConflictError 
} from '../../src/utils/handleError';
import { ZodError, z } from 'zod';

describe('handleError', () => {
  let res: any;
  
  beforeEach(() => {
    // Setup mock response object
    res = {
      status: vi.fn().mockReturnThis(),
      json: vi.fn().mockReturnThis()
    };
    
    // Mock console.error to avoid polluting test output
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });
  
  it('handles NotFoundError with 404 status', () => {
    const error = new NotFoundError('Resource not found');
    
    handleError(error, res);
    
    expect(res.status).toHaveBeenCalledWith(404);
    expect(res.json).toHaveBeenCalledWith({
      success: false,
      message: 'Resource not found'
    });
  });
  
  it('handles ValidationError with 400 status', () => {
    const error = new ValidationError('Invalid input');
    
    handleError(error, res);
    
    expect(res.status).toHaveBeenCalledWith(400);
    expect(res.json).toHaveBeenCalledWith({
      success: false,
      message: 'Invalid input'
    });
  });
  
  it('handles AuthorizationError with 403 status', () => {
    const error = new AuthorizationError('Access denied');
    
    handleError(error, res);
    
    expect(res.status).toHaveBeenCalledWith(403);
    expect(res.json).toHaveBeenCalledWith({
      success: false,
      message: 'Access denied'
    });
  });
  
  it('handles ConflictError with 409 status', () => {
    const error = new ConflictError('Resource already exists');
    
    handleError(error, res);
    
    expect(res.status).toHaveBeenCalledWith(409);
    expect(res.json).toHaveBeenCalledWith({
      success: false,
      message: 'Resource already exists'
    });
  });
  
  it('handles ZodError with 400 status and formatted errors', () => {
    const schema = z.object({
      name: z.string(),
      age: z.number().min(18)
    });
    
    let zodError;
    try {
      schema.parse({ name: 'Test', age: 16 });
    } catch (error) {
      zodError = error;
    }
    
    handleError(zodError, res);
    
    expect(res.status).toHaveBeenCalledWith(400);
    expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
      success: false,
      message: 'Validation error',
      errors: expect.any(Array)
    }));
  });
  
  it('handles unknown errors with 500 status', () => {
    const error = new Error('Unknown server error');
    
    // Set NODE_ENV to development for testing error message inclusion
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';
    
    handleError(error, res);
    
    expect(res.status).toHaveBeenCalledWith(500);
    expect(res.json).toHaveBeenCalledWith({
      success: false,
      message: 'Internal server error',
      error: 'Unknown server error'
    });
    
    // Restore original NODE_ENV
    process.env.NODE_ENV = originalEnv;
  });
  
  it('does not include error details in production', () => {
    const error = new Error('Secret error');
    
    // Set NODE_ENV to production
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'production';
    
    handleError(error, res);
    
    expect(res.status).toHaveBeenCalledWith(500);
    expect(res.json).toHaveBeenCalledWith({
      success: false,
      message: 'Internal server error',
      error: undefined
    });
    
    // Restore original NODE_ENV
    process.env.NODE_ENV = originalEnv;
  });
  
  it('includes context in error logging', () => {
    const error = new Error('Test error');
    const spy = vi.spyOn(console, 'error');
    
    handleError(error, res, 'TEST_CONTEXT');
    
    expect(spy).toHaveBeenCalledWith('Error in TEST_CONTEXT:', error);
  });
});