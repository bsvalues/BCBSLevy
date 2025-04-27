import express, { Request, Response, Router } from 'express';
import { eq, and, desc, sql } from 'drizzle-orm';
import { db } from '../index';
import { 
  taxDistricts,
  taxCodes,
  levyRates,
  levyScenarios,
  properties
} from '@terrafusion/shared';

// Create router
const router = Router();

/**
 * Get all tax districts
 */
router.get('/districts', async (req: Request, res: Response) => {
  try {
    const districts = await db.select().from(taxDistricts);
    
    return res.json({
      success: true,
      districts
    });
  } catch (error) {
    console.error('Error fetching tax districts:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch tax districts'
    });
  }
});

/**
 * Get tax district by ID
 */
router.get('/districts/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const district = await db.select()
      .from(taxDistricts)
      .where(eq(taxDistricts.id, parseInt(id)))
      .limit(1);
    
    if (!district.length) {
      return res.status(404).json({
        success: false,
        message: 'Tax district not found'
      });
    }
    
    return res.json({
      success: true,
      district: district[0]
    });
  } catch (error) {
    console.error(`Error fetching tax district ${req.params.id}:`, error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch tax district'
    });
  }
});

/**
 * Get levy rates for a tax district
 */
router.get('/districts/:id/rates', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const rates = await db.select()
      .from(levyRates)
      .where(eq(levyRates.taxDistrictId, parseInt(id)));
    
    return res.json({
      success: true,
      rates
    });
  } catch (error) {
    console.error(`Error fetching levy rates for district ${req.params.id}:`, error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch levy rates'
    });
  }
});

/**
 * Get tax codes for a tax district
 */
router.get('/districts/:id/tax-codes', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const codes = await db.select()
      .from(taxCodes)
      .where(eq(taxCodes.taxDistrictId, parseInt(id)));
    
    return res.json({
      success: true,
      codes
    });
  } catch (error) {
    console.error(`Error fetching tax codes for district ${req.params.id}:`, error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch tax codes'
    });
  }
});

/**
 * Calculate levy for a tax district
 */
router.post('/calculate', async (req: Request, res: Response) => {
  try {
    const { 
      taxDistrictId, 
      year, 
      priorYearLevyAmount,
      assessedValueChange,
      newConstructionValue,
      annexationValue,
      inflationRate
    } = req.body;
    
    // Input validation
    if (!taxDistrictId || !year || priorYearLevyAmount === undefined) {
      return res.status(400).json({
        success: false,
        message: 'Missing required parameters'
      });
    }
    
    // Get district properties for calculation
    const properties = await db.select({
      totalAssessedValue: sql<number>`SUM(${taxCodes.totalAssessedValue})`
    })
    .from(taxCodes)
    .where(eq(taxCodes.taxDistrictId, taxDistrictId));
    
    const totalAssessedValue = properties[0]?.totalAssessedValue || 0;
    
    // Perform levy calculation
    const limitFactor = 1 + (inflationRate || 0.01); // Default 1% inflation
    const statutoryMaximum = priorYearLevyAmount * limitFactor;
    
    // Apply assessed value changes
    const adjustedAssessedValue = totalAssessedValue + 
      (newConstructionValue || 0) + 
      (annexationValue || 0);
    
    // Calculate effective rate
    const effectiveRate = (priorYearLevyAmount / totalAssessedValue) * 100;
    
    // Calculate new levy amount
    const calculatedLevyAmount = Math.min(
      statutoryMaximum,
      adjustedAssessedValue * (effectiveRate / 100)
    );
    
    return res.json({
      success: true,
      result: {
        taxDistrictId,
        year,
        priorYearLevyAmount,
        totalAssessedValue,
        adjustedAssessedValue,
        statutoryMaximum,
        calculatedLevyAmount,
        effectiveRate
      }
    });
  } catch (error) {
    console.error('Error calculating levy:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to calculate levy'
    });
  }
});

/**
 * Save a levy scenario
 */
router.post('/scenarios', async (req: Request, res: Response) => {
  try {
    const { 
      name,
      description,
      taxDistrictId,
      year,
      priorYearLevyAmount,
      targetLevyAmount,
      assessedValueChange,
      newConstructionValue,
      annexationValue,
      inflationRate,
      userId
    } = req.body;
    
    // Input validation
    if (!name || !taxDistrictId || !year || !userId) {
      return res.status(400).json({
        success: false,
        message: 'Missing required parameters'
      });
    }
    
    // Create scenario
    const result = await db.insert(levyScenarios).values({
      name,
      description,
      taxDistrictId,
      year,
      priorYearLevyAmount,
      targetLevyAmount,
      assessedValueChange,
      newConstructionValue,
      annexationValue,
      inflationRate,
      userId,
      createdAt: new Date(),
      updatedAt: new Date()
    }).returning();
    
    return res.json({
      success: true,
      scenario: result[0]
    });
  } catch (error) {
    console.error('Error saving levy scenario:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to save levy scenario'
    });
  }
});

export default router;