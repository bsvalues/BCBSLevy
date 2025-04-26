import { Router, Request, Response } from 'express';
import { desc, eq, and, gte, lte } from 'drizzle-orm';
import { db } from '../index';
import { 
  importLogs,
  exportLogs,
  importTypeEnum,
  exportTypeEnum
} from '@terrafusion/shared';
import multer from 'multer';
import path from 'path';
import fs from 'fs';

const router = Router();

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: function(req, file, cb) {
    const uploadDir = path.join(process.cwd(), 'uploads');
    // Create the directory if it doesn't exist
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: function(req, file, cb) {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({ 
  storage: storage,
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB limit
  },
  fileFilter: function(req, file, cb) {
    // Accept excel, csv, and text files
    const allowedExtensions = ['.xlsx', '.xls', '.csv', '.txt', '.json'];
    const ext = path.extname(file.originalname).toLowerCase();
    
    if (allowedExtensions.includes(ext)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only Excel, CSV, TXT, and JSON files are allowed.'));
    }
  }
});

/**
 * Get import logs
 */
router.get('/imports', async (req: Request, res: Response) => {
  try {
    const userId = parseInt(req.query.userId as string);
    const limit = parseInt(req.query.limit as string) || 50;
    const offset = parseInt(req.query.offset as string) || 0;
    const importType = req.query.importType as string;
    const startDate = req.query.startDate as string;
    const endDate = req.query.endDate as string;
    
    // Build query conditions
    let conditions = [];
    
    if (userId) {
      conditions.push(eq(importLogs.userId, userId));
    }
    
    if (importType) {
      conditions.push(eq(importLogs.importType, importType as any));
    }
    
    if (startDate) {
      conditions.push(gte(importLogs.createdAt, new Date(startDate)));
    }
    
    if (endDate) {
      conditions.push(lte(importLogs.createdAt, new Date(endDate)));
    }
    
    // Execute query
    const imports = await db.query.importLogs.findMany({
      where: conditions.length > 0 ? and(...conditions) : undefined,
      orderBy: [desc(importLogs.createdAt)],
      limit: limit,
      offset: offset
    });
    
    // Get total count for pagination
    const countResult = await db.select({ count: db.fn.count() })
      .from(importLogs)
      .where(conditions.length > 0 ? and(...conditions) : undefined);
    
    const totalCount = Number(countResult[0].count);
    
    return res.status(200).json({
      imports,
      pagination: {
        total: totalCount,
        offset,
        limit,
        hasMore: offset + imports.length < totalCount
      }
    });
  } catch (error) {
    console.error('Error fetching import logs:', error);
    return res.status(500).json({ error: 'Failed to fetch import logs' });
  }
});

/**
 * Get export logs
 */
router.get('/exports', async (req: Request, res: Response) => {
  try {
    const userId = parseInt(req.query.userId as string);
    const limit = parseInt(req.query.limit as string) || 50;
    const offset = parseInt(req.query.offset as string) || 0;
    const exportType = req.query.exportType as string;
    const startDate = req.query.startDate as string;
    const endDate = req.query.endDate as string;
    
    // Build query conditions
    let conditions = [];
    
    if (userId) {
      conditions.push(eq(exportLogs.userId, userId));
    }
    
    if (exportType) {
      conditions.push(eq(exportLogs.exportType, exportType as any));
    }
    
    if (startDate) {
      conditions.push(gte(exportLogs.createdAt, new Date(startDate)));
    }
    
    if (endDate) {
      conditions.push(lte(exportLogs.createdAt, new Date(endDate)));
    }
    
    // Execute query
    const exports = await db.query.exportLogs.findMany({
      where: conditions.length > 0 ? and(...conditions) : undefined,
      orderBy: [desc(exportLogs.createdAt)],
      limit: limit,
      offset: offset
    });
    
    // Get total count for pagination
    const countResult = await db.select({ count: db.fn.count() })
      .from(exportLogs)
      .where(conditions.length > 0 ? and(...conditions) : undefined);
    
    const totalCount = Number(countResult[0].count);
    
    return res.status(200).json({
      exports,
      pagination: {
        total: totalCount,
        offset,
        limit,
        hasMore: offset + exports.length < totalCount
      }
    });
  } catch (error) {
    console.error('Error fetching export logs:', error);
    return res.status(500).json({ error: 'Failed to fetch export logs' });
  }
});

/**
 * Upload file for import
 */
router.post('/import', upload.single('file'), async (req: Request, res: Response) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }
    
    const { 
      userId, 
      importType, 
      year = new Date().getFullYear() 
    } = req.body;
    
    if (!userId || !importType) {
      return res.status(400).json({ error: 'Missing required fields: userId, importType' });
    }
    
    // Create import log entry
    const [importLog] = await db.insert(importLogs).values({
      userId: parseInt(userId),
      filename: req.file.originalname,
      importType: importType as any,
      status: 'PENDING',
      year: parseInt(year),
      createdById: parseInt(userId),
      updatedById: parseInt(userId),
      importMetadata: {
        fileSize: req.file.size,
        mimetype: req.file.mimetype,
        storedFilename: req.file.filename,
        storedPath: req.file.path
      }
    }).returning();
    
    // In a real implementation, we would start a background job to process the file
    // For now, we'll just return the import log entry with the PENDING status
    
    return res.status(201).json({ 
      importId: importLog.id,
      filename: req.file.originalname,
      status: 'PENDING',
      message: 'File uploaded successfully. Processing will begin shortly.'
    });
  } catch (error) {
    console.error('Error uploading file:', error);
    return res.status(500).json({ error: 'Failed to upload file' });
  }
});

/**
 * Generate export
 */
router.post('/export', async (req: Request, res: Response) => {
  try {
    const { 
      userId, 
      exportType, 
      parameters = {},
      year = new Date().getFullYear(),
      filename = `export-${Date.now()}.csv`
    } = req.body;
    
    if (!userId || !exportType) {
      return res.status(400).json({ error: 'Missing required fields: userId, exportType' });
    }
    
    // Create export log entry
    const [exportLog] = await db.insert(exportLogs).values({
      userId: parseInt(userId),
      filename,
      exportType: exportType as any,
      status: 'PENDING',
      year: parseInt(year),
      exportMetadata: parameters,
      createdById: parseInt(userId),
      updatedById: parseInt(userId)
    }).returning();
    
    // In a real implementation, we would start a background job to generate the export
    // For now, we'll just return the export log entry with the PENDING status
    
    return res.status(201).json({ 
      exportId: exportLog.id,
      filename,
      status: 'PENDING',
      message: 'Export request received. Processing will begin shortly.'
    });
  } catch (error) {
    console.error('Error creating export:', error);
    return res.status(500).json({ error: 'Failed to create export' });
  }
});

/**
 * Get import/export types
 */
router.get('/types', async (req: Request, res: Response) => {
  try {
    // Get enum values directly from the schema
    return res.status(200).json({
      importTypes: Object.values(importTypeEnum.enumValues),
      exportTypes: Object.values(exportTypeEnum.enumValues)
    });
  } catch (error) {
    console.error('Error fetching types:', error);
    return res.status(500).json({ error: 'Failed to fetch import/export types' });
  }
});

export default router;