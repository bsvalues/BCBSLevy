import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { db } from '../../../../shared/db';
import { 
  taxDistricts, 
  taxCodes,
  taxCodeToTaxDistrict,
  levies
} from '../../../../shared/schema';
import { eq, and, like, ilike, desc, asc } from 'drizzle-orm';
import { AuthenticatedRequest, requireAuth } from '../../middleware/mockAuth';

const router = Router();

// Validation schema for tax district queries
const TaxDistrictQuerySchema = z.object({
  name: z.string().optional(),
  districtType: z.string().optional(),
  countyName: z.string().optional(),
  stateName: z.string().optional(),
  isActive: z.coerce.boolean().optional(),
  page: z.coerce.number().int().positive().optional().default(1),
  limit: z.coerce.number().int().positive().max(100).optional().default(20),
  sortBy: z.enum(['name', 'districtType', 'countyName', 'stateName', 'createdAt']).optional().default('name'),
  sortDir: z.enum(['asc', 'desc']).optional().default('asc'),
});

// Get all tax districts with optional filtering
router.get('/', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const parsedQuery = TaxDistrictQuerySchema.safeParse(req.query);
    
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
      whereConditions.push(ilike(taxDistricts.name, `%${query.name}%`));
    }
    
    if (query.districtType) {
      whereConditions.push(ilike(taxDistricts.districtType, `%${query.districtType}%`));
    }
    
    if (query.countyName) {
      whereConditions.push(ilike(taxDistricts.countyName, `%${query.countyName}%`));
    }
    
    if (query.stateName) {
      whereConditions.push(ilike(taxDistricts.stateName, `%${query.stateName}%`));
    }
    
    if (query.isActive !== undefined) {
      whereConditions.push(eq(taxDistricts.isActive, query.isActive));
    }
    
    // Execute query with filtering, sorting, and pagination
    const taxDistrictsList = await db.query.taxDistricts.findMany({
      where: whereConditions.length > 0 ? and(...whereConditions) : undefined,
      orderBy: query.sortDir === 'asc' 
        ? asc(taxDistricts[query.sortBy as keyof typeof taxDistricts])
        : desc(taxDistricts[query.sortBy as keyof typeof taxDistricts]),
      offset,
      limit: query.limit,
    });
    
    // Get total count for pagination
    const countResult = await db.select({ count: db.fn.count() }).from(taxDistricts)
      .where(whereConditions.length > 0 ? and(...whereConditions) : undefined);
    
    const totalCount = Number(countResult[0].count);
    const totalPages = Math.ceil(totalCount / query.limit);
    
    return res.json({
      success: true,
      data: taxDistrictsList,
      pagination: {
        page: query.page,
        limit: query.limit,
        totalItems: totalCount,
        totalPages
      }
    });
  } catch (error) {
    console.error('Error fetching tax districts:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch tax districts',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

// Get a specific tax district by ID
router.get('/:id', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const taxDistrictId = parseInt(req.params.id);
    
    if (isNaN(taxDistrictId)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid tax district ID'
      });
    }
    
    const taxDistrict = await db.query.taxDistricts.findFirst({
      where: eq(taxDistricts.id, taxDistrictId)
    });
    
    if (!taxDistrict) {
      return res.status(404).json({
        success: false,
        message: 'Tax district not found'
      });
    }
    
    return res.json({
      success: true,
      data: taxDistrict
    });
  } catch (error) {
    console.error('Error fetching tax district:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch tax district',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

// Get tax codes associated with a tax district
router.get('/:id/tax-codes', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const taxDistrictId = parseInt(req.params.id);
    
    if (isNaN(taxDistrictId)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid tax district ID'
      });
    }
    
    // Verify tax district exists
    const taxDistrict = await db.query.taxDistricts.findFirst({
      where: eq(taxDistricts.id, taxDistrictId)
    });
    
    if (!taxDistrict) {
      return res.status(404).json({
        success: false,
        message: 'Tax district not found'
      });
    }
    
    // Get tax codes associated with this district
    const taxCodeRelations = await db.select({
      relationId: taxCodeToTaxDistrict.id,
      taxCodeId: taxCodeToTaxDistrict.taxCodeId,
      percentage: taxCodeToTaxDistrict.percentage,
      isActive: taxCodeToTaxDistrict.isActive
    })
    .from(taxCodeToTaxDistrict)
    .where(eq(taxCodeToTaxDistrict.taxDistrictId, taxDistrictId));
    
    if (!taxCodeRelations.length) {
      return res.json({
        success: true,
        data: [],
        message: 'No tax codes associated with this tax district'
      });
    }
    
    // Get the tax code details for each relation
    const taxCodeIds = taxCodeRelations.map(relation => relation.taxCodeId);
    const taxCodeDetails = await db.query.taxCodes.findMany({
      where: db.and(
        db.inArray(taxCodes.id, taxCodeIds),
        eq(taxCodes.isActive, true)
      )
    });
    
    // Combine the tax code details with the relationship data
    const result = taxCodeRelations.map(relation => {
      const taxCodeDetail = taxCodeDetails.find(tc => tc.id === relation.taxCodeId);
      return {
        ...relation,
        taxCode: taxCodeDetail || null
      };
    });
    
    return res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('Error fetching tax codes for tax district:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch tax codes for tax district',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

// Get levies associated with a tax district
router.get('/:id/levies', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const taxDistrictId = parseInt(req.params.id);
    
    if (isNaN(taxDistrictId)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid tax district ID'
      });
    }
    
    // Verify tax district exists
    const taxDistrict = await db.query.taxDistricts.findFirst({
      where: eq(taxDistricts.id, taxDistrictId)
    });
    
    if (!taxDistrict) {
      return res.status(404).json({
        success: false,
        message: 'Tax district not found'
      });
    }
    
    // Get tax levies associated with this district
    const districtLevies = await db.query.levies.findMany({
      where: eq(levies.taxDistrictId, taxDistrictId),
      orderBy: [
        desc(levies.taxYear),
        asc(levies.name)
      ],
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
    
    return res.json({
      success: true,
      data: districtLevies
    });
  } catch (error) {
    console.error('Error fetching levies for tax district:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch levies for tax district',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

// Get a list of district types
router.get('/types/list', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    // Get unique district types
    const districtTypes = await db.selectDistinct({
      districtType: taxDistricts.districtType
    })
    .from(taxDistricts)
    .where(eq(taxDistricts.isActive, true));
    
    // Extract district types
    const types = districtTypes.map(type => type.districtType).filter(Boolean);
    
    return res.json({
      success: true,
      data: types
    });
  } catch (error) {
    console.error('Error fetching district types:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch district types',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

export default router;