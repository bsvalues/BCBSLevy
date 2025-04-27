import express, { Request, Response, Router } from 'express';
import { eq, and, gte, lte, desc, sql, asc } from 'drizzle-orm';
import multer from 'multer';
import path from 'path';
import fs from 'fs';
import { db } from '../index';
import { 
  importLogs,
  exportLogs,
  properties,
  taxDistricts
} from '@terrafusion/shared';

// Configure multer storage for file uploads
const storage = multer.diskStorage({
  destination: function(req, file, cb) {
    const uploadDir = path.join(__dirname, '../../../uploads');
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: function(req, file, cb) {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({ 
  storage: storage,
  limits: {
    fileSize: 50 * 1024 * 1024, // 50MB max file size
  },
  fileFilter: function(req, file, cb) {
    // Accept only Excel files and CSV
    const filetypes = /xlsx|xls|csv/;
    const extname = filetypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = filetypes.test(file.mimetype);
    
    if (extname && mimetype) {
      return cb(null, true);
    } else {
      cb(new Error('Only Excel and CSV files are allowed'));
    }
  }
});

// Create router
const router = Router();

/**
 * Get import logs 
 */
router.get('/import-logs', async (req: Request, res: Response) => {
  try {
    const { limit = 20, offset = 0, year } = req.query;
    
    let query = db.select()
      .from(importLogs)
      .orderBy(desc(importLogs.createdAt))
      .limit(parseInt(limit as string))
      .offset(parseInt(offset as string));
      
    if (year) {
      query = query.where(eq(importLogs.year, parseInt(year as string)));
    }
    
    const logs = await query;
    
    // Get total count for pagination
    const totalCount = await db.select({
      count: sql`COUNT(*)`
    })
    .from(importLogs)
    .where(year ? eq(importLogs.year, parseInt(year as string)) : undefined);
    
    return res.json({
      success: true,
      logs,
      pagination: {
        total: totalCount[0]?.count || 0,
        limit: parseInt(limit as string),
        offset: parseInt(offset as string)
      }
    });
  } catch (error) {
    console.error('Error fetching import logs:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch import logs'
    });
  }
});

/**
 * Get export logs
 */
router.get('/export-logs', async (req: Request, res: Response) => {
  try {
    const { limit = 20, offset = 0, year } = req.query;
    
    let query = db.select()
      .from(exportLogs)
      .orderBy(desc(exportLogs.createdAt))
      .limit(parseInt(limit as string))
      .offset(parseInt(offset as string));
      
    if (year) {
      query = query.where(eq(exportLogs.year, parseInt(year as string)));
    }
    
    const logs = await query;
    
    // Get total count for pagination
    const totalCount = await db.select({
      count: sql`COUNT(*)`
    })
    .from(exportLogs)
    .where(year ? eq(exportLogs.year, parseInt(year as string)) : undefined);
    
    return res.json({
      success: true,
      logs,
      pagination: {
        total: totalCount[0]?.count || 0,
        limit: parseInt(limit as string),
        offset: parseInt(offset as string)
      }
    });
  } catch (error) {
    console.error('Error fetching export logs:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch export logs'
    });
  }
});

/**
 * Get property summary for a tax district
 */
router.get('/property-summary/:districtId', async (req: Request, res: Response) => {
  try {
    const { districtId } = req.params;
    
    // Get district to verify it exists
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
    
    // Get properties in this district
    const propertyList = await db.select()
      .from(properties)
      .where(eq(properties.taxDistrictId, parseInt(districtId)))
      .limit(1000); // Limit to prevent excessive data
    
    // Calculate summary statistics
    const totalAssessedValue = propertyList.reduce((sum, property) => 
      sum + (property.assessedValue || 0), 0);
      
    const avgAssessedValue = propertyList.length ? 
      totalAssessedValue / propertyList.length : 0;
    
    const propertyTypes = new Map();
    propertyList.forEach(property => {
      const type = property.propertyType || 'Unknown';
      propertyTypes.set(type, (propertyTypes.get(type) || 0) + 1);
    });
    
    const typeDistribution = Array.from(propertyTypes.entries()).map(([type, count]) => ({
      type,
      count,
      percentage: parseFloat(((count as number / propertyList.length) * 100).toFixed(2))
    }));
    
    return res.json({
      success: true,
      districtId: parseInt(districtId),
      propertyCount: propertyList.length,
      totalAssessedValue,
      avgAssessedValue,
      typeDistribution,
      recentProperties: propertyList
        .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
        .slice(0, 10)
    });
  } catch (error) {
    console.error(`Error fetching property summary for district ${req.params.districtId}:`, error);
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch property summary'
    });
  }
});

/**
 * Upload property data file
 */
router.post('/upload/properties', upload.single('file'), async (req: Request, res: Response) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        message: 'No file uploaded'
      });
    }
    
    const { taxDistrictId, year, userId } = req.body;
    
    // Validate required fields
    if (!taxDistrictId || !year || !userId) {
      return res.status(400).json({
        success: false,
        message: 'Missing required parameters'
      });
    }
    
    // Insert an import log entry
    const importLog = await db.insert(importLogs).values({
      taxDistrictId: parseInt(taxDistrictId),
      year: parseInt(year),
      userId: parseInt(userId),
      fileName: req.file.filename,
      fileSize: req.file.size,
      importType: 'PROPERTY',
      status: 'PENDING',
      createdAt: new Date(),
      updatedAt: new Date()
    }).returning();
    
    // In a real implementation, this would trigger a background job to process the file
    // For now, we'll just return success and the import log entry
    
    return res.json({
      success: true,
      message: 'File uploaded successfully. Processing will begin shortly.',
      importLog: importLog[0],
      file: {
        originalName: req.file.originalname,
        storedName: req.file.filename,
        size: req.file.size,
        path: req.file.path
      }
    });
  } catch (error) {
    console.error('Error uploading property data:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to upload property data'
    });
  }
});

/**
 * Export tax district data
 */
router.post('/export/tax-district/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { format = 'json', includeProperties = false, userId } = req.body;
    
    // Validate required fields
    if (!userId) {
      return res.status(400).json({
        success: false,
        message: 'User ID is required'
      });
    }
    
    // Get tax district
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
    
    // Create export log entry
    const exportLog = await db.insert(exportLogs).values({
      taxDistrictId: parseInt(id),
      userId: parseInt(userId),
      exportType: includeProperties ? 'DISTRICT_WITH_PROPERTIES' : 'DISTRICT_ONLY',
      format: format.toUpperCase(),
      status: 'COMPLETED',
      createdAt: new Date(),
      updatedAt: new Date()
    }).returning();
    
    // If properties are requested, fetch them
    let districtData: any = district[0];
    
    if (includeProperties) {
      const propertyList = await db.select()
        .from(properties)
        .where(eq(properties.taxDistrictId, parseInt(id)))
        .limit(5000);
        
      districtData = {
        ...districtData,
        properties: propertyList
      };
    }
    
    // Handle different export formats
    if (format.toLowerCase() === 'csv') {
      // In a real implementation, this would convert to CSV
      // For now, we'll just return JSON with a note
      return res.json({
        success: true,
        message: 'Data exported successfully (CSV conversion would happen in production)',
        exportLog: exportLog[0],
        data: districtData
      });
    } else {
      // JSON format
      return res.json({
        success: true,
        exportLog: exportLog[0],
        data: districtData
      });
    }
  } catch (error) {
    console.error(`Error exporting tax district ${req.params.id}:`, error);
    return res.status(500).json({
      success: false,
      message: 'Failed to export tax district data'
    });
  }
});

export default router;