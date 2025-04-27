/**
 * Mock response formatter for testing
 */

import { Response } from 'express';
import { vi } from 'vitest';

type ApiResponse<T> = {
  success: boolean;
  message?: string;
  data?: T;
  meta?: Record<string, any>;
};

type ResponseFormatter = {
  success: <T>(data: T, message?: string, meta?: Record<string, any>) => Response;
  created: <T>(data: T, message?: string, meta?: Record<string, any>) => Response;
  noContent: () => Response;
  notFound: (message?: string) => Response;
  badRequest: (message?: string, errors?: any[]) => Response;
  unauthorized: (message?: string) => Response;
  forbidden: (message?: string) => Response;
  serverError: (message?: string, error?: any) => Response;
};

export const createResponseFormatter = (res: Response): ResponseFormatter => {
  return {
    success: vi.fn((data, message = 'Success', meta = {}) => {
      const response: ApiResponse<typeof data> = {
        success: true,
        message,
        data,
        meta
      };
      return res.status(200).json(response);
    }),
    
    created: vi.fn((data, message = 'Resource created successfully', meta = {}) => {
      const response: ApiResponse<typeof data> = {
        success: true,
        message,
        data,
        meta
      };
      return res.status(201).json(response);
    }),
    
    noContent: vi.fn(() => {
      return res.status(204).end();
    }),
    
    notFound: vi.fn((message = 'Resource not found') => {
      const response: ApiResponse<null> = {
        success: false,
        message
      };
      return res.status(404).json(response);
    }),
    
    badRequest: vi.fn((message = 'Bad request', errors = []) => {
      const response: ApiResponse<null> = {
        success: false,
        message,
        meta: { errors }
      };
      return res.status(400).json(response);
    }),
    
    unauthorized: vi.fn((message = 'Unauthorized') => {
      const response: ApiResponse<null> = {
        success: false,
        message
      };
      return res.status(401).json(response);
    }),
    
    forbidden: vi.fn((message = 'Forbidden') => {
      const response: ApiResponse<null> = {
        success: false,
        message
      };
      return res.status(403).json(response);
    }),
    
    serverError: vi.fn((message = 'Internal server error', error = null) => {
      const response: ApiResponse<null> = {
        success: false,
        message,
        meta: process.env.NODE_ENV === 'development' ? { error } : undefined
      };
      return res.status(500).json(response);
    })
  };
};

export default createResponseFormatter;