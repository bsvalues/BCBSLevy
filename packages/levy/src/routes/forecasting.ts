import express, { Request, Response, Router } from 'express';
import { eq, and, gte, lte, desc, sql } from 'drizzle-orm';
import { db } from '../index';
import { 
  taxCodes,
  taxCodeHistoricalRates,
  properties
} from '@terrafusion/shared';

// Create router
const router = Router();

/**
 * Get historical rates for forecasting
 */
router.get('/historical-rates', async (req: Request, res: Response) => {
  try {
    const { taxCodeId, years } = req.query;
    
    // If a specific tax code is requested
    if (taxCodeId) {
      // Get the tax code first to verify it exists
      const code = await db.select()
        .from(taxCodes)
        .where(eq(taxCodes.id, parseInt(taxCodeId as string)))
        .limit(1);
      
      if (!code.length) {
        return res.status(404).json({
          success: false,
          message: 'Tax code not found'
        });
      }
      
      // Get historical rates for this tax code
      const rates = await db.select()
        .from(taxCodeHistoricalRates)
        .where(eq(taxCodeHistoricalRates.taxCodeId, parseInt(taxCodeId as string)))
        .orderBy(desc(taxCodeHistoricalRates.year));
      
      // Calculate year-over-year changes for trend analysis
      const ratesWithChanges = rates.map((rate, index) => {
        if (index === rates.length - 1) {
          return { ...rate, changePercent: 0 };
        }
        
        const prevRate = rates[index + 1];
        const changePercent = ((rate.levyRate - prevRate.levyRate) / prevRate.levyRate) * 100;
        
        return {
          ...rate,
          changePercent: parseFloat(changePercent.toFixed(2))
        };
      });
      
      // Calculate average rate change
      const avgRateChange = ratesWithChanges
        .filter(r => r.changePercent !== 0)
        .reduce((acc, rate) => acc + rate.changePercent, 0) / 
        (ratesWithChanges.length - 1 || 1);
      
      return res.json({
        success: true,
        taxCodeId: parseInt(taxCodeId as string),
        rates: ratesWithChanges,
        trends: {
          avgYearlyRateChangePercent: parseFloat(avgRateChange.toFixed(2)),
          minRate: Math.min(...rates.map(r => r.levyRate)),
          maxRate: Math.max(...rates.map(r => r.levyRate)),
          volatility: calculateVolatility(rates.map(r => r.levyRate))
        }
      });
    } 
    // Get rates for all tax codes if no specific one is requested
    else {
      const allCodes = await db.select()
        .from(taxCodes)
        .limit(100);  // Limit to prevent excessive data
        
      // For each tax code, get the most recent historical rate
      const codePromises = allCodes.map(async code => {
        const rates = await db.select()
          .from(taxCodeHistoricalRates)
          .where(eq(taxCodeHistoricalRates.taxCodeId, code.id))
          .orderBy(desc(taxCodeHistoricalRates.year))
          .limit(1);
          
        return {
          ...code,
          currentRate: rates.length > 0 ? rates[0].levyRate : null,
          currentYear: rates.length > 0 ? rates[0].year : null
        };
      });
      
      const codesWithRates = await Promise.all(codePromises);
      
      return res.json({
        success: true,
        taxCodes: codesWithRates
      });
    }
  } catch (error) {
    console.error('Error fetching historical rates:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch historical rates'
    });
  }
});

/**
 * Generate levy forecast
 */
router.post('/generate', async (req: Request, res: Response) => {
  try {
    const { 
      taxCodeId, 
      years = 5,
      baseYear,
      inflationRate = 0.02,
      populationGrowthRate = 0.01,
      assessedValueGrowthRate = 0.03,
      newConstructionRate = 0.02
    } = req.body;
    
    // Input validation
    if (!taxCodeId) {
      return res.status(400).json({
        success: false,
        message: 'Tax code ID is required'
      });
    }
    
    // Get the tax code and its most recent data
    const code = await db.select()
      .from(taxCodes)
      .where(eq(taxCodes.id, taxCodeId))
      .limit(1);
      
    if (!code.length) {
      return res.status(404).json({
        success: false,
        message: 'Tax code not found'
      });
    }
    
    const taxCode = code[0];
    
    // Get historical rates to establish baseline and trends
    const rates = await db.select()
      .from(taxCodeHistoricalRates)
      .where(eq(taxCodeHistoricalRates.taxCodeId, taxCodeId))
      .orderBy(desc(taxCodeHistoricalRates.year));
    
    if (!rates.length) {
      return res.status(400).json({
        success: false,
        message: 'No historical data available for forecasting'
      });
    }
    
    // Determine starting point for forecast
    const mostRecentRate = rates[0];
    const startYear = baseYear || mostRecentRate.year;
    const startLevyRate = mostRecentRate.levyRate;
    const startAssessedValue = mostRecentRate.totalAssessedValue || taxCode.totalAssessedValue;
    
    // Calculate historical trends for more accurate forecasting
    const yearlyRateChanges = rates.slice(0, -1).map((rate, i) => {
      return (rate.levyRate - rates[i + 1].levyRate) / rates[i + 1].levyRate;
    });
    
    const avgHistoricalRateChange = yearlyRateChanges.length > 0 ? 
      yearlyRateChanges.reduce((a, b) => a + b, 0) / yearlyRateChanges.length : 
      inflationRate;
    
    // Generate forecast for each year
    const forecast = [];
    let currentYear = startYear;
    let currentLevyRate = startLevyRate;
    let currentAssessedValue = startAssessedValue;
    let currentLevyAmount = currentLevyRate * currentAssessedValue / 100;
    
    for (let i = 0; i < years; i++) {
      currentYear++;
      
      // Apply growth factors
      const assessedValueGrowth = currentAssessedValue * assessedValueGrowthRate;
      const newConstruction = currentAssessedValue * newConstructionRate;
      currentAssessedValue += assessedValueGrowth + newConstruction;
      
      // Apply inflation and historical trends to levy rate
      const rateChange = (inflationRate + avgHistoricalRateChange) / 2;
      currentLevyRate *= (1 + rateChange);
      
      // Calculate new levy amount
      currentLevyAmount = currentLevyRate * currentAssessedValue / 100;
      
      // Add to forecast
      forecast.push({
        year: currentYear,
        levyRate: parseFloat(currentLevyRate.toFixed(4)),
        assessedValue: Math.round(currentAssessedValue),
        levyAmount: Math.round(currentLevyAmount),
        assessedValueGrowth: Math.round(assessedValueGrowth),
        newConstruction: Math.round(newConstruction)
      });
    }
    
    return res.json({
      success: true,
      taxCodeId,
      forecast,
      parameters: {
        baseYear: startYear,
        years,
        inflationRate,
        assessedValueGrowthRate,
        newConstructionRate,
        historicalRateChange: parseFloat(avgHistoricalRateChange.toFixed(4))
      },
      confidence: {
        high: 0.95,
        medium: 0.9,
        low: 0.8
      }
    });
  } catch (error) {
    console.error('Error generating forecast:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to generate forecast'
    });
  }
});

/**
 * Calculate volatility from a series of values
 */
function calculateVolatility(values: number[]): number {
  if (values.length < 2) return 0;
  
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
  return parseFloat(Math.sqrt(variance).toFixed(4));
}

export default router;