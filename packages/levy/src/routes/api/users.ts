import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { db } from '../../../../shared/db';
import { 
  users,
  userRoles
} from '../../../../shared/schema';
import { eq, and, like, ilike, desc, asc } from 'drizzle-orm';
import { AuthenticatedRequest, requireAuth, requireAdmin } from '../../middleware/mockAuth';

const router = Router();

// Validation schema for user queries
const UserQuerySchema = z.object({
  username: z.string().optional(),
  email: z.string().optional(),
  isActive: z.coerce.boolean().optional(),
  isAdmin: z.coerce.boolean().optional(),
  page: z.coerce.number().int().positive().optional().default(1),
  limit: z.coerce.number().int().positive().max(100).optional().default(20),
  sortBy: z.enum(['username', 'email', 'firstName', 'lastName', 'createdAt']).optional().default('username'),
  sortDir: z.enum(['asc', 'desc']).optional().default('asc'),
});

// Validation schema for user creation/updates
const UserValidationSchema = z.object({
  username: z.string().min(3).max(64),
  email: z.string().email().max(120),
  firstName: z.string().max(64).optional(),
  lastName: z.string().max(64).optional(),
  isActive: z.boolean().default(true),
  isAdmin: z.boolean().default(false),
  passwordHash: z.string().min(8).max(256).optional(), // Optional for updates
  roles: z.array(z.string()).optional(),
});

// Get all users with optional filtering (admin only)
router.get('/', requireAuth, requireAdmin, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const parsedQuery = UserQuerySchema.safeParse(req.query);
    
    if (!parsedQuery.success) {
      return res.status(400).json({
        success: false,
        message: 'Invalid query parameters',
        errors: parsedQuery.error.errors
      });
    }
    
    const query = parsedQuery.data;
    const offset = (query.page - 1) * query.limit;
    
    // Build query conditions
    const whereConditions = [];
    
    if (query.username) {
      whereConditions.push(ilike(users.username, `%${query.username}%`));
    }
    
    if (query.email) {
      whereConditions.push(ilike(users.email, `%${query.email}%`));
    }
    
    if (query.isActive !== undefined) {
      whereConditions.push(eq(users.isActive, query.isActive));
    }
    
    if (query.isAdmin !== undefined) {
      whereConditions.push(eq(users.isAdmin, query.isAdmin));
    }
    
    // Execute query with filtering, sorting, and pagination
    const usersList = await db.query.users.findMany({
      where: whereConditions.length > 0 ? and(...whereConditions) : undefined,
      orderBy: query.sortDir === 'asc' 
        ? asc(users[query.sortBy as keyof typeof users])
        : desc(users[query.sortBy as keyof typeof users]),
      offset,
      limit: query.limit,
      with: {
        roles: true
      },
      columns: {
        // Exclude sensitive data
        passwordHash: false,
        resetToken: false,
        resetTokenExpiry: false
      }
    });
    
    // Get total count for pagination
    const countResult = await db.select({ count: db.fn.count() }).from(users)
      .where(whereConditions.length > 0 ? and(...whereConditions) : undefined);
    
    const totalCount = Number(countResult[0].count);
    const totalPages = Math.ceil(totalCount / query.limit);
    
    return res.json({
      success: true,
      data: usersList,
      pagination: {
        page: query.page,
        limit: query.limit,
        totalItems: totalCount,
        totalPages
      }
    });
  } catch (error) {
    console.error('Error fetching users:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch users',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

// Get a specific user by ID
router.get('/:id', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const userId = parseInt(req.params.id);
    
    if (isNaN(userId)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid user ID'
      });
    }
    
    // Non-admin users can only view their own profile
    if (!req.user?.isAdmin && req.user?.id !== userId) {
      return res.status(403).json({
        success: false,
        message: 'Access denied'
      });
    }
    
    const user = await db.query.users.findFirst({
      where: eq(users.id, userId),
      with: {
        roles: true
      },
      columns: {
        // Exclude sensitive data
        passwordHash: false,
        resetToken: false,
        resetTokenExpiry: false
      }
    });
    
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }
    
    return res.json({
      success: true,
      data: user
    });
  } catch (error) {
    console.error('Error fetching user:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch user',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

// Create a new user (admin only)
router.post('/', requireAuth, requireAdmin, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const validationSchema = UserValidationSchema.merge(
      z.object({
        passwordHash: z.string().min(8).max(256), // Required for creation
      })
    );
    
    const parseResult = validationSchema.safeParse(req.body);
    
    if (!parseResult.success) {
      return res.status(400).json({
        success: false,
        message: 'Invalid user data',
        errors: parseResult.error.errors
      });
    }
    
    const userData = parseResult.data;
    
    // Check if username or email already exists
    const existingUser = await db.query.users.findFirst({
      where: db.or(
        eq(users.username, userData.username),
        eq(users.email, userData.email)
      )
    });
    
    if (existingUser) {
      return res.status(409).json({
        success: false,
        message: 'Username or email already exists'
      });
    }
    
    // Extract roles from the request and create user without roles first
    const { roles, ...userDataWithoutRoles } = userData;
    
    // Create the user
    const newUser = await db.insert(users).values({
      ...userDataWithoutRoles,
      createdAt: new Date(),
      updatedAt: new Date()
    }).returning();
    
    // If roles were specified, add them to the user
    if (roles && roles.length > 0) {
      const userRoleEntries = roles.map(role => ({
        userId: newUser[0].id,
        role,
        createdAt: new Date()
      }));
      
      await db.insert(userRoles).values(userRoleEntries);
    }
    
    // Get the complete user with roles
    const createdUser = await db.query.users.findFirst({
      where: eq(users.id, newUser[0].id),
      with: {
        roles: true
      },
      columns: {
        // Exclude sensitive data
        passwordHash: false,
        resetToken: false,
        resetTokenExpiry: false
      }
    });
    
    return res.status(201).json({
      success: true,
      message: 'User created successfully',
      data: createdUser
    });
  } catch (error) {
    console.error('Error creating user:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to create user',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

// Update a user
router.put('/:id', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const userId = parseInt(req.params.id);
    
    if (isNaN(userId)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid user ID'
      });
    }
    
    // Non-admin users can only update their own profile and cannot update isAdmin status
    if (!req.user?.isAdmin && req.user?.id !== userId) {
      return res.status(403).json({
        success: false,
        message: 'Access denied'
      });
    }
    
    // Verify user exists
    const existingUser = await db.query.users.findFirst({
      where: eq(users.id, userId)
    });
    
    if (!existingUser) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }
    
    // For non-admin users, prevent changing admin status
    let validationSchema = UserValidationSchema.partial();
    if (!req.user?.isAdmin) {
      validationSchema = validationSchema.omit({ isAdmin: true });
      
      // Remove isAdmin from the request body to prevent exploit attempts
      if (req.body.isAdmin !== undefined) {
        delete req.body.isAdmin;
      }
    }
    
    const parseResult = validationSchema.safeParse(req.body);
    
    if (!parseResult.success) {
      return res.status(400).json({
        success: false,
        message: 'Invalid update data',
        errors: parseResult.error.errors
      });
    }
    
    // If updating username or email, check if they're already taken by another user
    if (parseResult.data.username || parseResult.data.email) {
      const conflictQuery = db.or(
        parseResult.data.username ? eq(users.username, parseResult.data.username) : undefined,
        parseResult.data.email ? eq(users.email, parseResult.data.email) : undefined
      );
      
      const conflictUser = await db.query.users.findFirst({
        where: db.and(
          conflictQuery,
          db.not(eq(users.id, userId))
        )
      });
      
      if (conflictUser) {
        return res.status(409).json({
          success: false,
          message: 'Username or email already exists'
        });
      }
    }
    
    // Extract roles from the request, if any
    const { roles, ...updateData } = parseResult.data;
    
    // Update the user
    await db.update(users)
      .set({
        ...updateData,
        updatedAt: new Date()
      })
      .where(eq(users.id, userId));
    
    // Update roles if specified and user is admin
    if (roles && req.user?.isAdmin) {
      // Delete existing roles
      await db.delete(userRoles).where(eq(userRoles.userId, userId));
      
      // Add new roles
      if (roles.length > 0) {
        const userRoleEntries = roles.map(role => ({
          userId,
          role,
          createdAt: new Date()
        }));
        
        await db.insert(userRoles).values(userRoleEntries);
      }
    }
    
    // Get the updated user
    const updatedUser = await db.query.users.findFirst({
      where: eq(users.id, userId),
      with: {
        roles: true
      },
      columns: {
        // Exclude sensitive data
        passwordHash: false,
        resetToken: false,
        resetTokenExpiry: false
      }
    });
    
    return res.json({
      success: true,
      message: 'User updated successfully',
      data: updatedUser
    });
  } catch (error) {
    console.error('Error updating user:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to update user',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

// Get current user profile
router.get('/profile/me', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    if (!req.user?.id) {
      return res.status(401).json({
        success: false,
        message: 'Not authenticated'
      });
    }
    
    const profile = await db.query.users.findFirst({
      where: eq(users.id, req.user.id),
      with: {
        roles: true
      },
      columns: {
        // Exclude sensitive data
        passwordHash: false,
        resetToken: false,
        resetTokenExpiry: false
      }
    });
    
    if (!profile) {
      return res.status(404).json({
        success: false,
        message: 'User profile not found'
      });
    }
    
    return res.json({
      success: true,
      data: profile
    });
  } catch (error) {
    console.error('Error fetching user profile:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch user profile',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

export default router;