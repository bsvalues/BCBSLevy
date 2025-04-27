/**
 * Mock Authentication Middleware
 * 
 * This module provides mock authentication functionality for the API.
 * In a production environment, this would be replaced with a real authentication system.
 */

import { Request, Response, NextFunction } from 'express';

/**
 * Interface extending Express Request to include user information
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
 * Mock authentication middleware that adds a mock user to every request
 * 
 * This is for development purposes only and should be replaced with real authentication in production
 */
export const requireAuth = (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
  // Mock user - in production, this would be extracted from a JWT or session
  req.user = {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    isAdmin: true,
    firstName: 'Admin',
    lastName: 'User',
    roles: ['admin', 'user']
  };
  
  next();
};

/**
 * Mock admin authorization middleware
 * 
 * Requires that the user has admin permissions
 */
export const requireAdmin = (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
  if (!req.user?.isAdmin) {
    return res.status(403).json({
      success: false,
      message: 'Forbidden: Requires administrator privileges'
    });
  }
  
  next();
};

/**
 * Middleware to check if user has a specific role
 * 
 * @param role - The role to check for
 */
export const requireRole = (role: string) => {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
    if (!req.user?.roles.includes(role)) {
      return res.status(403).json({
        success: false,
        message: `Forbidden: Requires ${role} privileges`
      });
    }
    
    next();
  };
};

/**
 * Middleware to check if the user is the owner of a resource or an admin
 * 
 * @param userIdParam - Function to extract the user ID to check against from the request
 */
export const requireOwnershipOrAdmin = (
  userIdParam: (req: AuthenticatedRequest) => number
) => {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
    // Admins can access any resource
    if (req.user?.isAdmin) {
      return next();
    }
    
    const resourceUserId = userIdParam(req);
    
    // Check if the authenticated user is the owner of the resource
    if (req.user?.id === resourceUserId) {
      return next();
    }
    
    return res.status(403).json({
      success: false,
      message: 'Forbidden: You do not have permission to access this resource'
    });
  };
};