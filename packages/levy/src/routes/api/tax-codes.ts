import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { db } from '../../../../shared/db';
import { 
  taxCodes, 
  taxCodeHistoricalRates,
  taxCodeToTaxDistrict,
  taxDistricts
} from '../../../../shared/schema';
import { eq, and, like, ilike, desc, asc } from 'drizzle-orm';
import { AuthenticatedRequest, requireAuth } from '../../middleware/mockAuth';

const router = Router();

// Validation schema for tax code queries
const TaxCodeQuerySchema = z.object({
  code: z.string().optional(),
  name: z.string().optional(),
  isActive: z.coerce.boolean().optional(),
  page: z.coerce.number().int().positive().optional().default(1),
  limit: z.coerce.number().int().positive().max(100).optional().default(20),
  sortBy: z.enum(['code', 'name', 'levyRate', 'createdAt']).optional().default('code'),
  sortDir: z.enum(['asc', 'desc']).optional().default('asc'),
});

// Get all tax codes with optional filtering
router.get('/', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const parsedQuery = TaxCodeQuerySchema.safeParse(req.query);
    
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
    
    if (query.code) {
      whereConditions.push(ilike(taxCodes.code, `%${query.code}%`));
    }
    
    if (query.name) {
      whereConditions.push(ilike(taxCodes.name, `%${query.name}%`));
    }
    
    if (query.isActive !== undefined) {
      whereConditions.push(eq(taxCodes.isActive, query.isActive));
    }
    
    // Execute query with filtering, sorting, and pagination
    const taxCodeList = await db.query.taxCodes.findMany({
      where: whereConditions.length > 0 ? and(...whereConditions) : undefined,
      orderBy: query.sortDir === 'asc' 
        ? asc(taxCodes[query.sortBy as keyof typeof taxCodes])
        : desc(taxCodes[query.sortBy as keyof typeof taxCodes]),
      offset,
      limit: query.limit,
    });
    
    // Get total count for pagination
    const countResult = await db.select({ count: db.fn.count() }).from(taxCodes)
      .where(whereConditions.length > 0 ? and(...whereConditions) : undefined);
    
    const totalCount = Number(countResult[0].count);
    const totalPages = Math.ceil(totalCount / query.limit);
    
    return res.json({
      success: true,
      data: taxCodeList,
      pagination: {
        page: query.page,
        limit: query.limit,
        totalItems: totalCount,
        totalPages
      }
    });
  } catch (error) {
    console.error('Error fetching tax codes:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch tax codes',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

// Get a specific tax code by ID
router.get('/:id', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const taxCodeId = parseInt(req.params.id);
    
    if (isNaN(taxCodeId)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid tax code ID'
      });
    }
    
    const taxCode = await db.query.taxCodes.findFirst({
      where: eq(taxCodes.id, taxCodeId)
    });
    
    if (!taxCode) {
      return res.status(404).json({
        success: false,
        message: 'Tax code not found'
      });
    }
    
    return res.json({
      success: true,
      data: taxCode
    });
  } catch (error) {
    console.error('Error fetching tax code:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch tax code',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

// Get historical rates for a tax code
router.get('/:id/historical-rates', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const taxCodeId = parseInt(req.params.id);
    
    if (isNaN(taxCodeId)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid tax code ID'
      });
    }
    
    // Verify tax code exists
    const taxCode = await db.query.taxCodes.findFirst({
      where: eq(taxCodes.id, taxCodeId)
    });
    
    if (!taxCode) {
      return res.status(404).json({
        success: false,
        message: 'Tax code not found'
      });
    }
    
    // Get historical rates
    const historicalRates = await db.query.taxCodeHistoricalRates.findMany({
      where: eq(taxCodeHistoricalRates.taxCodeId, taxCodeId),
      orderBy: desc(taxCodeHistoricalRates.year)
    });
    
    return res.json({
      success: true,
      data: historicalRates
    });
  } catch (error) {
    console.error('Error fetching historical rates:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch historical rates',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

// Get tax districts associated with a tax code
router.get('/:id/tax-districts', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const taxCodeId = parseInt(req.params.id);
    
    if (isNaN(taxCodeId)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid tax code ID'
      });
    }
    
    // Verify tax code exists
    const taxCode = await db.query.taxCodes.findFirst({
      where: eq(taxCodes.id, taxCodeId)
    });
    
    if (!taxCode) {
      return res.status(404).json({
        success: false,
        message: 'Tax code not found'
      });
    }
    
    // Get tax districts associated with this tax code
    const taxDistrictRelations = await db.select({
      relationId: taxCodeToTaxDistrict.id,
      taxDistrictId: taxCodeToTaxDistrict.taxDistrictId,
      percentage: taxCodeToTaxDistrict.percentage,
      isActive: taxCodeToTaxDistrict.isActive
    })
    .from(taxCodeToTaxDistrict)
    .where(eq(taxCodeToTaxDistrict.taxCodeId, taxCodeId));
    
    if (!taxDistrictRelations.length) {
      return res.json({
        success: true,
        data: [],
        message: 'No tax districts associated with this tax code'
      });
    }
    
    // Get the tax district details for each relation
    const taxDistrictIds = taxDistrictRelations.map(relation => relation.taxDistrictId);
    const taxDistrictDetails = await db.query.taxDistricts.findMany({
      where: db.and(
        db.inArray(taxDistricts.id, taxDistrictIds),
        eq(taxDistricts.isActive, true)
      )
    });
    
    // Combine the tax district details with the relationship data
    const result = taxDistrictRelations.map(relation => {
      const taxDistrictDetail = taxDistrictDetails.find(td => td.id === relation.taxDistrictId);
      return {
        ...relation,
        taxDistrict: taxDistrictDetail || null
      };
    });
    
    return res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('Error fetching tax districts for tax code:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch tax districts for tax code',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

export default router;