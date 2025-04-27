/**
 * Levy Controller
 * 
 * Extends the BaseController to provide specialized functionality for levies.
 */

import { Request, Response } from 'express';
import { BaseController } from './BaseController';
import { db } from '../../../shared/db';
import { 
  levies,
  taxDistricts,
  taxCodes,
  users
} from '../../../shared/schema';
import { eq, and, inArray, desc } from 'drizzle-orm';
import { handleError, NotFoundError, AuthorizationError } from '../utils/handleError';
import { createResponseFormatter } from '../utils/formatResponse';
import { AuthenticatedRequest } from '../middleware/mockAuth';

/**
 * Controller for levy-related operations
 */
export class LevyController extends BaseController {
  /**
   * Create a new LevyController
   */
  constructor() {
    super({
      tableName: 'levies',
      primaryKey: 'id'
    });
  }
  
  /**
   * Create a new levy with validation of related entities
   */
  createLevy = async (req: AuthenticatedRequest, res: Response) => {
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
      return handleError(error, res, 'Levy:create');
    }
  };
  
  /**
   * Update a levy with validation of related entities and permissions
   */
  updateLevy = async (req: AuthenticatedRequest, res: Response) => {
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
      return handleError(error, res, 'Levy:update');
    }
  };
  
  /**
   * Delete a levy with permission checks
   */
  deleteLevy = async (req: AuthenticatedRequest, res: Response) => {
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
      return handleError(error, res, 'Levy:delete');
    }
  };
  
  /**
   * Bulk approve levies (admin only)
   */
  bulkApprove = async (req: AuthenticatedRequest, res: Response) => {
    try {
      const { levyIds } = req.body;
      
      if (!req.user?.isAdmin) {
        throw new AuthorizationError('Only administrators can approve levies');
      }
      
      if (!levyIds || !Array.isArray(levyIds) || levyIds.length === 0) {
        throw new Error('No levy IDs provided');
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
      return handleError(error, res, 'Levy:bulkApprove');
    }
  };
  
  /**
   * Get the levy history for a tax district
   */
  getLevyHistory = async (req: Request, res: Response) => {
    try {
      const taxDistrictId = parseInt(req.params.districtId);
      
      // Verify tax district exists
      const taxDistrict = await db.query.taxDistricts.findFirst({
        where: eq(taxDistricts.id, taxDistrictId)
      });
      
      if (!taxDistrict) {
        throw new NotFoundError('Tax district not found');
      }
      
      // Get levy history for the district, grouped by year
      const levyHistory = await db.query.levies.findMany({
        where: eq(levies.taxDistrictId, taxDistrictId),
        orderBy: desc(levies.taxYear),
        with: {
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
      
      // Group the levy history by year
      const levyHistoryByYear = levyHistory.reduce((acc, levy) => {
        const year = levy.taxYear;
        
        if (!acc[year]) {
          acc[year] = [];
        }
        
        acc[year].push(levy);
        return acc;
      }, {} as Record<number, typeof levyHistory>);
      
      // Convert to array format
      const result = Object.entries(levyHistoryByYear).map(([year, levies]) => ({
        year: parseInt(year),
        levies,
        totalLevyAmount: levies.reduce((sum, levy) => sum + (levy.levyAmount || 0), 0),
        levyCount: levies.length
      }));
      
      const formatter = createResponseFormatter(res);
      return formatter.success(result, 'Levy history retrieved successfully');
      
    } catch (error) {
      return handleError(error, res, 'Levy:getLevyHistory');
    }
  };
}

export default LevyController;