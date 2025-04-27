/**
 * API Response Formatter
 * 
 * Standardizes API responses across all endpoints to ensure consistent structure.
 */

import { Response } from 'express';

/**
 * Interface for pagination metadata
 */
export interface PaginationMetadata {
  page: number;
  limit: number;
  totalItems: number;
  totalPages: number;
}

/**
 * Interface for successful API response
 */
export interface SuccessResponse<T> {
  success: true;
  data: T;
  message?: string;
  pagination?: PaginationMetadata;
}

/**
 * Interface for error API response
 */
export interface ErrorResponse {
  success: false;
  message: string;
  errors?: any[];
}

/**
 * Union type for all API responses
 */
export type ApiResponse<T> = SuccessResponse<T> | ErrorResponse;

/**
 * Returns a success response with optional message and pagination
 * 
 * @param data - The data to be returned
 * @param message - Optional success message
 * @param pagination - Optional pagination metadata
 * @param status - HTTP status code (default: 200)
 */
export const successResponse = <T>(
  res: Response, 
  data: T, 
  message?: string, 
  pagination?: PaginationMetadata,
  status: number = 200
): Response => {
  const response: SuccessResponse<T> = {
    success: true,
    data
  };
  
  if (message) {
    response.message = message;
  }
  
  if (pagination) {
    response.pagination = pagination;
  }
  
  return res.status(status).json(response);
};

/**
 * Returns an error response
 * 
 * @param message - Error message
 * @param errors - Optional array of detailed errors
 * @param status - HTTP status code (default: 400)
 */
export const errorResponse = (
  res: Response, 
  message: string, 
  errors?: any[], 
  status: number = 400
): Response => {
  const response: ErrorResponse = {
    success: false,
    message
  };
  
  if (errors) {
    response.errors = errors;
  }
  
  return res.status(status).json(response);
};

/**
 * Returns a created response (201)
 * 
 * @param data - The created resource
 * @param message - Optional success message
 */
export const createdResponse = <T>(
  res: Response, 
  data: T, 
  message: string = 'Resource created successfully'
): Response => {
  return successResponse(res, data, message, undefined, 201);
};

/**
 * Returns a no content response (204)
 */
export const noContentResponse = (res: Response): Response => {
  return res.status(204).send();
};

/**
 * Returns a paginated list response
 * 
 * @param data - Array of items
 * @param pagination - Pagination metadata
 * @param message - Optional success message
 */
export const paginatedResponse = <T>(
  res: Response,
  data: T[],
  pagination: PaginationMetadata,
  message?: string
): Response => {
  return successResponse(res, data, message, pagination);
};

/**
 * Factory function to create response helpers bound to a response object
 * 
 * @param res - Express response object
 */
export const createResponseFormatter = (res: Response) => {
  return {
    success: <T>(data: T, message?: string, status: number = 200) => 
      successResponse(res, data, message, undefined, status),
      
    error: (message: string, errors?: any[], status: number = 400) => 
      errorResponse(res, message, errors, status),
      
    created: <T>(data: T, message?: string) => 
      createdResponse(res, data, message),
      
    noContent: () => noContentResponse(res),
    
    paginated: <T>(data: T[], pagination: PaginationMetadata, message?: string) => 
      paginatedResponse(res, data, pagination, message)
  };
};

export default createResponseFormatter;