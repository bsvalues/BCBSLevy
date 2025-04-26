import { Router, Request, Response } from 'express';
import { eq, and, gte, lte, desc } from 'drizzle-orm';
import { db } from '../index';
import { 
  taxDistricts, 
  taxCodes, 
  taxCodeHistoricalRates 
} from '@terrafusion/shared';

const router = Router();

/**
 * Get historical rates for forecasting
 */
router.get('/historical-rates', async (req: Request, res: Response) => {
  try {
    const taxDistrictId = parseInt(req.query.taxDistrictId as string);
    const startYear = parseInt(req.query.startYear as string) || (new Date().getFullYear() - 5);
    const endYear = parseInt(req.query.endYear as string) || new Date().getFullYear();
    
    if (!taxDistrictId) {
      return res.status(400).json({ error: 'Missing required parameter: taxDistrictId' });
    }
    
    // Get tax codes for the district
    const codes = await db.query.taxCodes.findMany({
      where: eq(taxCodes.taxDistrictId, taxDistrictId),
      orderBy: taxCodes.code
    });
    
    const codeIds = codes.map(code => code.id);
    
    // Get historical rates for these tax codes
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
    
    // Group by tax code and year for easier processing
    const ratesByCodeAndYear = historicalRates.reduce((acc, rate) => {
      if (!acc[rate.taxCodeId]) {
        acc[rate.taxCodeId] = {};
      }
      acc[rate.taxCodeId][rate.year] = rate;
      return acc;
    }, {} as Record<number, Record<number, typeof historicalRates[0]>>);
    
    return res.status(200).json({
      taxCodes: codes,
      historicalRates: ratesByCodeAndYear,
      startYear,
      endYear
    });
  } catch (error) {
    console.error('Error fetching historical rates:', error);
    return res.status(500).json({ error: 'Failed to fetch historical rates' });
  }
});

/**
 * Generate forecast based on historical data
 */
router.post('/generate', async (req: Request, res: Response) => {
  try {
    const {
      taxDistrictId,
      forecastYears = 3,
      method = 'linear', // 'linear', 'average', 'weighted', 'custom'
      customWeights,
      baseYear = new Date().getFullYear(),
      parameters = {}
    } = req.body;
    
    if (!taxDistrictId) {
      return res.status(400).json({ error: 'Missing required parameter: taxDistrictId' });
    }
    
    // Get historical data for the district
    const startYear = baseYear - 5;
    const endYear = baseYear;
    
    // Get tax codes for the district
    const codes = await db.query.taxCodes.findMany({
      where: eq(taxCodes.taxDistrictId, taxDistrictId)
    });
    
    const codeIds = codes.map(code => code.id);
    
    // Get historical rates
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
    
    // Calculate forecasts based on method
    const forecasts = generateForecasts(
      codes,
      historicalRates,
      forecastYears,
      method,
      customWeights,
      baseYear,
      parameters
    );
    
    return res.status(200).json({
      forecasts,
      method,
      baseYear,
      forecastYears,
      parameters
    });
  } catch (error) {
    console.error('Error generating forecasts:', error);
    return res.status(500).json({ error: 'Failed to generate forecasts' });
  }
});

/**
 * Helper function to generate forecasts based on historical data
 */
function generateForecasts(
  taxCodes: any[],
  historicalRates: any[],
  forecastYears: number,
  method: string,
  customWeights: any,
  baseYear: number,
  parameters: any
) {
  // Group historical rates by tax code
  const ratesByCode = historicalRates.reduce((acc, rate) => {
    if (!acc[rate.taxCodeId]) {
      acc[rate.taxCodeId] = [];
    }
    acc[rate.taxCodeId].push(rate);
    return acc;
  }, {} as Record<number, any[]>);
  
  const forecasts: any = {};
  
  // Generate forecasts for each tax code
  taxCodes.forEach(code => {
    const codeRates = ratesByCode[code.id] || [];
    const codeForecast = [];
    
    // Sort rates by year
    codeRates.sort((a, b) => a.year - b.year);
    
    // Generate forecast for future years
    for (let i = 1; i <= forecastYears; i++) {
      const forecastYear = baseYear + i;
      let forecastRate;
      
      switch (method) {
        case 'linear':
          forecastRate = calculateLinearForecast(codeRates, forecastYear);
          break;
        case 'average':
          forecastRate = calculateAverageForecast(codeRates);
          break;
        case 'weighted':
          forecastRate = calculateWeightedForecast(codeRates, customWeights);
          break;
        case 'custom':
          forecastRate = calculateCustomForecast(codeRates, parameters);
          break;
        default:
          forecastRate = calculateLinearForecast(codeRates, forecastYear);
      }
      
      codeForecast.push({
        year: forecastYear,
        levyRate: forecastRate,
        confidence: calculateConfidence(codeRates, method, forecastYear)
      });
    }
    
    forecasts[code.id] = codeForecast;
  });
  
  return forecasts;
}

/**
 * Calculate linear regression forecast
 */
function calculateLinearForecast(rates: any[], targetYear: number): number {
  if (rates.length < 2) {
    return rates.length === 1 ? rates[0].levyRate : 0;
  }
  
  // Simple linear regression
  const n = rates.length;
  const xValues = rates.map(r => r.year);
  const yValues = rates.map(r => r.levyRate);
  
  const xMean = xValues.reduce((sum, x) => sum + x, 0) / n;
  const yMean = yValues.reduce((sum, y) => sum + y, 0) / n;
  
  let numerator = 0;
  let denominator = 0;
  
  for (let i = 0; i < n; i++) {
    numerator += (xValues[i] - xMean) * (yValues[i] - yMean);
    denominator += (xValues[i] - xMean) * (xValues[i] - xMean);
  }
  
  const slope = denominator !== 0 ? numerator / denominator : 0;
  const intercept = yMean - (slope * xMean);
  
  // Calculate forecast using y = mx + b
  const forecast = slope * targetYear + intercept;
  
  // Ensure forecast is not negative
  return Math.max(0, forecast);
}

/**
 * Calculate average forecast
 */
function calculateAverageForecast(rates: any[]): number {
  if (rates.length === 0) return 0;
  
  const sum = rates.reduce((total, rate) => total + rate.levyRate, 0);
  return sum / rates.length;
}

/**
 * Calculate weighted average forecast
 */
function calculateWeightedForecast(rates: any[], weights: any): number {
  if (rates.length === 0) return 0;
  
  // Default weights give more importance to recent years
  const defaultWeights = rates.map((_, index) => index + 1);
  const actualWeights = weights || defaultWeights;
  
  let weightedSum = 0;
  let totalWeight = 0;
  
  // Calculate weighted sum
  rates.forEach((rate, index) => {
    const weight = index < actualWeights.length ? actualWeights[index] : 1;
    weightedSum += rate.levyRate * weight;
    totalWeight += weight;
  });
  
  return totalWeight > 0 ? weightedSum / totalWeight : 0;
}

/**
 * Calculate custom forecast based on parameters
 */
function calculateCustomForecast(rates: any[], parameters: any): number {
  // Implement custom forecast logic based on parameters
  // This is a placeholder implementation
  const baseRate = calculateAverageForecast(rates);
  const growthFactor = parameters.growthFactor || 1.02;
  
  return baseRate * growthFactor;
}

/**
 * Calculate confidence score for the forecast
 */
function calculateConfidence(rates: any[], method: string, forecastYear: number): number {
  if (rates.length < 2) return 0.5; // Low confidence with little data
  
  // Base confidence on data consistency and forecast distance
  const yearRange = Math.max(...rates.map(r => r.year)) - Math.min(...rates.map(r => r.year));
  const rateVariability = calculateVariability(rates.map(r => r.levyRate));
  const forecastDistance = forecastYear - Math.max(...rates.map(r => r.year));
  
  // More data points, longer history, and less variability increase confidence
  let confidence = 0.8 - (rateVariability * 0.5) - (forecastDistance * 0.05);
  
  // Adjust based on method
  if (method === 'linear' && yearRange > 3) {
    confidence += 0.1; // Linear regression works better with more years
  } else if (method === 'weighted') {
    confidence += 0.05; // Weighted tends to be more reliable
  }
  
  // Ensure confidence is between 0 and 1
  return Math.max(0, Math.min(1, confidence));
}

/**
 * Calculate variability (coefficient of variation)
 */
function calculateVariability(values: number[]): number {
  if (values.length < 2) return 0;
  
  const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
  if (mean === 0) return 1; // Avoid division by zero
  
  const sumSquaredDiff = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0);
  const stdDev = Math.sqrt(sumSquaredDiff / values.length);
  
  return stdDev / mean; // Coefficient of variation
}

export default router;