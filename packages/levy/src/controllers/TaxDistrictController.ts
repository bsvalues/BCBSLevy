/**
 * Tax District Controller
 * 
 * Extends the BaseController to provide specialized functionality for tax districts.
 */

import { Request, Response } from 'express';
import { BaseController } from './BaseController';
import { db } from '../../../shared/db';
import { 
  taxDistricts, 
  taxCodes,
  taxCodeToTaxDistrict,
  levies
} from '../../../shared/schema';
import { eq, and, like, ilike, desc, asc } from 'drizzle-orm';
import { handleError, NotFoundError } from '../utils/handleError';
import { createResponseFormatter } from '../utils/formatResponse';

/**
 * Controller for tax district-related operations
 */
export class TaxDistrictController extends BaseController {
  /**
   * Create a new TaxDistrictController
   */
  constructor() {
    super({
      tableName: 'taxDistricts',
      primaryKey: 'id'
    });
  }
  
  /**
   * Get tax codes associated with a tax district
   */
  getTaxCodes = async (req: Request, res: Response) => {
    try {
      const taxDistrictId = parseInt(req.params.id);
      
      // Verify tax district exists
      const taxDistrict = await db.query.taxDistricts.findFirst({
        where: eq(taxDistricts.id, taxDistrictId)
      });
      
      if (!taxDistrict) {
        throw new NotFoundError('Tax district not found');
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
        const formatter = createResponseFormatter(res);
        return formatter.success([], 'No tax codes associated with this tax district');
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
      
      const formatter = createResponseFormatter(res);
      return formatter.success(result, 'Tax codes retrieved successfully');
      
    } catch (error) {
      return handleError(error, res, 'TaxDistrict:getTaxCodes');
    }
  };
  
  /**
   * Get levies associated with a tax district
   */
  getLevies = async (req: Request, res: Response) => {
    try {
      const taxDistrictId = parseInt(req.params.id);
      
      // Verify tax district exists
      const taxDistrict = await db.query.taxDistricts.findFirst({
        where: eq(taxDistricts.id, taxDistrictId)
      });
      
      if (!taxDistrict) {
        throw new NotFoundError('Tax district not found');
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
      
      const formatter = createResponseFormatter(res);
      return formatter.success(districtLevies, 'Levies retrieved successfully');
      
    } catch (error) {
      return handleError(error, res, 'TaxDistrict:getLevies');
    }
  };
  
  /**
   * Get a list of district types
   */
  getDistrictTypes = async (req: Request, res: Response) => {
    try {
      // Get unique district types
      const districtTypes = await db.selectDistinct({
        districtType: taxDistricts.districtType
      })
      .from(taxDistricts)
      .where(eq(taxDistricts.isActive, true));
      
      // Extract district types
      const types = districtTypes.map(type => type.districtType).filter(Boolean);
      
      const formatter = createResponseFormatter(res);
      return formatter.success(types, 'District types retrieved successfully');
      
    } catch (error) {
      return handleError(error, res, 'TaxDistrict:getDistrictTypes');
    }
  };
  
  /**
   * Get statistics for a tax district
   */
  getStatistics = async (req: Request, res: Response) => {
    try {
      const taxDistrictId = parseInt(req.params.id);
      
      // Verify tax district exists
      const taxDistrict = await db.query.taxDistricts.findFirst({
        where: eq(taxDistricts.id, taxDistrictId)
      });
      
      if (!taxDistrict) {
        throw new NotFoundError('Tax district not found');
      }
      
      // Get levy statistics
      const levyCount = await db.select({ count: db.fn.count() })
        .from(levies)
        .where(eq(levies.taxDistrictId, taxDistrictId));
      
      // Get tax code statistics
      const taxCodeCount = await db.select({ count: db.fn.count() })
        .from(taxCodeToTaxDistrict)
        .where(eq(taxCodeToTaxDistrict.taxDistrictId, taxDistrictId));
      
      // Get last 5 years of levies for trend analysis
      const currentYear = new Date().getFullYear();
      const recentLevies = await db.query.levies.findMany({
        where: db.and(
          eq(levies.taxDistrictId, taxDistrictId),
          db.gte(levies.taxYear, currentYear - 5)
        ),
        orderBy: desc(levies.taxYear)
      });
      
      // Calculate year-over-year growth rates
      const levyByYear = recentLevies.reduce((acc, levy) => {
        if (!acc[levy.taxYear]) {
          acc[levy.taxYear] = 0;
        }
        acc[levy.taxYear] += levy.levyAmount || 0;
        return acc;
      }, {} as Record<number, number>);
      
      const years = Object.keys(levyByYear).map(Number).sort((a, b) => b - a);
      const growthRates = years.slice(1).map((year, index) => {
        const previousYear = years[index];
        const currentYearAmount = levyByYear[year];
        const previousYearAmount = levyByYear[previousYear];
        
        if (previousYearAmount === 0) return 0;
        
        return (currentYearAmount - previousYearAmount) / previousYearAmount * 100;
      });
      
      const statistics = {
        levyCount: Number(levyCount[0].count),
        taxCodeCount: Number(taxCodeCount[0].count),
        recentYears: years,
        yearlyLevyAmounts: years.map(year => ({
          year,
          amount: levyByYear[year]
        })),
        growthRates: growthRates.map((rate, index) => ({
          year: years[index + 1],
          rate
        })),
        averageGrowthRate: growthRates.length > 0 
          ? growthRates.reduce((a, b) => a + b, 0) / growthRates.length 
          : 0
      };
      
      const formatter = createResponseFormatter(res);
      return formatter.success(statistics, 'Tax district statistics retrieved successfully');
      
    } catch (error) {
      return handleError(error, res, 'TaxDistrict:getStatistics');
    }
  };
}

export default TaxDistrictController;