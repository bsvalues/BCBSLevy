import { Router, Request, Response } from 'express';
import { eq, and, desc, asc, between, gte, lte, like, or } from 'drizzle-orm';
import { db } from '../index';
import {
  properties,
  taxDistricts,
  taxCodes
} from '@terrafusion/shared';

const router = Router();

/**
 * Search properties
 */
router.get('/search', async (req: Request, res: Response) => {
  try {
    const query = req.query.query as string;
    const districtId = parseInt(req.query.districtId as string);
    const limit = parseInt(req.query.limit as string) || 50;
    const offset = parseInt(req.query.offset as string) || 0;
    const sortBy = req.query.sortBy as string || 'propertyId';
    const sortOrder = req.query.sortOrder as string === 'desc' ? 'desc' : 'asc';
    
    // Build the search conditions
    const conditions = [];
    
    if (districtId) {
      conditions.push(eq(properties.taxDistrictId, districtId));
    }
    
    if (query) {
      conditions.push(
        or(
          like(properties.propertyId, `%${query}%`),
          like(properties.address, `%${query}%`),
          like(properties.ownerName, `%${query}%`)
        )
      );
    }
    
    // Execute the search query
    const propertiesResult = await db.query.properties.findMany({
      where: conditions.length > 0 ? and(...conditions) : undefined,
      limit,
      offset,
      orderBy: sortOrder === 'desc' 
        ? desc(properties[sortBy as keyof typeof properties]) 
        : asc(properties[sortBy as keyof typeof properties])
    });
    
    // Get total count for pagination
    const countResult = await db.select({ count: db.fn.count() })
      .from(properties)
      .where(conditions.length > 0 ? and(...conditions) : undefined);
    
    const totalCount = Number(countResult[0].count);
    
    return res.status(200).json({
      properties: propertiesResult,
      pagination: {
        total: totalCount,
        offset,
        limit,
        hasMore: offset + propertiesResult.length < totalCount
      }
    });
  } catch (error) {
    console.error('Error searching properties:', error);
    return res.status(500).json({ error: 'Failed to search properties' });
  }
});

/**
 * Get property by ID
 */
router.get('/properties/:id', async (req: Request, res: Response) => {
  try {
    const propertyId = parseInt(req.params.id);
    
    // Get the property
    const property = await db.query.properties.findFirst({
      where: eq(properties.id, propertyId)
    });
    
    if (!property) {
      return res.status(404).json({ error: 'Property not found' });
    }
    
    // Get district and tax code information
    const district = await db.query.taxDistricts.findFirst({
      where: eq(taxDistricts.id, property.taxDistrictId)
    });
    
    const taxCode = property.taxCodeId ? await db.query.taxCodes.findFirst({
      where: eq(taxCodes.id, property.taxCodeId)
    }) : null;
    
    // Construct the full property data
    const propertyData = {
      ...property,
      district: district ? {
        id: district.id,
        name: district.districtName,
        type: district.districtType
      } : null,
      taxCode: taxCode ? {
        id: taxCode.id,
        code: taxCode.code
      } : null
    };
    
    return res.status(200).json(propertyData);
  } catch (error) {
    console.error('Error fetching property:', error);
    return res.status(500).json({ error: 'Failed to fetch property' });
  }
});

/**
 * Get properties by district
 */
router.get('/by-district/:districtId', async (req: Request, res: Response) => {
  try {
    const districtId = parseInt(req.params.districtId);
    const limit = parseInt(req.query.limit as string) || 100;
    const offset = parseInt(req.query.offset as string) || 0;
    
    // Get properties for the district
    const propertiesResult = await db.query.properties.findMany({
      where: eq(properties.taxDistrictId, districtId),
      limit,
      offset,
      orderBy: asc(properties.propertyId)
    });
    
    // Get total count for pagination
    const countResult = await db.select({ count: db.fn.count() })
      .from(properties)
      .where(eq(properties.taxDistrictId, districtId));
    
    const totalCount = Number(countResult[0].count);
    
    // Get the district
    const district = await db.query.taxDistricts.findFirst({
      where: eq(taxDistricts.id, districtId)
    });
    
    if (!district) {
      return res.status(404).json({ error: 'District not found' });
    }
    
    // Calculate district summary statistics
    const totalAssessedValue = propertiesResult.reduce(
      (sum, property) => sum + (property.assessedValue || 0), 
      0
    );
    
    const averageAssessedValue = propertiesResult.length > 0 
      ? totalAssessedValue / propertiesResult.length 
      : 0;
    
    const summary = {
      districtId,
      districtName: district.districtName,
      districtType: district.districtType,
      propertyCount: totalCount,
      totalAssessedValue,
      averageAssessedValue,
      properties: propertiesResult,
      pagination: {
        total: totalCount,
        offset,
        limit,
        hasMore: offset + propertiesResult.length < totalCount
      }
    };
    
    return res.status(200).json(summary);
  } catch (error) {
    console.error('Error fetching properties by district:', error);
    return res.status(500).json({ error: 'Failed to fetch properties by district' });
  }
});

/**
 * Get property assessment history
 */
router.get('/properties/:id/history', async (req: Request, res: Response) => {
  try {
    const propertyId = parseInt(req.params.id);
    const startYear = parseInt(req.query.startYear as string) || (new Date().getFullYear() - 5);
    const endYear = parseInt(req.query.endYear as string) || new Date().getFullYear();
    
    // Get the property
    const property = await db.query.properties.findFirst({
      where: eq(properties.id, propertyId)
    });
    
    if (!property) {
      return res.status(404).json({ error: 'Property not found' });
    }
    
    // In a real implementation, we would fetch historical assessment data
    // For now, we'll generate simulated historical data
    const currentYear = new Date().getFullYear();
    const years = Array.from({ length: endYear - startYear + 1 }, (_, i) => startYear + i);
    
    const assessmentHistory = years.map(year => {
      const yearDiff = year - (currentYear - 5);
      // Simulate growth at average of 2% per year with some noise
      const growthFactor = Math.pow(1.02, yearDiff) * (0.95 + Math.random() * 0.1);
      const baseValue = property.assessedValue || 0;
      
      return {
        year,
        assessedValue: Math.round(baseValue * growthFactor),
        taxRate: 0, // Would be populated from historical tax rates
        taxAmount: 0 // Would be calculated based on historical rates
      };
    });
    
    // Calculate growth rates and tax amounts
    const historyWithGrowth = assessmentHistory.map((assessment, index) => {
      const previousYear = index > 0 ? assessmentHistory[index - 1] : null;
      const growthRate = previousYear 
        ? (assessment.assessedValue - previousYear.assessedValue) / previousYear.assessedValue * 100 
        : 0;
      
      // Assume a reasonable tax rate for simulation
      const taxRate = 0.025 - (Math.random() * 0.005); // Range around 2.5%
      const taxAmount = assessment.assessedValue * taxRate;
      
      return {
        ...assessment,
        growthRate,
        taxRate,
        taxAmount
      };
    });
    
    return res.status(200).json({
      property,
      history: historyWithGrowth,
      startYear,
      endYear
    });
  } catch (error) {
    console.error('Error fetching property history:', error);
    return res.status(500).json({ error: 'Failed to fetch property history' });
  }
});

export default router;