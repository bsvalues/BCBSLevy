import { Router, Request, Response } from 'express';
import { eq, and, desc, asc, between, gte, lte } from 'drizzle-orm';
import { db } from '../index';
import {
  taxDistricts,
  taxCodes,
  taxCodeHistoricalRates,
  properties,
  levyRates
} from '@terrafusion/shared';

const router = Router();

/**
 * Get historical rate trends
 */
router.get('/trends', async (req: Request, res: Response) => {
  try {
    const districtId = parseInt(req.query.districtId as string);
    const startYear = parseInt(req.query.startYear as string) || (new Date().getFullYear() - 5);
    const endYear = parseInt(req.query.endYear as string) || new Date().getFullYear();
    
    if (!districtId) {
      return res.status(400).json({ error: 'Missing required parameter: districtId' });
    }
    
    // Get tax codes for the district
    const codes = await db.query.taxCodes.findMany({
      where: eq(taxCodes.taxDistrictId, districtId)
    });
    
    if (codes.length === 0) {
      return res.status(404).json({ error: 'No tax codes found for the specified district' });
    }
    
    const codeIds = codes.map(code => code.id);
    
    // Get historical rates for the tax codes
    const historicalRates = await db.query.taxCodeHistoricalRates.findMany({
      where: and(
        taxCodeHistoricalRates.taxCodeId in codeIds,
        gte(taxCodeHistoricalRates.year, startYear),
        lte(taxCodeHistoricalRates.year, endYear)
      ),
      orderBy: [
        taxCodeHistoricalRates.taxCodeId,
        taxCodeHistoricalRates.year
      ]
    });
    
    // Group rates by tax code for easier consumption
    const ratesByCode = historicalRates.reduce((acc, rate) => {
      if (!acc[rate.taxCodeId]) {
        acc[rate.taxCodeId] = {
          taxCodeId: rate.taxCodeId,
          code: codes.find(c => c.id === rate.taxCodeId)?.code || 'Unknown',
          rates: []
        };
      }
      
      acc[rate.taxCodeId].rates.push({
        year: rate.year,
        levyRate: rate.levyRate,
        levyAmount: rate.levyAmount,
        totalAssessedValue: rate.totalAssessedValue
      });
      
      return acc;
    }, {} as Record<number, any>);
    
    // Format the data for time series visualization
    const trends = {
      taxCodes: codes,
      ratesByCode: Object.values(ratesByCode),
      startYear,
      endYear,
      years: Array.from({ length: endYear - startYear + 1 }, (_, i) => startYear + i)
    };
    
    return res.status(200).json(trends);
  } catch (error) {
    console.error('Error fetching historical trends:', error);
    return res.status(500).json({ error: 'Failed to fetch historical trends' });
  }
});

/**
 * Get comparative analysis data
 */
router.get('/compare-districts', async (req: Request, res: Response) => {
  try {
    const districtIds = req.query.districtIds as string;
    const year = parseInt(req.query.year as string) || new Date().getFullYear();
    
    if (!districtIds) {
      return res.status(400).json({ error: 'Missing required parameter: districtIds' });
    }
    
    const ids = districtIds.split(',').map(id => parseInt(id));
    
    // Get district data
    const districts = await db.query.taxDistricts.findMany({
      where: taxDistricts.id in ids
    });
    
    if (districts.length === 0) {
      return res.status(404).json({ error: 'No districts found with the specified IDs' });
    }
    
    // Get rates for each district
    const allRates = await db.query.levyRates.findMany({
      where: and(
        levyRates.taxDistrictId in ids,
        eq(levyRates.year, year)
      )
    });
    
    // Get tax codes for all districts
    const taxCodesByDistrict = await db.query.taxCodes.findMany({
      where: and(
        taxCodes.taxDistrictId in ids,
        eq(taxCodes.year, year)
      )
    });
    
    // Group rates by district
    const ratesByDistrict = ids.reduce((acc, districtId) => {
      const districtRates = allRates.filter(rate => rate.taxDistrictId === districtId);
      const districtTaxCodes = taxCodesByDistrict.filter(code => code.taxDistrictId === districtId);
      const district = districts.find(d => d.id === districtId);
      
      if (district) {
        acc[districtId] = {
          district: {
            id: district.id,
            name: district.districtName,
            type: district.districtType
          },
          rates: districtRates,
          taxCodes: districtTaxCodes,
          averageRate: calculateAverageRate(districtRates),
          totalAssessedValue: calculateTotalAssessedValue(districtTaxCodes)
        };
      }
      
      return acc;
    }, {} as Record<number, any>);
    
    return res.status(200).json({
      year,
      districtComparisons: Object.values(ratesByDistrict)
    });
  } catch (error) {
    console.error('Error comparing districts:', error);
    return res.status(500).json({ error: 'Failed to compare districts' });
  }
});

/**
 * Get property value trends
 */
router.get('/property-trends', async (req: Request, res: Response) => {
  try {
    const districtId = parseInt(req.query.districtId as string);
    const startYear = parseInt(req.query.startYear as string) || (new Date().getFullYear() - 5);
    const endYear = parseInt(req.query.endYear as string) || new Date().getFullYear();
    const limit = parseInt(req.query.limit as string) || 500;
    
    if (!districtId) {
      return res.status(400).json({ error: 'Missing required parameter: districtId' });
    }
    
    // Get properties for the district
    const propertiesResult = await db.query.properties.findMany({
      where: eq(properties.taxDistrictId, districtId),
      limit
    });
    
    if (propertiesResult.length === 0) {
      return res.status(404).json({ error: 'No properties found for the specified district' });
    }
    
    // Get property IDs
    const propertyIds = propertiesResult.map(property => property.id);
    
    // Calculate trends
    const years = Array.from({ length: endYear - startYear + 1 }, (_, i) => startYear + i);
    const propertyValueTrends = {
      years,
      properties: propertiesResult,
      trends: {
        averageValue: years.map(year => ({
          year,
          value: calculateAveragePropertyValue(propertiesResult, year)
        })),
        totalValue: years.map(year => ({
          year,
          value: calculateTotalPropertyValue(propertiesResult, year)
        })),
        growthRate: years.map((year, index) => {
          if (index === 0) return { year, value: 0 };
          
          const currentValue = calculateTotalPropertyValue(propertiesResult, year);
          const previousValue = calculateTotalPropertyValue(propertiesResult, year - 1);
          
          return {
            year,
            value: previousValue ? (currentValue - previousValue) / previousValue * 100 : 0
          };
        })
      }
    };
    
    return res.status(200).json(propertyValueTrends);
  } catch (error) {
    console.error('Error fetching property trends:', error);
    return res.status(500).json({ error: 'Failed to fetch property trends' });
  }
});

/**
 * Calculate average rate from levy rates
 */
function calculateAverageRate(rates: any[]): number {
  if (rates.length === 0) return 0;
  
  const sum = rates.reduce((total, rate) => total + rate.rate, 0);
  return sum / rates.length;
}

/**
 * Calculate total assessed value from tax codes
 */
function calculateTotalAssessedValue(taxCodes: any[]): number {
  if (taxCodes.length === 0) return 0;
  
  return taxCodes.reduce((total, code) => total + (code.assessedValue || 0), 0);
}

/**
 * Calculate average property value for a specific year
 */
function calculateAveragePropertyValue(properties: any[], year: number): number {
  if (properties.length === 0) return 0;
  
  // In a real implementation, this would use historical property values
  // For now, we'll use a simple simulation based on the current value
  const values = properties.map(property => {
    const baseValue = property.assessedValue || 0;
    const yearDiff = year - (new Date().getFullYear() - 5);
    // Assume 2% annual growth on average, with some randomization
    const growthFactor = Math.pow(1.02, yearDiff) * (0.95 + Math.random() * 0.1);
    return baseValue * growthFactor;
  });
  
  const sum = values.reduce((total, value) => total + value, 0);
  return sum / properties.length;
}

/**
 * Calculate total property value for a specific year
 */
function calculateTotalPropertyValue(properties: any[], year: number): number {
  if (properties.length === 0) return 0;
  
  // In a real implementation, this would use historical property values
  // For now, we'll use a simple simulation based on the current value
  return properties.reduce((total, property) => {
    const baseValue = property.assessedValue || 0;
    const yearDiff = year - (new Date().getFullYear() - 5);
    // Assume 2% annual growth on average, with some randomization
    const growthFactor = Math.pow(1.02, yearDiff) * (0.95 + Math.random() * 0.1);
    return total + (baseValue * growthFactor);
  }, 0);
}

export default router;