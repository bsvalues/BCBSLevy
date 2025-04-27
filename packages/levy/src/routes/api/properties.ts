import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { db } from '../../../../shared/db';
import { 
  properties, 
  propertyAssessments,
  propertyDetails,
  taxCodes
} from '../../../../shared/schema';
import { eq, and, like, ilike, desc, asc } from 'drizzle-orm';
import { AuthenticatedRequest, requireAuth } from '../../middleware/mockAuth';

const router = Router();

// Validation schema for property queries
const PropertyQuerySchema = z.object({
  parcelNumber: z.string().optional(),
  address: z.string().optional(),
  ownerName: z.string().optional(),
  taxCodeId: z.coerce.number().int().positive().optional(),
  page: z.coerce.number().int().positive().optional().default(1),
  limit: z.coerce.number().int().positive().max(100).optional().default(20),
  sortBy: z.enum(['parcelNumber', 'address', 'ownerName', 'assessedValue', 'createdAt']).optional().default('parcelNumber'),
  sortDir: z.enum(['asc', 'desc']).optional().default('asc'),
});

// Get all properties with optional filtering
router.get('/', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const parsedQuery = PropertyQuerySchema.safeParse(req.query);
    
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
    
    if (query.parcelNumber) {
      whereConditions.push(ilike(properties.parcelNumber, `%${query.parcelNumber}%`));
    }
    
    if (query.address) {
      whereConditions.push(ilike(properties.address, `%${query.address}%`));
    }
    
    if (query.ownerName) {
      whereConditions.push(ilike(properties.ownerName, `%${query.ownerName}%`));
    }
    
    if (query.taxCodeId) {
      whereConditions.push(eq(properties.taxCodeId, query.taxCodeId));
    }
    
    // Execute query with filtering, sorting, and pagination
    const propertiesList = await db.query.properties.findMany({
      where: whereConditions.length > 0 ? and(...whereConditions) : undefined,
      orderBy: query.sortDir === 'asc' 
        ? asc(properties[query.sortBy as keyof typeof properties])
        : desc(properties[query.sortBy as keyof typeof properties]),
      offset,
      limit: query.limit,
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
    
    // Get total count for pagination
    const countResult = await db.select({ count: db.fn.count() }).from(properties)
      .where(whereConditions.length > 0 ? and(...whereConditions) : undefined);
    
    const totalCount = Number(countResult[0].count);
    const totalPages = Math.ceil(totalCount / query.limit);
    
    return res.json({
      success: true,
      data: propertiesList,
      pagination: {
        page: query.page,
        limit: query.limit,
        totalItems: totalCount,
        totalPages
      }
    });
  } catch (error) {
    console.error('Error fetching properties:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch properties',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

// Get a specific property by ID
router.get('/:id', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const propertyId = parseInt(req.params.id);
    
    if (isNaN(propertyId)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid property ID'
      });
    }
    
    const property = await db.query.properties.findFirst({
      where: eq(properties.id, propertyId),
      with: {
        taxCode: true,
        details: true
      }
    });
    
    if (!property) {
      return res.status(404).json({
        success: false,
        message: 'Property not found'
      });
    }
    
    return res.json({
      success: true,
      data: property
    });
  } catch (error) {
    console.error('Error fetching property:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch property',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

// Get assessment history for a property
router.get('/:id/assessments', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const propertyId = parseInt(req.params.id);
    
    if (isNaN(propertyId)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid property ID'
      });
    }
    
    // Verify property exists
    const property = await db.query.properties.findFirst({
      where: eq(properties.id, propertyId)
    });
    
    if (!property) {
      return res.status(404).json({
        success: false,
        message: 'Property not found'
      });
    }
    
    // Get assessment history
    const assessments = await db.query.propertyAssessments.findMany({
      where: eq(propertyAssessments.propertyId, propertyId),
      orderBy: desc(propertyAssessments.year)
    });
    
    return res.json({
      success: true,
      data: assessments
    });
  } catch (error) {
    console.error('Error fetching property assessments:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch property assessments',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

// Get property details
router.get('/:id/details', requireAuth, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const propertyId = parseInt(req.params.id);
    
    if (isNaN(propertyId)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid property ID'
      });
    }
    
    // Verify property exists
    const property = await db.query.properties.findFirst({
      where: eq(properties.id, propertyId)
    });
    
    if (!property) {
      return res.status(404).json({
        success: false,
        message: 'Property not found'
      });
    }
    
    // Get property details
    const details = await db.query.propertyDetails.findFirst({
      where: eq(propertyDetails.propertyId, propertyId)
    });
    
    if (!details) {
      return res.status(404).json({
        success: false,
        message: 'Property details not found'
      });
    }
    
    return res.json({
      success: true,
      data: details
    });
  } catch (error) {
    console.error('Error fetching property details:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch property details',
      error: process.env.NODE_ENV === 'development' ? error : undefined
    });
  }
});

export default router;