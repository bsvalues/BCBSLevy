/**
 * Enhanced Tax Codes API Routes
 * 
 * Example of using the new utilities and middleware for better API design
 */

import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { db } from '../../../../../shared/db';
import { 
  taxCodes, 
  taxCodeHistoricalRates,
  taxCodeToTaxDistrict,
  taxDistricts
} from '../../../../../shared/schema';
import { eq, and, like, ilike, desc, asc } from 'drizzle-orm';
import { AuthenticatedRequest, requireAuth } from '../../../middleware/mockAuth';
import { validateRequest, commonValidations } from '../../../middleware/validateRequest';
import { handleError, NotFoundError } from '../../../utils/handleError';
import { buildQueryParams, applyPagination, applySorting, applyFilters } from '../../../utils/buildQueryParams';
import { createResponseFormatter } from '../../../utils/formatResponse';

const router = Router();

// Validation schema for tax code queries
const TaxCodeQuerySchema = z.object({
  ...commonValidations.pagination.shape,
  ...commonValidations.sorting.shape,
  code: z.string().optional(),
  name: z.string().optional(),
  isActive: z.coerce.boolean().optional(),
});

// Get all tax codes with optional filtering
router.get('/', 
  requireAuth,
  validateRequest({ query: TaxCodeQuerySchema }),
  async (req: AuthenticatedRequest, res: Response) => {
    try {
      const { pagination, sorting, filters } = buildQueryParams(req, 'code');
      const { offset, limit } = applyPagination(pagination);
      
      // Custom filters (beyond the standard filter[field]=value pattern)
      const whereConditions = [];
      
      if (req.query.code) {
        whereConditions.push(ilike(taxCodes.code, `%${req.query.code}%`));
      }
      
      if (req.query.name) {
        whereConditions.push(ilike(taxCodes.name, `%${req.query.name}%`));
      }
      
      if (req.query.isActive !== undefined) {
        whereConditions.push(eq(taxCodes.isActive, req.query.isActive === 'true'));
      }
      
      // Build the combined WHERE clause
      const whereClause = whereConditions.length > 0 ? and(...whereConditions) : undefined;
      
      // Execute query with filtering, sorting, and pagination
      const taxCodeList = await db.query.taxCodes.findMany({
        where: whereClause,
        orderBy: sorting.sortDir === 'asc' 
          ? asc(taxCodes[sorting.sortBy as keyof typeof taxCodes] || taxCodes.code)
          : desc(taxCodes[sorting.sortBy as keyof typeof taxCodes] || taxCodes.code),
        offset,
        limit,
      });
      
      // Get total count for pagination
      const countResult = await db.select({ count: db.fn.count() }).from(taxCodes)
        .where(whereClause);
      
      const totalCount = Number(countResult[0].count);
      const totalPages = Math.ceil(totalCount / limit);
      
      // Use response formatter
      const formatter = createResponseFormatter(res);
      return formatter.paginated(taxCodeList, {
        page: pagination.page,
        limit: pagination.limit,
        totalItems: totalCount,
        totalPages
      }, 'Tax codes retrieved successfully');
      
    } catch (error) {
      return handleError(error, res, 'TaxCodes:list');
    }
  }
);

// Get a specific tax code by ID
router.get('/:id', 
  requireAuth,
  validateRequest({ params: commonValidations.idParam }),
  async (req: AuthenticatedRequest, res: Response) => {
    try {
      const taxCodeId = parseInt(req.params.id);
      
      const taxCode = await db.query.taxCodes.findFirst({
        where: eq(taxCodes.id, taxCodeId)
      });
      
      if (!taxCode) {
        throw new NotFoundError('Tax code not found');
      }
      
      const formatter = createResponseFormatter(res);
      return formatter.success(taxCode, 'Tax code retrieved successfully');
      
    } catch (error) {
      return handleError(error, res, 'TaxCodes:get');
    }
  }
);

// Get historical rates for a tax code
router.get('/:id/historical-rates', 
  requireAuth,
  validateRequest({ params: commonValidations.idParam }),
  async (req: AuthenticatedRequest, res: Response) => {
    try {
      const taxCodeId = parseInt(req.params.id);
      
      // Verify tax code exists
      const taxCode = await db.query.taxCodes.findFirst({
        where: eq(taxCodes.id, taxCodeId)
      });
      
      if (!taxCode) {
        throw new NotFoundError('Tax code not found');
      }
      
      // Get historical rates
      const historicalRates = await db.query.taxCodeHistoricalRates.findMany({
        where: eq(taxCodeHistoricalRates.taxCodeId, taxCodeId),
        orderBy: desc(taxCodeHistoricalRates.year)
      });
      
      const formatter = createResponseFormatter(res);
      return formatter.success(historicalRates, 'Historical rates retrieved successfully');
      
    } catch (error) {
      return handleError(error, res, 'TaxCodes:historicalRates');
    }
  }
);

export default router;