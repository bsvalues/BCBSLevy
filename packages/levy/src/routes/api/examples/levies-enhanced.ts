/**
 * Enhanced Levies API Routes
 * 
 * Example of using the new utilities and middleware for better API design
 */

import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { db } from '../../../../../shared/db';
import { 
  levies,
  taxDistricts,
  taxCodes,
  users
} from '../../../../../shared/schema';
import { eq, and, like, ilike, desc, asc, inArray } from 'drizzle-orm';
import { AuthenticatedRequest, requireAuth, requireAdmin } from '../../../middleware/mockAuth';
import { validateRequest, commonValidations } from '../../../middleware/validateRequest';
import { handleError, NotFoundError, AuthorizationError, ConflictError } from '../../../utils/handleError';
import { buildQueryParams, applyPagination, applySorting } from '../../../utils/buildQueryParams';
import { createResponseFormatter } from '../../../utils/formatResponse';

// Import the validation schema
import { LevyCreateSchema, LevyUpdateSchema } from '../../../../../shared/schema/leviesValidation';

const router = Router();

// Enhanced validation schema for levy queries
const LevyQuerySchema = z.object({
  ...commonValidations.pagination.shape,
  ...commonValidations.sorting.shape,
  name: z.string().optional(),
  taxYear: z.coerce.number().int().positive().optional(),
  taxDistrictId: z.coerce.number().int().positive().optional(),
  taxCodeId: z.coerce.number().int().positive().optional(),
  status: z.enum(['draft', 'submitted', 'approved', 'rejected', 'archived']).optional(),
});

// Get all levies with optional filtering
router.get('/', 
  requireAuth,
  validateRequest({ query: LevyQuerySchema }), 
  async (req: AuthenticatedRequest, res: Response) => {
    try {
      const { pagination, sorting } = buildQueryParams(req, 'taxYear');
      const { offset, limit } = applyPagination(pagination);
      
      // Build query conditions
      const whereConditions = [];
      
      if (req.query.name) {
        whereConditions.push(ilike(levies.name, `%${req.query.name}%`));
      }
      
      if (req.query.taxYear) {
        whereConditions.push(eq(levies.taxYear, Number(req.query.taxYear)));
      }
      
      if (req.query.taxDistrictId) {
        whereConditions.push(eq(levies.taxDistrictId, Number(req.query.taxDistrictId)));
      }
      
      if (req.query.taxCodeId) {
        whereConditions.push(eq(levies.taxCodeId, Number(req.query.taxCodeId)));
      }
      
      if (req.query.status) {
        whereConditions.push(eq(levies.status, req.query.status as string));
      }
      
      // Execute query with filtering, sorting, and pagination
      const leviesList = await db.query.levies.findMany({
        where: whereConditions.length > 0 ? and(...whereConditions) : undefined,
        orderBy: sorting.sortDir === 'asc' 
          ? asc(levies[sorting.sortBy as keyof typeof levies] || levies.taxYear)
          : desc(levies[sorting.sortBy as keyof typeof levies] || levies.taxYear),
        offset,
        limit,
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
      const totalPages = Math.ceil(totalCount / limit);
      
      // Use response formatter
      const formatter = createResponseFormatter(res);
      return formatter.paginated(leviesList, {
        page: pagination.page,
        limit: pagination.limit,
        totalItems: totalCount,
        totalPages
      }, 'Levies retrieved successfully');
      
    } catch (error) {
      return handleError(error, res, 'Levies:list');
    }
  }
);

// Get a specific levy by ID
router.get('/:id', 
  requireAuth,
  validateRequest({ params: commonValidations.idParam }),
  async (req: AuthenticatedRequest, res: Response) => {
    try {
      const levyId = parseInt(req.params.id);
      
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
        throw new NotFoundError('Levy not found');
      }
      
      const formatter = createResponseFormatter(res);
      return formatter.success(levy);
      
    } catch (error) {
      return handleError(error, res, 'Levies:get');
    }
  }
);

// Create a new levy
router.post('/', 
  requireAuth,
  validateRequest({ body: LevyCreateSchema }),
  async (req: AuthenticatedRequest, res: Response) => {
    try {
      const levyData = req.body;
      
      // Verify tax district exists
      const taxDistrict = await db.query.taxDistricts.findFirst({
        where: eq(taxDistricts.id, levyData.taxDistrictId)
      });
      
      if (!taxDistrict) {
        throw new NotFoundError('Tax district not found');
      }
      
      // Verify tax code exists
      const taxCode = await db.query.taxCodes.findFirst({
        where: eq(taxCodes.id, levyData.taxCodeId)
      });
      
      if (!taxCode) {
        throw new NotFoundError('Tax code not found');
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
      
      const formatter = createResponseFormatter(res);
      return formatter.created(createdLevy, 'Levy created successfully');
      
    } catch (error) {
      return handleError(error, res, 'Levies:create');
    }
  }
);

// Update an existing levy
router.put('/:id', 
  requireAuth,
  validateRequest({ 
    params: commonValidations.idParam,
    body: LevyUpdateSchema
  }),
  async (req: AuthenticatedRequest, res: Response) => {
    try {
      const levyId = parseInt(req.params.id);
      const updateData = req.body;
      
      // Verify levy exists
      const existingLevy = await db.query.levies.findFirst({
        where: eq(levies.id, levyId)
      });
      
      if (!existingLevy) {
        throw new NotFoundError('Levy not found');
      }
      
      // Prevent updating approved levies unless user is admin
      if (existingLevy.status === 'approved' && !req.user?.isAdmin) {
        throw new AuthorizationError('Cannot update an approved levy unless you are an administrator');
      }
      
      // If updating tax district or tax code, verify they exist
      if (updateData.taxDistrictId) {
        const taxDistrict = await db.query.taxDistricts.findFirst({
          where: eq(taxDistricts.id, updateData.taxDistrictId)
        });
        
        if (!taxDistrict) {
          throw new NotFoundError('Tax district not found');
        }
      }
      
      if (updateData.taxCodeId) {
        const taxCode = await db.query.taxCodes.findFirst({
          where: eq(taxCodes.id, updateData.taxCodeId)
        });
        
        if (!taxCode) {
          throw new NotFoundError('Tax code not found');
        }
      }
      
      // Set the current user as updater
      const userId = req.user?.id || 1; // Default to 1 if no user in testing
      
      // Handle approval if status is changing to 'approved'
      if (updateData.status === 'approved' && existingLevy.status !== 'approved') {
        // Only admins can approve
        if (!req.user?.isAdmin) {
          throw new AuthorizationError('Only administrators can approve levies');
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
      
      const formatter = createResponseFormatter(res);
      return formatter.success(updatedLevy, 'Levy updated successfully');
      
    } catch (error) {
      return handleError(error, res, 'Levies:update');
    }
  }
);

// Delete a levy
router.delete('/:id', 
  requireAuth,
  validateRequest({ params: commonValidations.idParam }),
  async (req: AuthenticatedRequest, res: Response) => {
    try {
      const levyId = parseInt(req.params.id);
      
      // Verify levy exists
      const existingLevy = await db.query.levies.findFirst({
        where: eq(levies.id, levyId)
      });
      
      if (!existingLevy) {
        throw new NotFoundError('Levy not found');
      }
      
      // Check if levy can be deleted
      if (existingLevy.status === 'approved' && !req.user?.isAdmin) {
        throw new AuthorizationError('Cannot delete an approved levy unless you are an administrator');
      }
      
      // Delete the levy
      await db.delete(levies).where(eq(levies.id, levyId));
      
      const formatter = createResponseFormatter(res);
      return formatter.noContent();
      
    } catch (error) {
      return handleError(error, res, 'Levies:delete');
    }
  }
);

// Bulk approve levies (admin only)
router.post('/bulk/approve', 
  requireAuth,
  requireAdmin,
  validateRequest({ 
    body: z.object({
      levyIds: z.array(z.number().int().positive())
    })
  }),
  async (req: AuthenticatedRequest, res: Response) => {
    try {
      const { levyIds } = req.body;
      
      if (levyIds.length === 0) {
        throw new ValidationError('No levy IDs provided');
      }
      
      // Get all the levies to be approved
      const leviesToApprove = await db.query.levies.findMany({
        where: db.and(
          inArray(levies.id, levyIds),
          db.not(eq(levies.status, 'approved'))
        )
      });
      
      if (leviesToApprove.length === 0) {
        throw new NotFoundError('No valid levies to approve');
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
      
      const formatter = createResponseFormatter(res);
      return formatter.success({
        approvedCount: leviesToApprove.length,
        approvedIds: leviesToApprove.map(levy => levy.id)
      }, `Successfully approved ${leviesToApprove.length} levies`);
      
    } catch (error) {
      return handleError(error, res, 'Levies:bulkApprove');
    }
  }
);

export default router;