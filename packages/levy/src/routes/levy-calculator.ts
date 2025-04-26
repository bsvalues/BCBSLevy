import { Router, Request, Response } from 'express';
import { eq, and } from 'drizzle-orm';
import { db } from '../index';
import { 
  taxDistricts, 
  levyRates, 
  taxCodes,
  taxCodeHistoricalRates,
  levyScenarios
} from '@terrafusion/shared';

const router = Router();

/**
 * Get all tax districts
 */
router.get('/districts', async (req: Request, res: Response) => {
  try {
    const year = parseInt(req.query.year as string) || new Date().getFullYear();
    
    const districts = await db.query.taxDistricts.findMany({
      where: eq(taxDistricts.year, year),
      orderBy: taxDistricts.districtName
    });
    
    return res.status(200).json({ districts });
  } catch (error) {
    console.error('Error fetching districts:', error);
    return res.status(500).json({ error: 'Failed to fetch tax districts' });
  }
});

/**
 * Get district by ID
 */
router.get('/districts/:id', async (req: Request, res: Response) => {
  try {
    const districtId = parseInt(req.params.id);
    const year = parseInt(req.query.year as string) || new Date().getFullYear();
    
    const district = await db.query.taxDistricts.findFirst({
      where: and(
        eq(taxDistricts.id, districtId),
        eq(taxDistricts.year, year)
      )
    });
    
    if (!district) {
      return res.status(404).json({ error: 'Tax district not found' });
    }
    
    return res.status(200).json({ district });
  } catch (error) {
    console.error('Error fetching district:', error);
    return res.status(500).json({ error: 'Failed to fetch tax district' });
  }
});

/**
 * Get levy rates for a district
 */
router.get('/districts/:id/rates', async (req: Request, res: Response) => {
  try {
    const districtId = parseInt(req.params.id);
    const year = parseInt(req.query.year as string) || new Date().getFullYear();
    
    const rates = await db.query.levyRates.findMany({
      where: and(
        eq(levyRates.taxDistrictId, districtId),
        eq(levyRates.year, year)
      )
    });
    
    return res.status(200).json({ rates });
  } catch (error) {
    console.error('Error fetching rates:', error);
    return res.status(500).json({ error: 'Failed to fetch levy rates' });
  }
});

/**
 * Get tax codes for a district
 */
router.get('/districts/:id/tax-codes', async (req: Request, res: Response) => {
  try {
    const districtId = parseInt(req.params.id);
    const year = parseInt(req.query.year as string) || new Date().getFullYear();
    
    const codes = await db.query.taxCodes.findMany({
      where: and(
        eq(taxCodes.taxDistrictId, districtId),
        eq(taxCodes.year, year)
      )
    });
    
    return res.status(200).json({ taxCodes: codes });
  } catch (error) {
    console.error('Error fetching tax codes:', error);
    return res.status(500).json({ error: 'Failed to fetch tax codes' });
  }
});

/**
 * Calculate levy rate
 */
router.post('/calculate', async (req: Request, res: Response) => {
  try {
    const { 
      taxDistrictId, 
      levyAmount, 
      assessedValue,
      year = new Date().getFullYear()
    } = req.body;
    
    if (!taxDistrictId || !levyAmount || !assessedValue) {
      return res.status(400).json({ 
        error: 'Missing required parameters: taxDistrictId, levyAmount, assessedValue' 
      });
    }
    
    // Calculate levy rate based on amount and assessed value
    const levyRate = (parseFloat(levyAmount) / parseFloat(assessedValue)) * 1000;
    
    return res.status(200).json({
      taxDistrictId,
      levyAmount: parseFloat(levyAmount),
      assessedValue: parseFloat(assessedValue),
      levyRate,
      year
    });
  } catch (error) {
    console.error('Error calculating levy rate:', error);
    return res.status(500).json({ error: 'Failed to calculate levy rate' });
  }
});

/**
 * Create a new levy scenario
 */
router.post('/scenarios', async (req: Request, res: Response) => {
  try {
    const { 
      userId,
      name,
      description,
      taxDistrictId,
      baseYear,
      targetYear,
      levyAmount,
      assessedValueChange,
      newConstructionValue,
      annexationValue,
      isPublic = false
    } = req.body;
    
    if (!userId || !name || !taxDistrictId || !baseYear || !targetYear) {
      return res.status(400).json({ 
        error: 'Missing required parameters' 
      });
    }
    
    // Insert the scenario into the database
    const [scenario] = await db.insert(levyScenarios).values({
      userId,
      name,
      description,
      taxDistrictId,
      baseYear,
      targetYear,
      levyAmount,
      assessedValueChange: assessedValueChange || 0,
      newConstructionValue: newConstructionValue || 0,
      annexationValue: annexationValue || 0,
      isPublic,
      status: 'DRAFT',
      year: targetYear,
      createdById: userId,
      updatedById: userId
    }).returning();
    
    return res.status(201).json({ scenario });
  } catch (error) {
    console.error('Error creating scenario:', error);
    return res.status(500).json({ error: 'Failed to create levy scenario' });
  }
});

/**
 * Get levy scenarios for a user
 */
router.get('/scenarios', async (req: Request, res: Response) => {
  try {
    const userId = parseInt(req.query.userId as string);
    
    if (!userId) {
      return res.status(400).json({ error: 'Missing required parameter: userId' });
    }
    
    const scenarios = await db.query.levyScenarios.findMany({
      where: eq(levyScenarios.userId, userId),
      orderBy: [levyScenarios.targetYear, levyScenarios.name]
    });
    
    return res.status(200).json({ scenarios });
  } catch (error) {
    console.error('Error fetching scenarios:', error);
    return res.status(500).json({ error: 'Failed to fetch levy scenarios' });
  }
});

export default router;