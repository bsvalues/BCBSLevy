import express, { Request, Response, Router } from 'express';
import { eq, and, gte, lte, desc, sql, asc } from 'drizzle-orm';
import { db } from '../index';
import { 
  taxCodes,
  taxCodeHistoricalRates,
  taxDistricts,
  properties
} from '@terrafusion/shared';

// Create router
const router = Router();

/**
 * Get historical rate trends for a tax district
 */
router.get('/district-trends/:districtId', async (req: Request, res: Response) => {
  try {
    const { districtId } = req.params;
    const { startYear, endYear } = req.query;
    
    // Get tax district to verify it exists
    const district = await db.select()
      .from(taxDistricts)
      .where(eq(taxDistricts.id, parseInt(districtId)))
      .limit(1);
      
    if (!district.length) {
      return res.status(404).json({
        success: false,
        message: 'Tax district not found'
      });
    }
    
    // Get all tax codes for this district
    const codes = await db.select()
      .from(taxCodes)
      .where(eq(taxCodes.taxDistrictId, parseInt(districtId)));
      
    if (!codes.length) {
      return res.status(404).json({
        success: false,
        message: 'No tax codes found for this district'
      });
    }
    
    // Build array of tax code IDs
    const taxCodeIds = codes.map(code => code.id);
    
    // Get historical rates for these tax codes
    let query = db.select()
      .from(taxCodeHistoricalRates)
      .where(sql`${taxCodeHistoricalRates.taxCodeId} IN (${taxCodeIds.join(',')})`);
      
    // Apply year filters if provided
    if (startYear) {
      query = query.where(gte(taxCodeHistoricalRates.year, parseInt(startYear as string)));
    }
    
    if (endYear) {
      query = query.where(lte(taxCodeHistoricalRates.year, parseInt(endYear as string)));
    }
    
    // Execute query
    const rates = await query.orderBy(asc(taxCodeHistoricalRates.year));
    
    // Group rates by year for trend analysis
    const ratesByYear: {[key: number]: any} = {};
    
    rates.forEach(rate => {
      if (!ratesByYear[rate.year]) {
        ratesByYear[rate.year] = {
          year: rate.year,
          rates: [],
          avgRate: 0,
          totalAssessedValue: 0,
          totalLevyAmount: 0
        };
      }
      
      ratesByYear[rate.year].rates.push(rate);
      ratesByYear[rate.year].totalAssessedValue += rate.totalAssessedValue || 0;
      ratesByYear[rate.year].totalLevyAmount += rate.levyAmount || 0;
    });
    
    // Calculate average rates for each year
    Object.keys(ratesByYear).forEach(year => {
      const yearData = ratesByYear[parseInt(year)];
      if (yearData.rates.length > 0) {
        yearData.avgRate = yearData.rates.reduce((sum: number, rate: any) => sum + rate.levyRate, 0) / yearData.rates.length;
        yearData.avgRate = parseFloat(yearData.avgRate.toFixed(4));
      }
    });
    
    // Convert to array and sort by year
    const trendData = Object.values(ratesByYear).sort((a: any, b: any) => a.year - b.year);
    
    // Calculate year-over-year changes
    const trendsWithChanges = trendData.map((yearData: any, index: number) => {
      if (index === 0) {
        return {
          ...yearData,
          rateChangePercent: 0,
          assessedValueChangePercent: 0,
          levyAmountChangePercent: 0
        };
      }
      
      const prevYear = trendData[index - 1];
      
      const rateChangePercent = prevYear.avgRate ? 
        ((yearData.avgRate - prevYear.avgRate) / prevYear.avgRate) * 100 : 0;
        
      const assessedValueChangePercent = prevYear.totalAssessedValue ? 
        ((yearData.totalAssessedValue - prevYear.totalAssessedValue) / prevYear.totalAssessedValue) * 100 : 0;
        
      const levyAmountChangePercent = prevYear.totalLevyAmount ? 
        ((yearData.totalLevyAmount - prevYear.totalLevyAmount) / prevYear.totalLevyAmount) * 100 : 0;
      
      return {
        ...yearData,
        rateChangePercent: parseFloat(rateChangePercent.toFixed(2)),
        assessedValueChangePercent: parseFloat(assessedValueChangePercent.toFixed(2)),
        levyAmountChangePercent: parseFloat(levyAmountChangePercent.toFixed(2))
      };
    });
    
    return res.json({
      success: true,
      districtId: parseInt(districtId),
      districtName: district[0].name,
      trends: trendsWithChanges,
      taxCodeCount: codes.length,
      yearsAnalyzed: trendsWithChanges.length,
      summary: {
        avgAnnualRateChange: calculateAverageChange(trendsWithChanges.map((t: any) => t.rateChangePercent)),
        avgAnnualAssessedValueChange: calculateAverageChange(trendsWithChanges.map((t: any) => t.assessedValueChangePercent)),
        avgAnnualLevyAmountChange: calculateAverageChange(trendsWithChanges.map((t: any) => t.levyAmountChangePercent)),
        volatility: calculateVolatility(trendsWithChanges.map((t: any) => t.avgRate))
      }
    });
  } catch (error) {
    console.error(`Error fetching historical trends for district ${req.params.districtId}:`, error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch historical trends'
    });
  }
});

/**
 * Compare multiple tax districts
 */
router.post('/compare-districts', async (req: Request, res: Response) => {
  try {
    const { districtIds, startYear, endYear } = req.body;
    
    // Validate input
    if (!districtIds || !Array.isArray(districtIds) || districtIds.length === 0) {
      return res.status(400).json({
        success: false,
        message: 'District IDs array is required'
      });
    }
    
    // Get districts to verify they exist
    const districts = await db.select()
      .from(taxDistricts)
      .where(sql`${taxDistricts.id} IN (${districtIds.join(',')})`);
      
    if (districts.length !== districtIds.length) {
      return res.status(404).json({
        success: false,
        message: 'One or more districts not found'
      });
    }
    
    // Process each district
    const districtPromises = districts.map(async district => {
      // Get all tax codes for this district
      const codes = await db.select()
        .from(taxCodes)
        .where(eq(taxCodes.taxDistrictId, district.id));
        
      if (!codes.length) {
        return {
          districtId: district.id,
          districtName: district.name,
          rateData: [],
          summary: null
        };
      }
      
      // Build array of tax code IDs
      const taxCodeIds = codes.map(code => code.id);
      
      // Get historical rates for these tax codes
      let query = db.select()
        .from(taxCodeHistoricalRates)
        .where(sql`${taxCodeHistoricalRates.taxCodeId} IN (${taxCodeIds.join(',')})`);
        
      // Apply year filters if provided
      if (startYear) {
        query = query.where(gte(taxCodeHistoricalRates.year, startYear));
      }
      
      if (endYear) {
        query = query.where(lte(taxCodeHistoricalRates.year, endYear));
      }
      
      // Execute query
      const rates = await query.orderBy(asc(taxCodeHistoricalRates.year));
      
      // Group rates by year
      const ratesByYear: {[key: number]: any} = {};
      
      rates.forEach(rate => {
        if (!ratesByYear[rate.year]) {
          ratesByYear[rate.year] = {
            year: rate.year,
            avgRate: 0,
            totalAssessedValue: 0,
            totalLevyAmount: 0,
            rateCount: 0
          };
        }
        
        ratesByYear[rate.year].totalAssessedValue += rate.totalAssessedValue || 0;
        ratesByYear[rate.year].totalLevyAmount += rate.levyAmount || 0;
        ratesByYear[rate.year].avgRate += rate.levyRate;
        ratesByYear[rate.year].rateCount += 1;
      });
      
      // Calculate averages
      Object.keys(ratesByYear).forEach(year => {
        const yearData = ratesByYear[parseInt(year)];
        if (yearData.rateCount > 0) {
          yearData.avgRate = yearData.avgRate / yearData.rateCount;
          yearData.avgRate = parseFloat(yearData.avgRate.toFixed(4));
        }
      });
      
      // Convert to array and sort by year
      const rateData = Object.values(ratesByYear).sort((a: any, b: any) => a.year - b.year);
      
      // Calculate summary stats
      const avgRates = rateData.map((d: any) => d.avgRate);
      const summary = {
        avgRate: calculateAverage(avgRates),
        minRate: Math.min(...avgRates),
        maxRate: Math.max(...avgRates),
        volatility: calculateVolatility(avgRates)
      };
      
      return {
        districtId: district.id,
        districtName: district.name,
        rateData,
        summary
      };
    });
    
    // Wait for all district data to be processed
    const districtResults = await Promise.all(districtPromises);
    
    return res.json({
      success: true,
      districts: districtResults,
      comparisonMetrics: generateComparisonMetrics(districtResults)
    });
  } catch (error) {
    console.error('Error comparing districts:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to compare districts'
    });
  }
});

/**
 * Get property value trends
 */
router.get('/property-value-trends/:districtId', async (req: Request, res: Response) => {
  try {
    const { districtId } = req.params;
    const { startYear, endYear, propertyType } = req.query;
    
    // Get tax district to verify it exists
    const district = await db.select()
      .from(taxDistricts)
      .where(eq(taxDistricts.id, parseInt(districtId)))
      .limit(1);
      
    if (!district.length) {
      return res.status(404).json({
        success: false,
        message: 'Tax district not found'
      });
    }
    
    // Build query for properties
    let query = db.select()
      .from(properties)
      .where(eq(properties.taxDistrictId, parseInt(districtId)));
      
    // Apply property type filter if provided
    if (propertyType) {
      query = query.where(eq(properties.propertyType, propertyType as string));
    }
    
    // Execute query
    const propertiesData = await query;
    
    if (!propertiesData.length) {
      return res.status(404).json({
        success: false,
        message: 'No properties found for this district'
      });
    }
    
    // Group properties by year
    const propertiesByYear: {[key: number]: any} = {};
    
    propertiesData.forEach(property => {
      const year = new Date(property.assessmentDate).getFullYear();
      
      // Apply year filters
      if ((startYear && year < parseInt(startYear as string)) || 
          (endYear && year > parseInt(endYear as string))) {
        return;
      }
      
      if (!propertiesByYear[year]) {
        propertiesByYear[year] = {
          year,
          propertyCount: 0,
          totalValue: 0,
          avgValue: 0,
          propertyTypes: {}
        };
      }
      
      propertiesByYear[year].propertyCount += 1;
      propertiesByYear[year].totalValue += property.assessedValue || 0;
      
      // Track counts by property type
      const type = property.propertyType || 'Unknown';
      if (!propertiesByYear[year].propertyTypes[type]) {
        propertiesByYear[year].propertyTypes[type] = 0;
      }
      propertiesByYear[year].propertyTypes[type] += 1;
    });
    
    // Calculate averages and format property types
    Object.keys(propertiesByYear).forEach(year => {
      const yearData = propertiesByYear[parseInt(year)];
      if (yearData.propertyCount > 0) {
        yearData.avgValue = yearData.totalValue / yearData.propertyCount;
      }
      
      // Convert property types to array
      const typeArray = Object.entries(yearData.propertyTypes).map(([type, count]) => ({
        type,
        count,
        percentage: parseFloat(((count as number / yearData.propertyCount) * 100).toFixed(2))
      }));
      
      yearData.propertyTypes = typeArray;
    });
    
    // Convert to array and sort by year
    const valueData = Object.values(propertiesByYear).sort((a: any, b: any) => a.year - b.year);
    
    // Calculate year-over-year changes
    const valueDataWithChanges = valueData.map((yearData: any, index: number) => {
      if (index === 0) {
        return {
          ...yearData,
          avgValueChangePercent: 0,
          totalValueChangePercent: 0
        };
      }
      
      const prevYear = valueData[index - 1];
      
      const avgValueChangePercent = prevYear.avgValue ? 
        ((yearData.avgValue - prevYear.avgValue) / prevYear.avgValue) * 100 : 0;
        
      const totalValueChangePercent = prevYear.totalValue ? 
        ((yearData.totalValue - prevYear.totalValue) / prevYear.totalValue) * 100 : 0;
      
      return {
        ...yearData,
        avgValueChangePercent: parseFloat(avgValueChangePercent.toFixed(2)),
        totalValueChangePercent: parseFloat(totalValueChangePercent.toFixed(2))
      };
    });
    
    return res.json({
      success: true,
      districtId: parseInt(districtId),
      districtName: district[0].name,
      propertyType: propertyType || 'All',
      trends: valueDataWithChanges,
      summary: {
        totalProperties: propertiesData.length,
        yearsAnalyzed: valueDataWithChanges.length,
        avgAnnualValueChange: calculateAverageChange(valueDataWithChanges.map((d: any) => d.avgValueChangePercent)),
        avgAnnualTotalValueChange: calculateAverageChange(valueDataWithChanges.map((d: any) => d.totalValueChangePercent)),
        volatility: calculateVolatility(valueDataWithChanges.map((d: any) => d.avgValue))
      }
    });
  } catch (error) {
    console.error(`Error fetching property value trends for district ${req.params.districtId}:`, error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch property value trends'
    });
  }
});

/**
 * Calculate average of an array of numbers
 */
function calculateAverage(values: number[]): number {
  if (values.length === 0) return 0;
  return parseFloat((values.reduce((sum, val) => sum + val, 0) / values.length).toFixed(4));
}

/**
 * Calculate average of percentage changes, skipping the first value (which is usually 0)
 */
function calculateAverageChange(changes: number[]): number {
  if (changes.length <= 1) return 0;
  const validChanges = changes.slice(1);
  return parseFloat((validChanges.reduce((sum, val) => sum + val, 0) / validChanges.length).toFixed(2));
}

/**
 * Calculate volatility from a series of values
 */
function calculateVolatility(values: number[]): number {
  if (values.length < 2) return 0;
  
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
  return parseFloat(Math.sqrt(variance).toFixed(4));
}

/**
 * Generate comparison metrics between districts
 */
function generateComparisonMetrics(districtResults: any[]): any {
  // Get districts with data
  const districtsWithData = districtResults.filter(d => d.rateData.length > 0);
  
  if (districtsWithData.length < 2) {
    return { 
      insufficientData: true,
      message: 'At least two districts with data are required for comparison'
    };
  }
  
  // Find common years across all districts
  const yearSets = districtsWithData.map(district => 
    new Set(district.rateData.map((r: any) => r.year))
  );
  
  // Intersection of all years
  const commonYears = [...yearSets[0]].filter(year => 
    yearSets.every(yearSet => yearSet.has(year))
  ).sort();
  
  if (commonYears.length === 0) {
    return {
      insufficientData: true,
      message: 'No common years found across districts for comparison'
    };
  }
  
  // Calculate correlation matrix
  const correlationMatrix: any = {};
  
  districtsWithData.forEach((district1, i) => {
    correlationMatrix[district1.districtId] = {};
    
    districtsWithData.forEach((district2, j) => {
      if (i === j) {
        correlationMatrix[district1.districtId][district2.districtId] = 1;
        return;
      }
      
      // Get rate data for common years
      const rates1: number[] = [];
      const rates2: number[] = [];
      
      commonYears.forEach(year => {
        const rate1Entry = district1.rateData.find((r: any) => r.year === year);
        const rate2Entry = district2.rateData.find((r: any) => r.year === year);
        
        if (rate1Entry && rate2Entry) {
          rates1.push(rate1Entry.avgRate);
          rates2.push(rate2Entry.avgRate);
        }
      });
      
      // Calculate correlation
      correlationMatrix[district1.districtId][district2.districtId] = 
        calculateCorrelation(rates1, rates2);
    });
  });
  
  // Calculate ranking by average rate
  const districtRankings = districtsWithData.map(district => ({
    districtId: district.districtId,
    districtName: district.districtName,
    avgRate: district.summary.avgRate,
    volatility: district.summary.volatility
  })).sort((a, b) => a.avgRate - b.avgRate);
  
  return {
    commonYearsAnalyzed: commonYears,
    correlationMatrix,
    rankings: districtRankings,
    volatilityComparison: districtRankings.sort((a, b) => a.volatility - b.volatility)
  };
}

/**
 * Calculate Pearson correlation coefficient between two arrays
 */
function calculateCorrelation(x: number[], y: number[]): number {
  if (x.length !== y.length || x.length < 2) return 0;
  
  const n = x.length;
  const xMean = x.reduce((a, b) => a + b, 0) / n;
  const yMean = y.reduce((a, b) => a + b, 0) / n;
  
  let numerator = 0;
  let xDenominator = 0;
  let yDenominator = 0;
  
  for (let i = 0; i < n; i++) {
    const xDiff = x[i] - xMean;
    const yDiff = y[i] - yMean;
    
    numerator += xDiff * yDiff;
    xDenominator += xDiff * xDiff;
    yDenominator += yDiff * yDiff;
  }
  
  const denominator = Math.sqrt(xDenominator * yDenominator);
  
  return denominator === 0 ? 0 : parseFloat((numerator / denominator).toFixed(4));
}

export default router;