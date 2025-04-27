import { Request } from 'express';

/**
 * Extended Request type that includes user authentication data
 */
export interface AuthenticatedRequest extends Request {
  user?: {
    id: number;
    username: string;
    email: string;
    isAdmin: boolean;
    firstName?: string;
    lastName?: string;
    roles: string[];
  };
}

/**
 * Mock middleware for authentication
 * 
 * @param req Express request object
 * @param res Express response object
 * @param next Next middleware function
 */
export function mockAuthMiddleware(req: Request, res: any, next: () => void) {
  // Add a mock user to the request
  (req as AuthenticatedRequest).user = {
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    isAdmin: false,
    firstName: 'Test',
    lastName: 'User',
    roles: ['user']
  };
  
  next();
}

/**
 * Mock middleware for admin authentication
 */
export function mockAdminAuthMiddleware(req: Request, res: any, next: () => void) {
  // Add a mock admin user to the request
  (req as AuthenticatedRequest).user = {
    id: 2,
    username: 'adminuser',
    email: 'admin@example.com',
    isAdmin: true,
    firstName: 'Admin',
    lastName: 'User',
    roles: ['admin', 'user']
  };
  
  next();
}