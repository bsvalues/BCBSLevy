import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { db } from '../../../../shared/db';
import { 
  levies,
  taxDistricts,
  taxCodes,
  users
} from '../../../../shared/schema';
import { eq, and, like, ilike, desc, asc, inArray } from 'drizzle-orm';
import { AuthenticatedRequest, requireAuth } from '../../middleware/mockAuth';

// Import the validation schema
import { LevyCreateSchema, LevyUpdateSchema } from '../../../../shared/schema/leviesValidation';

const router = Router();

// Validation schema for levy queries
const LevyQuerySchema = z.object({
  name: z.string().optional(),
  taxYear: z.coerce.number().int().positive().optional(),
  taxDistrictId: z.coerce.number().int().positive().optional(),
  taxCodeId: z.coerce.number().int().positive().optional(),
  status: z.enum(['draft', 'submitted', 'approved', 'rejected', 'archived']).optional(),
  page: z.coerce.number().int().positive().optional().default(1),
  limit: z.coerce.number().int().positive().max(100).optional().default(20),
  sortBy: z.enum(['name', 'taxYear', 'levyAmount', 'levyRate', 'status', 'createdAt']).optional().default('taxYear'),
  sortDir: z.enum(['asc', 'desc']).optional().default('desc'),
});

// Get all levies with optional filtering
router.get('/', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const parsedQuery = LevyQuerySchema.safeParse(req.query);
    
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
    
    if (query.name) {
      whereConditions.push(ilike(levies.name, `%${query.name}%`));
    }
    
    if (query.taxYear) {
      whereConditions.push(eq(levies.taxYear, query.taxYear));
    }
    
    if (query.taxDistrictId) {
      whereConditions.push(eq(levies.taxDistrictId, query.taxDistrictId));
    }
    
    if (query.taxCodeId) {
      whereConditions.push(eq(levies.taxCodeId, query.taxCodeId));
    }
    
    if (query.status) {
      whereConditions.push(eq(levies.status, query.status));
    }
    
    // Execute query with filtering, sorting, and pagination
    const leviesList = await db.query.levies.findMany({
      where: whereConditions.length > 0 ? and(...whereConditions) : undefined,
      orderBy: query.sortDir === 'asc' 
        ? asc(levies[query.sortBy as keyof typeof levies])
        : desc(levies[query.sortBy as keyof typeof levies]),
      offset,
      limit: query.limit,
      with: {
        taxDistrict: {
          columns: {
            id: true,
            name: true,
            districtType: true,
            countyName: true
          }
        },
        taxCode: {
          columns: {
            id: true,
            code: true,
            name: true,
            levyRate: true
          }
        }
      }
    });
    
    // Get total count for pagination
    const countResult = await db.select({ count: db.fn.count() }).from(levies)
      .where(whereConditions.length > 0 ? and(...whereConditions) : undefined);
    
    const totalCount = Number(countResult[0].count);
    const totalPages = Math.ceil(totalCount / query.limit);
    
    return res.json({
      success: true,
      data: leviesList,
      pagination: {
        page: query.page,
        limit: query.limit,
        totalItems: totalCount,
        totalPages
      }
    });
  } catch (error) {
    console.error('Error fetching levies:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch levies',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

// Get a specific levy by ID
router.get('/:id', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const levyId = parseInt(req.params.id);
    
    if (isNaN(levyId)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid levy ID'
      });
    }
    
    const levy = await db.query.levies.findFirst({
      where: eq(levies.id, levyId),
      with: {
        taxDistrict: true,
        taxCode: true,
        createdBy: {
          columns: {
            id: true,
            username: true,
            firstName: true,
            lastName: true
          }
        },
        updatedBy: {
          columns: {
            id: true,
            username: true,
            firstName: true,
            lastName: true
          }
        },
        approvedBy: {
          columns: {
            id: true,
            username: true,
            firstName: true,
            lastName: true
          }
        }
      }
    });
    
    if (!levy) {
      return res.status(404).json({
        success: false,
        message: 'Levy not found'
      });
    }
    
    return res.json({
      success: true,
      data: levy
    });
  } catch (error) {
    console.error('Error fetching levy:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch levy',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

// Create a new levy
router.post('/', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const parseResult = LevyCreateSchema.safeParse(req.body);
    
    if (!parseResult.success) {
      return res.status(400).json({
        success: false,
        message: 'Invalid levy data',
        errors: parseResult.error.errors
      });
    }
    
    const levyData = parseResult.data;
    
    // Verify tax district exists
    const taxDistrict = await db.query.taxDistricts.findFirst({
      where: eq(taxDistricts.id, levyData.taxDistrictId)
    });
    
    if (!taxDistrict) {
      return res.status(400).json({
        success: false,
        message: 'Tax district not found'
      });
    }
    
    // Verify tax code exists
    const taxCode = await db.query.taxCodes.findFirst({
      where: eq(taxCodes.id, levyData.taxCodeId)
    });
    
    if (!taxCode) {
      return res.status(400).json({
        success: false,
        message: 'Tax code not found'
      });
    }
    
    // Set the current user as creator and updater
    const userId = req.user?.id || 1; // Default to 1 if no user in testing
    
    // Insert new levy
    const newLevy = await db.insert(levies).values({
      ...levyData,
      createdById: userId,
      updatedById: userId,
      createdAt: new Date(),
      updatedAt: new Date()
    }).returning();
    
    // Get full levy details with relations for response
    const createdLevy = await db.query.levies.findFirst({
      where: eq(levies.id, newLevy[0].id),
      with: {
        taxDistrict: true,
        taxCode: true,
        createdBy: {
          columns: {
            id: true,
            username: true,
            firstName: true,
            lastName: true
          }
        },
        updatedBy: {
          columns: {
            id: true,
            username: true,
            firstName: true,
            lastName: true
          }
        }
      }
    });
    
    return res.status(201).json({
      success: true,
      message: 'Levy created successfully',
      data: createdLevy
    });
  } catch (error) {
    console.error('Error creating levy:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to create levy',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

// Update an existing levy
router.put('/:id', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const levyId = parseInt(req.params.id);
    
    if (isNaN(levyId)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid levy ID'
      });
    }
    
    // Verify levy exists
    const existingLevy = await db.query.levies.findFirst({
      where: eq(levies.id, levyId)
    });
    
    if (!existingLevy) {
      return res.status(404).json({
        success: false,
        message: 'Levy not found'
      });
    }
    
    // Prevent updating approved levies unless user is admin
    if (existingLevy.status === 'approved' && !req.user?.isAdmin) {
      return res.status(403).json({
        success: false,
        message: 'Cannot update an approved levy unless you are an administrator'
      });
    }
    
    const parseResult = LevyUpdateSchema.safeParse(req.body);
    
    if (!parseResult.success) {
      return res.status(400).json({
        success: false,
        message: 'Invalid update data',
        errors: parseResult.error.errors
      });
    }
    
    const updateData = parseResult.data;
    
    // If updating tax district or tax code, verify they exist
    if (updateData.taxDistrictId) {
      const taxDistrict = await db.query.taxDistricts.findFirst({
        where: eq(taxDistricts.id, updateData.taxDistrictId)
      });
      
      if (!taxDistrict) {
        return res.status(400).json({
          success: false,
          message: 'Tax district not found'
        });
      }
    }
    
    if (updateData.taxCodeId) {
      const taxCode = await db.query.taxCodes.findFirst({
        where: eq(taxCodes.id, updateData.taxCodeId)
      });
      
      if (!taxCode) {
        return res.status(400).json({
          success: false,
          message: 'Tax code not found'
        });
      }
    }
    
    // Set the current user as updater
    const userId = req.user?.id || 1; // Default to 1 if no user in testing
    
    // Handle approval if status is changing to 'approved'
    if (updateData.status === 'approved' && existingLevy.status !== 'approved') {
      // Only admins can approve
      if (!req.user?.isAdmin) {
        return res.status(403).json({
          success: false,
          message: 'Only administrators can approve levies'
        });
      }
      
      // Set approval details
      updateData.isApproved = true;
      updateData.approvedById = userId;
      updateData.approvedAt = new Date();
    }
    
    // Update the levy
    await db.update(levies)
      .set({
        ...updateData,
        updatedById: userId,
        updatedAt: new Date()
      })
      .where(eq(levies.id, levyId));
    
    // Get updated levy with relations for response
    const updatedLevy = await db.query.levies.findFirst({
      where: eq(levies.id, levyId),
      with: {
        taxDistrict: true,
        taxCode: true,
        createdBy: {
          columns: {
            id: true,
            username: true,
            firstName: true,
            lastName: true
          }
        },
        updatedBy: {
          columns: {
            id: true,
            username: true,
            firstName: true,
            lastName: true
          }
        },
        approvedBy: updateData.status === 'approved' ? {
          columns: {
            id: true,
            username: true,
            firstName: true,
            lastName: true
          }
        } : undefined
      }
    });
    
    return res.json({
      success: true,
      message: 'Levy updated successfully',
      data: updatedLevy
    });
  } catch (error) {
    console.error('Error updating levy:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to update levy',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

// Delete a levy
router.delete('/:id', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const levyId = parseInt(req.params.id);
    
    if (isNaN(levyId)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid levy ID'
      });
    }
    
    // Verify levy exists
    const existingLevy = await db.query.levies.findFirst({
      where: eq(levies.id, levyId)
    });
    
    if (!existingLevy) {
      return res.status(404).json({
        success: false,
        message: 'Levy not found'
      });
    }
    
    // Check if levy can be deleted
    if (existingLevy.status === 'approved' && !req.user?.isAdmin) {
      return res.status(403).json({
        success: false,
        message: 'Cannot delete an approved levy unless you are an administrator'
      });
    }
    
    // Delete the levy
    await db.delete(levies).where(eq(levies.id, levyId));
    
    return res.status(204).send();
  } catch (error) {
    console.error('Error deleting levy:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to delete levy',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

// Bulk approve levies (admin only)
router.post('/bulk/approve', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    // Only admins can approve
    if (!req.user?.isAdmin) {
      return res.status(403).json({
        success: false,
        message: 'Only administrators can approve levies'
      });
    }
    
    const bulkApproveSchema = z.object({
      levyIds: z.array(z.number().int().positive())
    });
    
    const parseResult = bulkApproveSchema.safeParse(req.body);
    
    if (!parseResult.success) {
      return res.status(400).json({
        success: false,
        message: 'Invalid request data',
        errors: parseResult.error.errors
      });
    }
    
    const { levyIds } = parseResult.data;
    
    if (levyIds.length === 0) {
      return res.status(400).json({
        success: false,
        message: 'No levy IDs provided'
      });
    }
    
    // Get all the levies to be approved
    const leviesToApprove = await db.query.levies.findMany({
      where: db.and(
        inArray(levies.id, levyIds),
        db.not(eq(levies.status, 'approved'))
      )
    });
    
    if (leviesToApprove.length === 0) {
      return res.status(400).json({
        success: false,
        message: 'No valid levies to approve'
      });
    }
    
    // Set the current user as approver
    const userId = req.user?.id || 1; // Default to 1 if no user in testing
    const now = new Date();
    
    // Update all levies
    await db.update(levies)
      .set({
        status: 'approved',
        isApproved: true,
        approvedById: userId,
        approvedAt: now,
        updatedById: userId,
        updatedAt: now
      })
      .where(db.and(
        inArray(levies.id, levyIds),
        db.not(eq(levies.status, 'approved'))
      ));
    
    return res.json({
      success: true,
      message: `Successfully approved ${leviesToApprove.length} levies`,
      data: {
        approvedCount: leviesToApprove.length,
        approvedIds: leviesToApprove.map(levy => levy.id)
      }
    });
  } catch (error) {
    console.error('Error bulk approving levies:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to bulk approve levies',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

export default router;